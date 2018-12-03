from map_data.distance_compute import *
from get_measures.ztmAPI import *
import time


URL = "https://api.um.warszawa.pl/api/action/busestrams_get/"

res_id = "%20f2e5503e927d-4ad3-9500-4ab9e55deb59"
line = 522  # line of actual bus to check
type = 1  # 1 for buses, 2 for trams


if __name__ == "__main__":
    # map latitude and longitude to integer values & then launch graph searching for calculate path value
    map_points = process_measures(URL, res_id, APIkey, line, type, measured_points)
 
    print("distance between 2 buses (graph edges):")
    print(distance_compute(map_points,
                                map_points[0][0],                    # latitude 1
                                map_points[0][1],                    # longitude 1
                                map_points[len(map_points)-1][0],    # latitude 2
                                map_points[len(map_points)-1][1]))   # longitude 2
 
    print("List of bus brigades:")
    print(get_brigades(URL, res_id, APIkey, line, type))
 
    firstBrigade = get_brigades(URL, res_id, APIkey, line, type)[0]
 
    print("Measure:")
    print(get_measure(URL, res_id, APIkey, line, type, firstBrigade))

