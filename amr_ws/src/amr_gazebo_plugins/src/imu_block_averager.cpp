// IMU block averager (DEC-038). Specification in the header and in docs/design/sensors.md §8.3-8.4.
#include "amr_gazebo_plugins/imu_block_averager.hpp"

#include <algorithm>
#include <cmath>
#include <sstream>

namespace amr_gazebo_plugins
{
namespace
{

// Floor division for possibly negative numerators (b > 0).
int64_t FloorDiv(int64_t a, int64_t b)
{
  int64_t q = a / b;
  if ((a % b != 0) && (a < 0)) {
    --q;
  }
  return q;
}

// True if x is within a relative 1e-9 of a positive integer; *n receives that integer.
bool IsPositiveInteger(double x, int64_t * n)
{
  const double r = std::round(x);
  if (r < 1.0 || std::fabs(x - r) > 1e-9 * std::max(1.0, r)) {
    return false;
  }
  *n = static_cast<int64_t>(r);
  return true;
}

}  // namespace

std::string ValidateConfig(const ImuDecimationConfig & c)
{
  std::ostringstream err;
  if (c.block_size < 2) {
    err << "block_size " << c.block_size << " must be >= 2";
  } else if (!(c.raw_rate_hz > 0.0) || !(c.output_rate_hz > 0.0) || !(c.physics_step_s > 0.0)) {
    err << "raw_rate " << c.raw_rate_hz << " Hz, output_rate " << c.output_rate_hz << " Hz and physics step "
        << c.physics_step_s << " s must all be > 0";
  } else if (std::fabs(c.raw_rate_hz - c.block_size * c.output_rate_hz) > 1e-9 * c.raw_rate_hz) {
    err << "raw_rate " << c.raw_rate_hz << " Hz must equal block_size " << c.block_size << " x output_rate "
        << c.output_rate_hz << " Hz";
  } else {
    int64_t period_ns = 0;
    int64_t steps = 0;
    if (!IsPositiveInteger(1e9 / c.raw_rate_hz, &period_ns)) {
      err << "raw period 1/" << c.raw_rate_hz << " Hz is not a whole number of nanoseconds";
    } else if (!IsPositiveInteger((1.0 / c.raw_rate_hz) / c.physics_step_s, &steps)) {
      err << "raw period " << 1.0 / c.raw_rate_hz << " s is not an integer multiple of the physics step "
          << c.physics_step_s << " s";
    } else if (std::fabs(c.sensor_update_rate_hz - c.raw_rate_hz) > 1e-9 * c.raw_rate_hz) {
      err << "IMU sensor update_rate " << c.sensor_update_rate_hz << " Hz must equal raw_rate " << c.raw_rate_hz
          << " Hz";
    }
  }
  return err.str();
}

std::string ValidateControllerRate(double output_rate_hz, double controller_rate_hz)
{
  std::ostringstream err;
  int64_t n = 0;
  if (!(output_rate_hz > 0.0) || !(controller_rate_hz > 0.0)) {
    err << "output rate " << output_rate_hz << " Hz and controller rate " << controller_rate_hz
        << " Hz must be > 0";
  } else if (!IsPositiveInteger(controller_rate_hz / output_rate_hz, &n)) {
    err << "output period 1/" << output_rate_hz << " s is not an integer multiple of the controller period 1/"
        << controller_rate_hz << " s (DEC-038 item 9, DEC-026)";
  }
  return err.str();
}

ImuBlockAverager::ImuBlockAverager(int block_size, int64_t raw_period_ns)
: block_size_(block_size), raw_period_ns_(raw_period_ns)
{
}

int64_t ImuBlockAverager::BlockOf(int64_t index) const
{
  // Block b holds the indices b*N - N + 1 ... b*N (aligned so that it ends on a multiple of N).
  return FloorDiv(index - 1, block_size_) + 1;
}

void ImuBlockAverager::CloseIncomplete()
{
  if (open_) {
    if (stream_started_) {
      ++counters_.dropped_incomplete;
    } else {
      ++counters_.discarded_partial;
    }
    open_ = false;
  }
}

void ImuBlockAverager::StartOver()
{
  if (open_) {
    ++counters_.discarded_partial;
    open_ = false;
  }
  have_last_ = false;
  stream_started_ = false;
}

bool ImuBlockAverager::Add(const ImuSample & s, ImuSample * out)
{
  ++counters_.samples;
  const int64_t index = FloorDiv(s.stamp_ns + raw_period_ns_ / 2, raw_period_ns_);
  const int64_t residual = s.stamp_ns - index * raw_period_ns_;
  if (residual > raw_period_ns_ / 100 || residual < -raw_period_ns_ / 100) {
    ++counters_.off_grid;
    return false;
  }
  if (have_last_) {
    if (index == last_index_) {
      ++counters_.duplicates;
      return false;
    }
    if (index < last_index_) {
      ++counters_.resets;
      StartOver();
    } else if (index > last_index_ + 1) {
      counters_.missing_samples += static_cast<uint64_t>(index - last_index_ - 1);
    }
  }
  have_last_ = true;
  last_index_ = index;

  const int64_t block = BlockOf(index);
  if (open_ && block != block_) {
    CloseIncomplete();
  }
  if (!open_) {
    open_ = true;
    block_ = block;
    count_ = 0;
    sum_accel_ = {{0.0, 0.0, 0.0}};
    sum_gyro_ = {{0.0, 0.0, 0.0}};
  }
  ++count_;
  for (int i = 0; i < 3; ++i) {
    sum_accel_[i] += s.linear_acceleration[i];
    sum_gyro_[i] += s.angular_velocity[i];
  }
  if (index != block * block_size_) {
    return false;  // not the last sample of its block yet
  }
  if (count_ != block_size_) {
    CloseIncomplete();
    return false;
  }
  open_ = false;
  stream_started_ = true;
  ++counters_.published;
  out->stamp_ns = s.stamp_ns;
  for (int i = 0; i < 3; ++i) {
    out->linear_acceleration[i] = sum_accel_[i] / block_size_;
    out->angular_velocity[i] = sum_gyro_[i] / block_size_;
  }
  return true;
}

void ImuBlockAverager::Reset()
{
  ++counters_.resets;
  StartOver();
}

void ImuBlockAverager::Finish()
{
  if (open_) {
    ++counters_.discarded_partial;
    open_ = false;
  }
}

}  // namespace amr_gazebo_plugins
