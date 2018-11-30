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

import time


if __name__ == "__main__":
    director = Director(DIRECTOR, DIRECTOR_PASSWD)
    bus1 = Bus(BUS1, BUS1_PASSWD)
    bus2 = Bus(BUS2, BUS2_PASSWD)
    bus3 = Bus(BUS3, BUS3_PASSWD)
    bus4 = Bus(BUS4, BUS4_PASSWD)
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
