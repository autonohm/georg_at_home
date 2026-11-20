#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"

using namespace std::chrono_literals;

/* This node subscribes to a Twist (cmd_vel) message,
 * applies a PT1 regulator to it,
 * and publishes the result */

class TwistLimiter : public rclcpp::Node {
public:
    TwistLimiter() : Node("twist_limiter") {
        this->declare_parameter("acceleration_limit_linear", 1.5);
        this->declare_parameter("acceleration_limit_angular", 1.5);
        this->declare_parameter("publisher_hz", 20.0);

        this->declare_parameter("pause_after_publishing_zero", false);

        this->declare_parameter("maximum.linear.x", 1.0);
        this->declare_parameter("maximum.linear.y", 1.0);
        this->declare_parameter("maximum.linear.z", 1.0);
        this->declare_parameter("maximum.angular.x", 1.0);
        this->declare_parameter("maximum.angular.y", 1.0);
        this->declare_parameter("maximum.angular.z", 1.0);

        // allow overriding QoS settings
        this->sub_options_.qos_overriding_options = rclcpp::QosOverridingOptions::with_default_policies();
        this->pub_options_.qos_overriding_options = rclcpp::QosOverridingOptions::with_default_policies();
        auto qos = rclcpp::QoS(10);
        qos.best_effort();
        subscription_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "twist_limiter/in", qos, std::bind(&TwistLimiter::topic_callback, this, std::placeholders::_1), this->sub_options_);
        publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("twist_limiter/out", qos, this->pub_options_);
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(static_cast<int>(1000.0 / this->get_parameter("publisher_hz").as_double())), std::bind(&TwistLimiter::timer_callback, this)
        );

        RCLCPP_INFO(this->get_logger(), "twist limiter online!");
    }

private:
    void topic_callback(const geometry_msgs::msg::Twist &msg) {
        this->in_value = msg;
        this->last_sub_msg = std::chrono::system_clock::now();
    }

    bool is_twist_zeroed(const geometry_msgs::msg::Twist &msg) {
        return !(msg.linear.x || msg.linear.y || msg.linear.z || msg.angular.x || msg.angular.y || msg.angular.z);
    }

    void timer_callback() {
        if (this->get_parameter("pause_after_publishing_zero").as_bool())
            if (is_twist_zeroed(in_value) && is_twist_zeroed(out_value))
                return;

        if ((this->last_sub_msg + 2s) < std::chrono::system_clock::now() && !is_twist_zeroed(in_value)) {
            // timeout detected + values aren't 0 (previous zeroing or controller untouched)
            RCLCPP_WARN(this->get_logger(), "Last message was 2s ago - Lag detected! Zeroing output.");
            // zero input: this preserves the deceleration limit, to not crash the robot
            this->in_value.linear.x = this->in_value.linear.y = this->in_value.linear.z = this->in_value.angular.x = this->in_value.angular.y = this->in_value.angular.z = 0.0;
        }

        // 1. Clamp the incoming change in velocity (aka acceleration) to `accel_limit`. Store as `increment`
        // 2. Check if `increment + *out` would exceed the `numerical_limit`. Maximum vel is assumed symmetrical in all directions (abs value)
        auto controller = [](double *out, const double in, const double numerical_limit, const double accel_limit) -> void {
            double increment = std::max(-accel_limit, std::min(accel_limit, in - (*out))); // limit max accel, min/max
            if (abs((*out) + increment) > numerical_limit) // new value would exceed maximum value
                (*out) = ((*out) > 0) ? numerical_limit : -numerical_limit; // use the limit as value (maximum)
            else
                (*out) += increment;
        };
        // linear
        const double max_vel_linear = this->get_parameter("acceleration_limit_linear").as_double() / this->get_parameter("publisher_hz").as_double(); // m/s² / 1/s = m/s
        controller(&this->out_value.linear.x, this->in_value.linear.x, this->get_parameter("maximum.linear.x").as_double(), max_vel_linear);
        controller(&this->out_value.linear.y, this->in_value.linear.y, this->get_parameter("maximum.linear.y").as_double(), max_vel_linear);
        controller(&this->out_value.linear.z, this->in_value.linear.z, this->get_parameter("maximum.linear.z").as_double(), max_vel_linear);
        // angular
        const double max_vel_angular = this->get_parameter("acceleration_limit_angular").as_double() / this->get_parameter("publisher_hz").as_double(); // rad/s² / 1/s = rad/s
        controller(&this->out_value.angular.x, this->in_value.angular.x, this->get_parameter("maximum.angular.x").as_double(), max_vel_angular);
        controller(&this->out_value.angular.y, this->in_value.angular.y, this->get_parameter("maximum.angular.y").as_double(), max_vel_angular);
        controller(&this->out_value.angular.z, this->in_value.angular.z, this->get_parameter("maximum.angular.z").as_double(), max_vel_angular);

        this->publisher_->publish(this->out_value);
    }


    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::SubscriptionOptions sub_options_;
    rclcpp::PublisherOptions pub_options_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr subscription_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;

    geometry_msgs::msg::Twist in_value;
    geometry_msgs::msg::Twist out_value;
    std::chrono::time_point<std::chrono::system_clock> last_sub_msg;
};


int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<TwistLimiter>());
    rclcpp::shutdown();
    return 0;
}
