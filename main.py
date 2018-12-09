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
    bus1.add_bus_navigator(bus_navigator_1)

    bus2 = Bus(BUS2, BUS2_PASSWD)
    bus_navigator_2 = BusNavigator(bus_line_414)
    bus2.add_bus_navigator(bus_navigator_2)

    bus3 = Bus(BUS3, BUS3_PASSWD)
    bus_navigator_3 = BusNavigator(bus_line_414)
    bus3.add_bus_navigator(bus_navigator_3)

    bus4 = Bus(BUS4, BUS4_PASSWD)
    bus_navigator_4 = BusNavigator(bus_line_414)
    bus4.add_bus_navigator(bus_navigator_4)

    director.start()
    time.sleep(5)
    bus1.start()
    bus2.start()
    bus3.start()
    bus4.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            director.stop()
            bus1.stop()
            bus2.stop()
            bus3.stop()
            bus4.stop()
            break
    print("MAS finished")
