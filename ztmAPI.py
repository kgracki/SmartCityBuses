from ztmSettings import APIkey
import requests
import time
from math import radians, sin, cos, acos


class TransportZTM:
    def __init__(self, URL, res_id, APIkey, line, type):
        self.URL = URL
        self.res_id = res_id
        self.APIkey = APIkey
        self.line = line
        self.type = type

    def getAllLineMeasures(self):
        params = {'resource_id': self.res_id, 'apikey': self.APIkey, 'type': self.type, 'line': self.line}

        # sending get request and saving the response as response object
        r = requests.get(url=self.URL, params=params)

        return r.json()

    def getListOfLineBrigades(self, data):
        brigades = []

        for i in range(0, len(data["result"]), 1):
            brigades.append(data["result"][i]['Brigade'])

        return brigades

    def getMeasureFromBrigade(self, data, brigade):
        for i in range(0, len(data["result"]), 1):

            if (data["result"][i]['Brigade'] == brigade):
                latitude = data["result"][i]['Lat']
                longtitude = data["result"][i]['Lon']
                time = data["result"][i]['Time']

        return (latitude, longtitude, time)

    def calculateDistance(self, lat1, lon1, lat2, lon2):
        dist = 6371.01 * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2))
        return round(dist, 2)


# Lat - wspolrzedna szerokosci geograficznej w ukladzie WGS84 (EPSG:4326)
# Lon - wspolrzedna dlugosci geograficznej w ukladzie WGS84 (EPSG:4326)
# Time - czas wyslania sygnalu GPS
# Lines - numer linii autobusowej lub tramwajowej
# Brigade - numer brygady pojazdu

# timestamp, gps_lat, gps_long = get_current_bus()

URL = "https://api.um.warszawa.pl/api/action/busestrams_get/"

res_id = "%20f2e5503e927d-4ad3-9500-4ab9e55deb59"
line = 522  # line of actual bus to check
type = 1  # 1 for buses, 2 for trams

tran = TransportZTM(URL, res_id, APIkey, line, type)

data = tran.getAllLineMeasures()

brigade = tran.getListOfLineBrigades(data)[0]

# extracting data to dictionary
try:
    # firstly we have to check if the brigade list is empty
    if not brigade:
        print("The brigade list is empty!")
    else:
        while True:
            data = tran.getAllLineMeasures()
            # returns latitude, longtitude, time in tuple if particular brigade exists
            measure = tran.getMeasureFromBrigade(data, brigade)
            print(measure)
            file = open('lineMeasures.txt', 'a')
            file.write(str(measure[0]) + "\t" + str(measure[1]) + "\t" + str(measure[2]) + "\n")
            file.close()
            time.sleep(10)
except:
    print("We could not find requested by http GET data! Please check input parameters!")
