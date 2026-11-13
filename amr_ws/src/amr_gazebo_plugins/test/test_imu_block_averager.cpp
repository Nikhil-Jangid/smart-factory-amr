// TEST-M3-13: unit tests of the DEC-038 IMU block averager (docs/testing/test_plan.md §7.3).
// Raw period 1 ms, block 10 (the DEC-038 values) unless stated. Sample k has stamp k ms.
#include <gtest/gtest.h>

#include <cmath>
#include <cstdint>
#include <random>
#include <vector>

#include "amr_gazebo_plugins/imu_block_averager.hpp"

using amr_gazebo_plugins::ImuBlockAverager;
using amr_gazebo_plugins::ImuDecimationConfig;
using amr_gazebo_plugins::ImuSample;
using amr_gazebo_plugins::ValidateConfig;
using amr_gazebo_plugins::ValidateControllerRate;

namespace
{
constexpr int64_t kMs = 1000000;  // ns

ImuSample Sample(int64_t k, double v)
{
  ImuSample s;
  s.stamp_ns = k * kMs;
  s.linear_acceleration = {{v, 2.0 * v, 9.8 + v}};
  s.angular_velocity = {{-v, 0.5 * v, 0.1 * v}};
  return s;
}

// Feeds samples k = first..last (value = k unless overridden) and returns the stamps (ms) of the outputs.
std::vector<int64_t> Feed(ImuBlockAverager & a, int64_t first, int64_t last, std::vector<ImuSample> * outs = nullptr)
{
  std::vector<int64_t> stamps;
  for (int64_t k = first; k <= last; ++k) {
    ImuSample out;
    if (a.Add(Sample(k, static_cast<double>(k)), &out)) {
      stamps.push_back(out.stamp_ns / kMs);
      if (outs) {
        outs->push_back(out);
      }
    }
  }
  return stamps;
}
}  // namespace

// (a) A complete block gives the exact per-axis mean and the newest sample's stamp.
TEST(ImuBlockAverager, FullBlockExactMeanAndNewestStamp)
{
  ImuBlockAverager a(10, kMs);
  std::vector<ImuSample> outs;
  EXPECT_EQ(Feed(a, 1, 10, &outs), (std::vector<int64_t>{10}));
  ASSERT_EQ(outs.size(), 1u);
  const double m = 5.5;  // mean of 1..10
  EXPECT_NEAR(outs[0].linear_acceleration[0], m, 1e-12);
  EXPECT_NEAR(outs[0].linear_acceleration[1], 2.0 * m, 1e-12);
  EXPECT_NEAR(outs[0].linear_acceleration[2], 9.8 + m, 1e-12);
  EXPECT_NEAR(outs[0].angular_velocity[0], -m, 1e-12);
  EXPECT_NEAR(outs[0].angular_velocity[1], 0.5 * m, 1e-12);
  EXPECT_NEAR(outs[0].angular_velocity[2], 0.1 * m, 1e-12);
  EXPECT_EQ(outs[0].stamp_ns, 10 * kMs);
  EXPECT_EQ(a.counters().published, 1u);
  EXPECT_EQ(a.counters().discarded_partial, 0u);
}

