class BusPosition:
    direction = None
    position_on_bus_line = None

    def __init__(self, position_on_bus_line, direction):
        self.direction = direction
        self.position_on_bus_line = position_on_bus_line
