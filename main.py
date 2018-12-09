#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : main.py
# Author            : Kacper Gracki <kacpergracki@gmail.com>
# Date              : 30.11.2018
# Last Modified Date: 30.11.2018
# Last Modified By  : Kacper Gracki <kacpergracki@gmail.com>

from agents.director import Director
from agents.bus import Bus
from credentials import *
from bus_lines.bus_line import BusLine
from bus.bus_navigator import BusNavigator

import time


if __name__ == "__main__":
    bus_line_414 = BusLine(414, 18400)
    director = Director(DIRECTOR, DIRECTOR_PASSWD)
    director.add_bus_line(bus_line_414)

    bus1 = Bus(BUS1, BUS1_PASSWD)
    bus_navigator_1 = BusNavigator(bus_line_414)
    bus_navigator_1.position_on_bus_line = 4000
    bus1.add_bus_navigator(bus_navigator_1)
    bus1.set_neighboring_buses(BUS3, BUS2)

    bus2 = Bus(BUS2, BUS2_PASSWD)
    bus_navigator_2 = BusNavigator(bus_line_414)
    bus_navigator_2.position_on_bus_line = 2000
    bus2.add_bus_navigator(bus_navigator_2)
    bus2.set_neighboring_buses(BUS1, BUS3)

    bus3 = Bus(BUS3, BUS3_PASSWD)
    bus_navigator_3 = BusNavigator(bus_line_414)
    bus3.add_bus_navigator(bus_navigator_3)
    bus3.set_neighboring_buses(BUS2, BUS1)

    director.start()
    time.sleep(5)
    bus1.start()
    bus2.start()
    bus3.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            director.stop()
            bus1.stop()
            bus2.stop()
            bus3.stop()
            break
    print("MAS finished")
