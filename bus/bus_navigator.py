from bus.bus_position import BusPosition;

class BusNavigator:
    start_time = None  # time when bus starts riding on this line
    last_position_reading = None  # time of last position reading
    position_on_bus_line = 0  # position on bus line in meters
    velocity = 15  # velocity in m/s
    nominal_velocity = 15  # velocity in m/s
    bus_line = None  # object containing bus line
    '''
        North direction - 1, south direction -1 ~~ Direction of movement of bus, 
        does he ride from starting point to end point or from end point to starting point?
    '''
    direction = 1

    def __init__(self, bus_line, position_on_bus_line = 0):
        self.bus_line = bus_line
        self.position_on_bus_line = position_on_bus_line

    # based on time interval and velocity
    def update_position_on_bus_line(self, time_point):
        distance = self.calculate_driven_distance(time_point)

        # made changes to position of bus on bus line
        self.position_on_bus_line += self.direction * distance

        # check if maybe bus reach end of line route? We assume that he immediately turn backs
        if self.position_on_bus_line > self.bus_line.length_of_the_bus_route:
            self.position_on_bus_line = 2 * self.bus_line.length_of_the_bus_route - self.position_on_bus_line
            self.direction *= -1

        # check if maybe bus reach starting point, turn him back
        if self.position_on_bus_line < 0:
            self.position_on_bus_line *= -1
            self.direction *= -1

    # calculate driven distance since last calculation
    def calculate_driven_distance(self, time_point):
        # this is first distance calculation
        if self.last_position_reading is None:
            self.last_position_reading = self.start_time

        # calculate time interval
        time_interval = (time_point - self.last_position_reading).total_seconds()
        # we assume that during this time interval velocity is constant,
        # so we can easily calculate distance drived by bus in this time interval
        distance = time_interval * self.velocity

        # prepare correct value for next time interval/distance calculating
        self.last_position_reading = time_point

        return distance

    def report_position(self):
        if self.direction == 1:
            direction = "north"
        else:
            direction = "south"

        return "My position: {}, I'm heading {}" . format(self.position_on_bus_line, direction)

    def calculate_distance_between(self, bus_position_point_of_view: BusPosition, bus_2_position: BusPosition):
        # do they go in the same direction?
        if bus_position_point_of_view.direction == bus_2_position.direction:
            return bus_2_position.position_on_bus_line - bus_position_point_of_view.position_on_bus_line

        # case when first bus is comming from start to end and second bus from end to start
        if bus_position_point_of_view.direction == 1 and bus_2_position.direction == -1:
            bus1_to_end_of_track_distance = (self.bus_line.length_of_the_bus_route -
                                             bus_position_point_of_view.position_on_bus_line)
            bus2_from_end_of_track_distance = (self.bus_line.length_of_the_bus_route -
                                               bus_2_position.position_on_bus_line)
            return bus1_to_end_of_track_distance + bus2_from_end_of_track_distance

        # case when first bus is comming from end to start and second bus from start to end
        if bus_position_point_of_view.direction == -1 and bus_2_position.direction == 1:
            bus1_to_start_of_track_distance = (self.bus_line.length_of_the_bus_route -
                                               bus_position_point_of_view.position_on_bus_line)
            bus2_from_start_of_track_distance = (self.bus_line.length_of_the_bus_route -
                                                 bus_2_position.position_on_bus_line)
            return bus1_to_start_of_track_distance + bus2_from_start_of_track_distance
