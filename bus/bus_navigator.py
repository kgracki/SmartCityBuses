class BusNavigator:
    start_time = None
    last_position_reading = None
    position_on_bus_line = 0
    velocity = 15 # velocity in m/s
    bus_line = None

    def __init__(self, bus_line, position_on_bus_line = 0):
        self.bus_line = bus_line
        self.position_on_bus_line = position_on_bus_line

    # based on time interval and velocity
    def update_position_on_bus_line(self, time_point):
        distance = self.calculate_driven_distance(time_point)

        # made changes to position of bus on bus line
        self.position_on_bus_line += distance

    # calculate driven distance since last calculation
    def calculate_driven_distance(self, time_point):
        # this is first distance calculation
        if self.last_position_reading is None:
            self.last_position_reading = self.start_time

        # calculate time interval
        time_interval = (time_point - self.last_position_reading).total_seconds()
        # we assume that during this time interval velocity is constant,
        # so we can easily calculate distance drived by bus in this time interval
        distance = time_interval * self.velocity;

        # prepare correct value for next time interval/distance calculating
        self.last_position_reading = time_point

        return distance
