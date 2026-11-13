// Command-freshness guard for the AMR drive controller (M2; DEC-029, TS-015).
//
// The installed diff_drive_controller (4.42.1) judges a TwistStamped command stale only when its
// header stamp is OLDER than cmd_vel_timeout; a stamp in the future (e.g. a wall-clock stamp while
// the controller runs on simulation time) is never stale, so the command timeout cannot stop the
// robot (TS-015). This node sits between /cmd_vel (all command publishers) and the controller input
// /diff_drive_controller/cmd_vel and enforces the simulation-time command contract (DEC-026):
//   - forward only if |now - stamp| <= cmd_vel_timeout (the controller's own freshness window);
//   - reject zero stamps and everything while this node's clock is not yet valid (freshness cannot
//     be established), so the controller's timeout brakes the robot;
//   - forward with stamp = min(stamp, now), so a forwarded command can never stay fresh beyond
//     cmd_vel_timeout after its arrival.
// `now` is this node's ROS clock (use_sim_time: true -> simulation time from /clock).
#include <algorithm>
#include <memory>

#include "geometry_msgs/msg/twist_stamped.hpp"
#include "rclcpp/rclcpp.hpp"

class CmdVelGuard : public rclcpp::Node
{
public:
  CmdVelGuard()
  : Node("cmd_vel_guard")
  {
    timeout_ = declare_parameter<double>("cmd_vel_timeout", 0.5);
    pub_ = create_publisher<geometry_msgs::msg::TwistStamped>("cmd_vel_out", 10);
    sub_ = create_subscription<geometry_msgs::msg::TwistStamped>(
      "cmd_vel_in", 10, [this](geometry_msgs::msg::TwistStamped::UniquePtr msg) {on_cmd(std::move(msg));});
    RCLCPP_INFO(get_logger(), "forwarding commands with |now - stamp| <= %.3f s", timeout_);
  }

private:
  void on_cmd(geometry_msgs::msg::TwistStamped::UniquePtr msg)
  {
    const rclcpp::Time now = get_clock()->now();
    const rclcpp::Time stamp(msg->header.stamp, now.get_clock_type());
    if (now.nanoseconds() == 0) {
      reject("clock not yet valid", 0.0);
      return;
    }
    if (stamp.nanoseconds() == 0) {
      reject("zero stamp", 0.0);
      return;
    }
    const double age = (now - stamp).seconds();  // > 0: old, < 0: in the future
    if (age > timeout_ || age < -timeout_) {
      reject(age > 0 ? "stale stamp" : "future stamp (clock-domain mismatch?)", age);
      return;
    }
    msg->header.stamp = std::min(stamp, now);
    pub_->publish(std::move(msg));
  }

  void reject(const char * why, double age)
  {
    ++rejected_;
    RCLCPP_WARN_THROTTLE(
      get_logger(), *get_clock(), 1000, "rejected command: %s (age %.3f s, window %.3f s; %lu rejected so far)",
      why, age, timeout_, static_cast<unsigned long>(rejected_));
  }

  double timeout_;
  uint64_t rejected_{0};
  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr pub_;
  rclcpp::Subscription<geometry_msgs::msg::TwistStamped>::SharedPtr sub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CmdVelGuard>());
  rclcpp::shutdown();
  return 0;
}