// (a) Long random run: every output equals the naive mean of its 10 samples (1e-12); blocks never overlap.
TEST(ImuBlockAverager, RandomStreamMatchesNaiveMean)
{
  std::mt19937 gen(38);
  std::normal_distribution<double> noise(0.0, 0.0316);
  ImuBlockAverager a(10, kMs);
  std::vector<ImuSample> in;
  int outputs = 0;
  for (int64_t k = 1; k <= 10000; ++k) {
    ImuSample s;
    s.stamp_ns = k * kMs;
    for (int i = 0; i < 3; ++i) {
      s.linear_acceleration[i] = noise(gen) + (k % 10 == 3 ? 5.0 : 0.0);
      s.angular_velocity[i] = noise(gen);
    }
    in.push_back(s);
    ImuSample out;
    if (a.Add(s, &out)) {
      ++outputs;
      ASSERT_EQ(out.stamp_ns % (10 * kMs), 0);
      for (int i = 0; i < 3; ++i) {
        double sa = 0.0, sg = 0.0;
        for (size_t j = in.size() - 10; j < in.size(); ++j) {
          sa += in[j].linear_acceleration[i];
          sg += in[j].angular_velocity[i];
        }
        EXPECT_NEAR(out.linear_acceleration[i], sa / 10.0, 1e-12);
        EXPECT_NEAR(out.angular_velocity[i], sg / 10.0, 1e-12);
      }
    }
  }
  EXPECT_EQ(outputs, 1000);
  EXPECT_EQ(a.counters().samples, 10000u);
  EXPECT_EQ(a.counters().dropped_incomplete + a.counters().discarded_partial + a.counters().duplicates +
    a.counters().resets + a.counters().missing_samples + a.counters().off_grid, 0u);
}

// (b) Startup: nothing before the first complete aligned block; a 9-sample first block is not published.
TEST(ImuBlockAverager, StartupWaitsForCompleteAlignedBlock)
{
  ImuBlockAverager a(10, kMs);
  EXPECT_EQ(Feed(a, 2, 30), (std::vector<int64_t>{20, 30}));  // block 1..10 has only 9 samples
  EXPECT_EQ(a.counters().discarded_partial, 1u);
  EXPECT_EQ(a.counters().dropped_incomplete, 0u);

  ImuBlockAverager b(10, kMs);  // the simulation starts at t = 0: block (-10, 0] holds one sample
  EXPECT_EQ(Feed(b, 0, 20), (std::vector<int64_t>{10, 20}));
  EXPECT_EQ(b.counters().discarded_partial, 1u);
}

// (c) A missing sample drops its block (counted); the next complete block is published.
TEST(ImuBlockAverager, MissingSampleDropsBlock)
{
  ImuBlockAverager a(10, kMs);
  std::vector<int64_t> stamps = Feed(a, 1, 14);
  stamps.push_back(-1);  // separator
  for (int64_t s : Feed(a, 16, 30)) {stamps.push_back(s);}  // sample 15 missing
  EXPECT_EQ(stamps, (std::vector<int64_t>{10, -1, 30}));
  EXPECT_EQ(a.counters().dropped_incomplete, 1u);
  EXPECT_EQ(a.counters().missing_samples, 1u);

  // Missing the last sample of a block: the block is closed incomplete when the next block starts.
  ImuBlockAverager b(10, kMs);
  Feed(b, 1, 19);
  EXPECT_EQ(Feed(b, 21, 30), (std::vector<int64_t>{30}));
  EXPECT_EQ(b.counters().dropped_incomplete, 1u);

  // A gap longer than a block: one dropped block (the open one), the skipped indices counted.
  ImuBlockAverager c(10, kMs);
  Feed(c, 1, 12);
  EXPECT_EQ(Feed(c, 41, 50), (std::vector<int64_t>{50}));
  EXPECT_EQ(c.counters().dropped_incomplete, 1u);
  EXPECT_EQ(c.counters().missing_samples, 28u);
}

// (d) A duplicate stamp is ignored (its value is not used) and counted.
TEST(ImuBlockAverager, DuplicateIgnored)
{
  ImuBlockAverager a(10, kMs);
  ImuSample out;
  for (int64_t k = 1; k <= 10; ++k) {
    ASSERT_FALSE(k < 10 && a.Add(Sample(k, static_cast<double>(k)), &out));
    if (k == 5) {
      EXPECT_FALSE(a.Add(Sample(5, 1000.0), &out));  // duplicate with a different value
    }
    if (k == 10) {
      ASSERT_TRUE(a.Add(Sample(10, 10.0), &out));
    }
  }
  EXPECT_NEAR(out.linear_acceleration[0], 5.5, 1e-12);
  EXPECT_EQ(a.counters().duplicates, 1u);
  EXPECT_FALSE(a.Add(Sample(10, 10.0), &out));  // duplicate of a block-final sample: no second output
  EXPECT_EQ(a.counters().duplicates, 2u);
  EXPECT_EQ(a.counters().published, 1u);
}

