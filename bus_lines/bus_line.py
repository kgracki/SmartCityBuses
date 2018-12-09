class BusLine:
    line_number = None  # line number as an integer
    length_of_the_bus_route = None  # length of bus line route given in meters

    def __init__(self, line_number, length_of_the_bus_route):
        self.line_number = line_number
        self.length_of_the_bus_route = length_of_the_bus_route
