#include <chrono>
#include <cmath>
#include <memory>
#include <string>
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

class DynamicSignalGenerator : public rclcpp::Node {
public:
  DynamicSignalGenerator() : Node("dynamic_signal_generator") {
    this->declare_parameter<std::string>("signal", "step"); // step, sine, ramp
    this->declare_parameter<double>("amplitude", 0.4);       // m/s
    this->declare_parameter<double>("frequency", 0.2);       // Hz (für Sinus)
    this->declare_parameter<double>("duration", 8.0);        // s

    pub_ = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
    timer_ = this->create_wall_timer(50ms, std::bind(&DynamicSignalGenerator::publish_signal, this)); // 20 Hz
    start_time_ = this->now();
  }

private:
  void publish_signal() {
    double t = (this->now() - start_time_).seconds();
    std::string type = this->get_parameter("signal").as_string();
    double amp = this->get_parameter("amplitude").as_double();
    double freq = this->get_parameter("frequency").as_double();
    double dur = this->get_parameter("duration").as_double();

    geometry_msgs::msg::Twist msg;

    if (t > dur) {
      msg.linear.x = 0.0;
      pub_->publish(msg);
      rclcpp::shutdown();
      return;
    }

    if (type == "step") {
      // Rechteck-Sprungantwort
      if (t >= 1.0 && t < 4.0) msg.linear.x = amp;
      else if (t >= 4.0 && t < 7.0) msg.linear.x = -amp;
    } else if (type == "sine") {
      msg.linear.x = amp * std::sin(2.0 * M_PI * freq * t);
    } else if (type == "ramp") {
      msg.linear.x = std::min(amp, (amp / 3.0) * t);
    }

    pub_->publish(msg);
  }

  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_;
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Time start_time_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DynamicSignalGenerator>());
  return 0;
}