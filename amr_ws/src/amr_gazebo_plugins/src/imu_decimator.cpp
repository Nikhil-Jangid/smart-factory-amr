// ImuDecimator: Gazebo Sim 8 system plugin for DEC-038 (IMU output decimation; docs/design/sensors.md §8).
//
// Attached to the robot model (amr.sensors.xacro, use_sensors:=true only). It subscribes to the raw IMU topic
// (default /imu_raw, 1 kHz, internal to Gazebo) and publishes the 100 Hz block mean on the output topic (default
// /imu), which the existing ros_gz_bridge maps to ROS /imu unchanged. The averaging rules live in the
// Gazebo-independent ImuBlockAverager. This file only reads and validates the configuration, moves messages, and
// copies orientation, orientation covariance, frame and entity name from the newest raw sample of each block. The
// rate covariances are the newest sample's divided by the block size (covariance of a mean of independent samples).
//
// SDF parameters (all optional; defaults are the DEC-038 values):
//   <input_topic>/imu_raw</input_topic>  <output_topic>/imu</output_topic>
//   <block_size>10</block_size>  <raw_rate>1000</raw_rate>  <output_rate>100</output_rate>
// Validation (DEC-038 item 9): raw_rate = block_size x output_rate; the raw period is an integer multiple of the
// world's physics step; exactly one IMU sensor of this model publishes input_topic, at raw_rate. It runs once, at
// the first PreUpdate, not in Configure(): when the model is part of the world file (not spawned into a running
// world), Configure() runs before the world's Physics component exists (found by TEST-M3-14 (g), 2026-11-03).
// Nothing is subscribed or published before the check passes. On an invalid configuration the plugin logs an
// error and stays inactive, so /imu is silent and the problem cannot go unnoticed. Gazebo Sim 8 gives a system
// no way to fail its own load.
#include <chrono>
#include <cstdint>
#include <iostream>
#include <memory>
#include <mutex>
#include <string>

#include <gz/common/Console.hh>
#include <gz/msgs/imu.pb.h>
#include <gz/plugin/Register.hh>
#include <gz/sim/EntityComponentManager.hh>
#include <gz/sim/System.hh>
#include <gz/sim/Util.hh>
#include <gz/sim/components/Imu.hh>
#include <gz/sim/components/Physics.hh>
#include <gz/transport/Node.hh>
#include <sdf/Element.hh>

#include "amr_gazebo_plugins/imu_block_averager.hpp"

