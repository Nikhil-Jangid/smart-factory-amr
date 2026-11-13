// IMU block averager (DEC-038; design: docs/design/sensors.md §8).
//
// Gazebo-independent core of the ImuDecimator system plugin. It turns a raw IMU stream sampled on a fixed grid
// (1 kHz) into non-overlapping block means (10 samples -> 100 Hz):
//   - Blocks are aligned to the output grid: the block that ends at sample index k_end (k_end a multiple of the
//     block size N) holds the samples k_end - N + 1 ... k_end. With a 1 ms raw period and N = 10, these are the
//     stamps t - 9 ms ... t, with t a multiple of 10 ms.
//   - A block is emitted only when all N samples are present exactly once. The output carries the stamp of the
//     newest sample (t) and the per-axis arithmetic mean of linear acceleration and angular velocity, i.e. the mean
//     over the interval (t - 10 ms, t].
//   - Startup or after a reset: nothing is emitted until the first complete aligned block.
//   - Missing sample: its block is dropped and counted. Duplicate stamp: ignored and counted. Stamp earlier than
//     the previous one (time reversal, e.g. a world reset): the buffer is cleared, the event counted, and the
//     startup rule applies again. Shutdown (Finish): an open partial block is discarded, never emitted.
// Pause/resume needs no special handling: blocks are formed from sample stamps (simulation time), not arrival time.
#ifndef AMR_GAZEBO_PLUGINS__IMU_BLOCK_AVERAGER_HPP_
#define AMR_GAZEBO_PLUGINS__IMU_BLOCK_AVERAGER_HPP_

#include <array>
#include <cstdint>
#include <string>

namespace amr_gazebo_plugins
{

struct ImuSample
{
  int64_t stamp_ns{0};
  std::array<double, 3> linear_acceleration{{0.0, 0.0, 0.0}};
  std::array<double, 3> angular_velocity{{0.0, 0.0, 0.0}};
};

struct ImuBlockCounters
{
  uint64_t samples{0};             // raw samples received
  uint64_t published{0};           // complete blocks emitted
  uint64_t dropped_incomplete{0};  // blocks dropped because a sample was missing (after the first complete block)
  uint64_t discarded_partial{0};   // partial blocks at startup, after a reset, or at shutdown (expected, <= 1 each)
  uint64_t missing_samples{0};     // grid indices skipped between consecutive samples
  uint64_t duplicates{0};          // samples whose stamp repeats the previous one (ignored)
  uint64_t off_grid{0};            // samples whose stamp is not on the raw grid (ignored)
  uint64_t resets{0};              // time reversals plus explicit Reset() calls
};

/// Configuration checked at plugin load (DEC-038 items 2, 3, 9). Rates in Hz, step in s.
struct ImuDecimationConfig
{
  int block_size{10};
  double raw_rate_hz{1000.0};
  double output_rate_hz{100.0};
  double physics_step_s{0.001};
  double sensor_update_rate_hz{1000.0};  // <update_rate> of the IMU sensor that publishes the input topic
};

/// Returns an empty string if the configuration is consistent, otherwise a message naming the values:
///   block_size >= 2; rates > 0; raw_rate = block_size * output_rate; the raw period is a whole number of ns;
///   the raw period is an integer multiple of the physics step; the sensor update rate equals raw_rate.
std::string ValidateConfig(const ImuDecimationConfig & config);

/// DEC-038 item 9 (dependency on DEC-026): the output (block) period must be an integer multiple of the
/// controller period, so that every block holds the same number of controller command steps. Returns an empty
/// string if output_period / controller_period is a positive integer, otherwise a message.
std::string ValidateControllerRate(double output_rate_hz, double controller_rate_hz);

class ImuBlockAverager
{
public:
  /// block_size >= 2 and raw_period_ns > 0 (checked by ValidateConfig before construction).
  ImuBlockAverager(int block_size, int64_t raw_period_ns);

  /// Adds one raw sample. Returns true and fills *out when the sample completes a block.
  bool Add(const ImuSample & sample, ImuSample * out);

  /// World reset: discards any open block, clears the history and counts a reset.
  void Reset();

  /// Shutdown: discards any open partial block. Nothing is emitted.
  void Finish();

  const ImuBlockCounters & counters() const {return counters_;}

private:
  void StartOver();
  void CloseIncomplete();
  int64_t BlockOf(int64_t index) const;

  const int block_size_;
  const int64_t raw_period_ns_;
  ImuBlockCounters counters_;
  bool have_last_{false};
  int64_t last_index_{0};
  bool stream_started_{false};  // true after the first complete block since start or reset
  bool open_{false};
  int64_t block_{0};
  int count_{0};
  std::array<double, 3> sum_accel_{{0.0, 0.0, 0.0}};
  std::array<double, 3> sum_gyro_{{0.0, 0.0, 0.0}};
};

}  // namespace amr_gazebo_plugins

#endif  // AMR_GAZEBO_PLUGINS__IMU_BLOCK_AVERAGER_HPP_
