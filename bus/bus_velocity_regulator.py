class BusVelocityRegulator:
    # python sucks!
    @staticmethod
    def calculate_new_bus_velocity(current_bus_navigator, desired_distance, max_velocity, max_velocity_change, neighbours_info):
        velocity_change = 1

        if current_bus_navigator.velocity + velocity_change <= max_velocity:
            current_bus_navigator.velocity += velocity_change

        return velocity_change
