#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : distance_compute.py
# Author            : Kacper Gracki <kacpergracki@gmail.com>
# Date              : 29.11.2018
# Last Modified Date: 29.11.2018
# Last Modified By  : Kacper Gracki <kacpergracki@gmail.com>

from math import hypot
from bus_test_map import measured_points
from ztmAPI import *
from ztmSettings import APIkey


def distance_compute(pts, ptX1, ptY1, ptX2, ptY2):
    # create lambda expression
    ptdiff = lambda p: (p[0][0] - p[1][0], p[0][1] - p[1][1])
    # check if your coordinates are in the map
    try:
        # get index of A bus
        apt = pts.index((ptX1, ptY1))
        # get index of B bus
        bpt = pts.index((ptX2, ptY2))
        # get distance between A and B
        if apt < bpt:
            distance = pts[apt:bpt]
        else:
            distance = pts[bpt:apt]
        # map given values
        diffs = map(ptdiff, zip(distance[:-1], distance[1:]))
        # compute path length
        path = sum(hypot(d1, d2) for d1, d2 in diffs)
    except ValueError:
        path = None

    # return path computed to meters
    return path / 1000 * 111


URL = "https://api.um.warszawa.pl/api/action/busestrams_get/"

res_id = "%20f2e5503e927d-4ad3-9500-4ab9e55deb59"
line = 522  # line of actual bus to check
type = 1  # 1 for buses, 2 for trams

'''
# methods usage:

distance_compute(map_points,
                 first_point_latitude,
                 first_point_longitude,
                 last_point_latitude,
                 last_point_longitude)

getBrigades(URL, res_id, APIkey, line, type)
# returns list of brigades (list of strings)              

getMeasure(URL, res_id, APIkey, line, type, brigade_id)
# returns measure (latitude, longitude, time)                 
'''

if __name__ == "__main__":

    bus = TransportZTM(URL, res_id, APIkey, line, type)
    # map latitude and longitude to integer values & then launch graph searching for calculate path value
    map_points = bus.mapMeasures(measured_points)

    print("distance between 2 buses (graph edges):")
    print(distance_compute(map_points,
                           map_points[0][0],                    # latitude 1
                           map_points[0][1],                    # longitude 1
                           map_points[len(map_points)-1][0],    # latitude 2
                           map_points[len(map_points)-1][1]))   # longitude 2

    print("List of bus brigades:")
    print(getBrigades(URL, res_id, APIkey, line, type))

    firstBrigade = getBrigades(URL, res_id, APIkey, line, type)[0]

    print("Measure:")
    print(getMeasure(URL, res_id, APIkey, line, type, firstBrigade))
