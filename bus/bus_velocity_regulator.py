from bus.bus_navigator import BusNavigator
from bus.bus_navigator import BusPosition


class BusVelocityRegulator:
    # python sucks!
    @staticmethod
    def calculate_new_bus_velocity(current_bus_navigator: BusNavigator, desired_distance, max_velocity, max_velocity_change, neighbours_info):
        factor = 0
        current_bus_position = BusPosition(current_bus_navigator.position_on_bus_line,current_bus_navigator.direction)
        next_bus_position = BusPosition(float(neighbours_info["next_bus_position"]), int(neighbours_info["next_bus_direction"]))
        previous_bus_position = BusPosition(float(neighbours_info["previous_bus_position"]), int(neighbours_info["previous_bus_direction"]))

        distance_to_next_bus = current_bus_navigator.calculate_distance_between(current_bus_position, next_bus_position, True)
        distance_to_previous_bus = current_bus_navigator.calculate_distance_between(current_bus_position, previous_bus_position, False)

        # #
        # real work to know how we should change velocity of the bus
        # #

        # normal case, middle bus, not first or last one
        if distance_to_next_bus > 0 and distance_to_previous_bus < 0:
            factor = (distance_to_next_bus - desired_distance) / desired_distance - (distance_to_previous_bus - desired_distance) / desired_distance
        # it means that next bus is very, very daleko
        elif distance_to_next_bus < 0 and distance_to_previous_bus < 0:
            factor = 1
        # it means that previous bus is very daleko
        elif  distance_to_next_bus > 0 and distance_to_previous_bus > 0:
            factor = -1

        if factor > 1:
            factor = 1
        if factor < -1:
            factor = -1

        velocity_change = max_velocity_change * factor
        current_bus_navigator.velocity += velocity_change

        # change of velocity can by done only in [nominal_velocity - max_velocity_change, nominal_velocity + max_velocity_change]
        if current_bus_navigator.velocity > max_velocity:
            current_bus_navigator.velocity = max_velocity

        if current_bus_navigator.velocity < current_bus_navigator.nominal_velocity - max_velocity_change:
            current_bus_navigator.velocity = current_bus_navigator.nominal_velocity - max_velocity_change

        return velocity_change