// (e) Time reversal: the buffer is cleared, the event counted, and a full aligned block is required again.
TEST(ImuBlockAverager, TimeReversalResets)
{
  ImuBlockAverager a(10, kMs);
  Feed(a, 1, 25);                                              // output at 10, 20; block 21..30 open
  EXPECT_EQ(Feed(a, 3, 20), (std::vector<int64_t>{20}));      // restart at 3 ms: block 1..10 partial
  EXPECT_EQ(a.counters().resets, 1u);
  EXPECT_EQ(a.counters().discarded_partial, 2u);              // the open 21..25 block and the 3..10 block
  EXPECT_EQ(a.counters().dropped_incomplete, 0u);
  EXPECT_EQ(a.counters().published, 3u);
}

// (f) Shutdown: a partial block is discarded and never published.
TEST(ImuBlockAverager, ShutdownDiscardsPartialBlock)
{
  ImuBlockAverager a(10, kMs);
  EXPECT_EQ(Feed(a, 1, 17), (std::vector<int64_t>{10}));
  a.Finish();
  EXPECT_EQ(a.counters().published, 1u);
  EXPECT_EQ(a.counters().discarded_partial, 1u);
  a.Finish();  // idempotent
  EXPECT_EQ(a.counters().discarded_partial, 1u);
}

// Pause/resume: blocks are formed from simulation stamps, not arrival time. A pause (no samples, simulation time
// frozen) in the middle of a block does not drop it; single steps while paused continue the grid; a sample
// re-delivered across the pause is a duplicate.
TEST(ImuBlockAverager, PauseResumeContinuesBlocks)
{
  ImuBlockAverager a(10, kMs);
  EXPECT_EQ(Feed(a, 1, 14), (std::vector<int64_t>{10}));
  ImuSample out;
  EXPECT_FALSE(a.Add(Sample(14, 14.0), &out));                  // paused; last sample re-delivered
  EXPECT_EQ(Feed(a, 15, 16), (std::vector<int64_t>{}));         // two single steps while paused
  std::vector<ImuSample> outs;
  EXPECT_EQ(Feed(a, 17, 20, &outs), (std::vector<int64_t>{20}));  // resumed
  EXPECT_NEAR(outs[0].linear_acceleration[0], 15.5, 1e-12);
  EXPECT_EQ(a.counters().duplicates, 1u);
  EXPECT_EQ(a.counters().dropped_incomplete + a.counters().resets + a.counters().missing_samples, 0u);
}

// World reset (ISystemReset -> Reset()): the open block is discarded, the reset counted once, and after the
// simulation clock restarts at 0 the first complete aligned block is required.
TEST(ImuBlockAverager, WorldResetRestartsCleanly)
{
  ImuBlockAverager a(10, kMs);
  Feed(a, 1, 35);
  a.Reset();
  EXPECT_EQ(a.counters().resets, 1u);
  EXPECT_EQ(a.counters().discarded_partial, 1u);              // the open 31..35 block
  EXPECT_EQ(Feed(a, 0, 20), (std::vector<int64_t>{10, 20}));  // earlier stamps after Reset(): no second count
  EXPECT_EQ(a.counters().resets, 1u);
  EXPECT_EQ(a.counters().discarded_partial, 2u);              // block (-10, 0] after the restart
  EXPECT_EQ(a.counters().dropped_incomplete, 0u);
}