namespace amr_gazebo_plugins
{

class ImuDecimator
  : public gz::sim::System,
  public gz::sim::ISystemConfigure,
  public gz::sim::ISystemPreUpdate,
  public gz::sim::ISystemReset
{
public:
  ~ImuDecimator() override
  {
    if (!active_) {
      return;
    }
    node_.Unsubscribe(input_topic_);
    std::lock_guard<std::mutex> lock(mutex_);
    averager_->Finish();  // a partial block is discarded, never published
    const ImuBlockCounters & c = averager_->counters();
    std::cout << "[amr_gazebo_plugins::ImuDecimator] shutdown: raw samples " << c.samples << ", published "
              << c.published << ", dropped_incomplete " << c.dropped_incomplete << ", discarded_partial "
              << c.discarded_partial << ", missing_samples " << c.missing_samples << ", duplicates "
              << c.duplicates << ", off_grid " << c.off_grid << ", resets " << c.resets << std::endl;
  }

  void Configure(
    const gz::sim::Entity & entity, const std::shared_ptr<const sdf::Element> & sdf,
    gz::sim::EntityComponentManager &, gz::sim::EventManager &) override
  {
    model_ = entity;
    input_topic_ = sdf->Get<std::string>("input_topic", "/imu_raw").first;
    output_topic_ = sdf->Get<std::string>("output_topic", "/imu").first;
    config_.block_size = sdf->Get<int>("block_size", 10).first;
    config_.raw_rate_hz = sdf->Get<double>("raw_rate", 1000.0).first;
    config_.output_rate_hz = sdf->Get<double>("output_rate", 100.0).first;
  }

  // One-time validation and activation at the first PreUpdate, when every world and model component exists. The
  // IMU system publishes its first sample in PostUpdate, so no raw sample precedes the subscription.
  void PreUpdate(const gz::sim::UpdateInfo &, gz::sim::EntityComponentManager & ecm) override
  {
    if (checked_) {
      return;
    }
    checked_ = true;
    const gz::sim::Entity world = gz::sim::worldEntity(ecm);
    const auto * physics = ecm.Component<gz::sim::components::Physics>(world);
    config_.physics_step_s = physics ? physics->Data().MaxStepSize() : 0.0;

    int matches = 0;
    const auto descendants = ecm.Descendants(model_);
    ecm.Each<gz::sim::components::Imu>(
      [&](const gz::sim::Entity & e, const gz::sim::components::Imu * imu) -> bool
      {
        if (descendants.count(e) && imu->Data().Topic() == input_topic_) {
          ++matches;
          config_.sensor_update_rate_hz = imu->Data().UpdateRate();
        }
        return true;
      });

    std::string error;
    if (!physics) {
      error = "the world has no physics component";
    } else if (matches != 1) {
      error = "expected exactly one IMU sensor of this model on topic " + input_topic_ + ", found " +
        std::to_string(matches);
    } else {
      error = ValidateConfig(config_);
    }
    if (!error.empty()) {
      gzerr << "[amr_gazebo_plugins::ImuDecimator] invalid configuration, NOT active (DEC-038): " << error
            << std::endl;
      return;
    }

    std::lock_guard<std::mutex> lock(mutex_);
    block_size_ = static_cast<float>(config_.block_size);
    averager_ = std::make_unique<ImuBlockAverager>(
      config_.block_size, static_cast<int64_t>(std::llround(1e9 / config_.raw_rate_hz)));
    publisher_ = node_.Advertise<gz::msgs::IMU>(output_topic_);
    if (!publisher_ || !node_.Subscribe(input_topic_, &ImuDecimator::OnRaw, this)) {
      gzerr << "[amr_gazebo_plugins::ImuDecimator] cannot advertise " << output_topic_ << " or subscribe "
            << input_topic_ << "; NOT active" << std::endl;
      averager_.reset();
      return;
    }
    active_ = true;
    std::cout << "[amr_gazebo_plugins::ImuDecimator] active: " << input_topic_ << " (" << config_.raw_rate_hz
              << " Hz) -> " << output_topic_ << " (" << config_.output_rate_hz << " Hz), block "
              << config_.block_size << ", physics step " << config_.physics_step_s << " s" << std::endl;
  }

  void Reset(const gz::sim::UpdateInfo &, gz::sim::EntityComponentManager &) override
  {
    if (!active_) {
      return;
    }
    std::lock_guard<std::mutex> lock(mutex_);
    averager_->Reset();
  }

private:
  void OnRaw(const gz::msgs::IMU & msg)
  {
    ImuSample in;
    in.stamp_ns = static_cast<int64_t>(msg.header().stamp().sec()) * 1000000000LL + msg.header().stamp().nsec();
    in.linear_acceleration = {{msg.linear_acceleration().x(), msg.linear_acceleration().y(),
        msg.linear_acceleration().z()}};
    in.angular_velocity = {{msg.angular_velocity().x(), msg.angular_velocity().y(), msg.angular_velocity().z()}};

    ImuSample mean;
    uint64_t dropped = 0;
    {
      std::lock_guard<std::mutex> lock(mutex_);
      const uint64_t dropped_before = averager_->counters().dropped_incomplete;
      if (!averager_->Add(in, &mean)) {
        dropped = averager_->counters().dropped_incomplete - dropped_before;
        if (dropped) {
          WarnDropped(in.stamp_ns);
        }
        return;
      }
    }
    // The block ends with this sample, so `msg` is the newest sample: keep its header (stamp t, frame),
    // entity name, orientation and covariances; replace the rates by the block means.
    gz::msgs::IMU out(msg);
    out.mutable_linear_acceleration()->set_x(mean.linear_acceleration[0]);
    out.mutable_linear_acceleration()->set_y(mean.linear_acceleration[1]);
    out.mutable_linear_acceleration()->set_z(mean.linear_acceleration[2]);
    out.mutable_angular_velocity()->set_x(mean.angular_velocity[0]);
    out.mutable_angular_velocity()->set_y(mean.angular_velocity[1]);
    out.mutable_angular_velocity()->set_z(mean.angular_velocity[2]);
    // The covariance of a mean of N independent samples is the per-sample covariance / N. The raw sensor's
    // covariance fields carry sigma_raw^2 = N x sigma_output^2, so dividing by N publishes sigma_output^2, the
    // DEC-032 values (1e-6 (rad/s)^2, 1e-4 (m/s^2)^2), as before DEC-038. The orientation is not averaged, so its
    // covariance is copied unchanged.
    for (int i = 0; i < out.angular_velocity_covariance().data_size(); ++i) {
      out.mutable_angular_velocity_covariance()->set_data(i, out.angular_velocity_covariance().data(i) / block_size_);
    }
    for (int i = 0; i < out.linear_acceleration_covariance().data_size(); ++i) {
      out.mutable_linear_acceleration_covariance()->set_data(
        i, out.linear_acceleration_covariance().data(i) / block_size_);
    }
    publisher_.Publish(out);
  }

  // Rate-limited (wall time, at most once per 5 s) warning for dropped blocks; the total is reported at shutdown.
  void WarnDropped(int64_t stamp_ns)
  {
    const auto now = std::chrono::steady_clock::now();
    if (now - last_warning_ < std::chrono::seconds(5)) {
      return;
    }
    last_warning_ = now;
    gzwarn << "[amr_gazebo_plugins::ImuDecimator] incomplete IMU block dropped at stamp " << stamp_ns
           << " ns (total dropped " << averager_->counters().dropped_incomplete << ")" << std::endl;
  }

  gz::sim::Entity model_{gz::sim::kNullEntity};
  ImuDecimationConfig config_;
  std::string output_topic_;
  bool checked_{false};
  gz::transport::Node node_;
  gz::transport::Node::Publisher publisher_;
  std::string input_topic_;
  std::mutex mutex_;
  std::unique_ptr<ImuBlockAverager> averager_;
  bool active_{false};
  float block_size_{10.0f};
  std::chrono::steady_clock::time_point last_warning_{};
};

}  // namespace amr_gazebo_plugins

GZ_ADD_PLUGIN(
  amr_gazebo_plugins::ImuDecimator, gz::sim::System,
  amr_gazebo_plugins::ImuDecimator::ISystemConfigure,
  amr_gazebo_plugins::ImuDecimator::ISystemPreUpdate,
  amr_gazebo_plugins::ImuDecimator::ISystemReset)
GZ_ADD_PLUGIN_ALIAS(amr_gazebo_plugins::ImuDecimator, "amr_gazebo_plugins::ImuDecimator")