// A stamp off the raw grid is ignored and counted; its block is incomplete and dropped.
TEST(ImuBlockAverager, OffGridStampIgnored)
{
  ImuBlockAverager a(10, kMs);
  Feed(a, 1, 10);
  ImuSample out;
  ImuSample s = Sample(11, 11.0);
  s.stamp_ns += kMs / 2;  // 11.5 ms
  EXPECT_FALSE(a.Add(s, &out));
  for (int64_t k = 13; k <= 20; ++k) {
    EXPECT_FALSE(a.Add(Sample(k, 1.0), &out));
  }
  EXPECT_EQ(a.counters().off_grid, 1u);
  EXPECT_EQ(a.counters().dropped_incomplete, 1u);
  EXPECT_EQ(Feed(a, 21, 30), (std::vector<int64_t>{30}));
}

// (g) Configuration consistency: DEC-038 values accepted; inconsistent values refused with a message.
TEST(ImuDecimationConfig, Validation)
{
  ImuDecimationConfig ok;  // 10, 1000 Hz, 100 Hz, 1 ms, sensor 1000 Hz
  EXPECT_EQ(ValidateConfig(ok), "");

  ImuDecimationConfig c = ok;
  c.output_rate_hz = 50.0;  // 10 x 50 != 1000
  EXPECT_NE(ValidateConfig(c).find("must equal block_size"), std::string::npos);
  c = ok;
  c.block_size = 1;
  EXPECT_NE(ValidateConfig(c), "");
  c = ok;
  c.raw_rate_hz = 0.0;
  EXPECT_NE(ValidateConfig(c), "");
  c = ok;
  c.physics_step_s = 0.002;  // a 1 ms raw period cannot be sampled with a 2 ms step
  EXPECT_NE(ValidateConfig(c).find("physics step"), std::string::npos);
  c = ok;
  c.physics_step_s = 0.0004;  // 1 ms / 0.4 ms = 2.5 steps
  EXPECT_NE(ValidateConfig(c).find("physics step"), std::string::npos);
  c = ok;
  c.physics_step_s = 0.0005;  // 2 steps per raw sample: consistent
  EXPECT_EQ(ValidateConfig(c), "");
  c = ok;
  c.sensor_update_rate_hz = 100.0;  // the IMU still at the old 100 Hz
  EXPECT_NE(ValidateConfig(c).find("update_rate"), std::string::npos);
  c = ok;
  c.raw_rate_hz = 3000.0;  // 333333.33 ns period
  c.output_rate_hz = 300.0;
  c.sensor_update_rate_hz = 3000.0;
  EXPECT_NE(ValidateConfig(c).find("nanoseconds"), std::string::npos);
}

// Rate consistency with the controller (DEC-038 item 9, DEC-026): the 10 ms block must be a whole number of
// controller periods.
TEST(ImuDecimationConfig, ControllerRateConstraint)
{
  for (double rate : {100.0, 200.0, 500.0, 1000.0}) {
    EXPECT_EQ(ValidateControllerRate(100.0, rate), "") << rate;
  }
  for (double rate : {50.0, 150.0, 30.0, 0.0}) {
    EXPECT_NE(ValidateControllerRate(100.0, rate), "") << rate;
  }
}

// Why the constraint matters: with a 50 Hz controller (20 ms hold), alternate blocks contain 0 and 2 command
// steps, so the per-block output alternates between ~0 and ~2x the mean acceleration.
TEST(ImuDecimationConfig, FiftyHertzControllerWouldAlias)
{
  ImuBlockAverager a(10, kMs);
  std::vector<double> outs;
  for (int64_t k = 1; k <= 100; ++k) {
    // Velocity step of 0.01 m/s once every 20 ms, in one 1 ms physics step: 10 m/s^2 for that step.
    const double accel = (k % 20 == 2) ? 10.0 : 0.0;
    ImuSample s = Sample(k, 0.0);
    s.linear_acceleration[0] = accel;
    ImuSample out;
    if (a.Add(s, &out)) {
      outs.push_back(out.linear_acceleration[0]);
    }
  }
  ASSERT_EQ(outs.size(), 10u);
  for (size_t i = 0; i < outs.size(); ++i) {
    EXPECT_NEAR(outs[i], (i % 2 == 0) ? 1.0 : 0.0, 1e-12);  // true mean is 0.5 m/s^2
  }
}
