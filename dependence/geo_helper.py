import geocoder
import numpy as np

POS_STEP_LAT = 8
POS_STEP_LNG = 8
g = geocoder.arcgis('武汉')
northeast = g.bbox['northeast']
southwest = g.bbox['southwest']
print(northeast)
print(southwest)
lat_step = float(northeast[0] - southwest[0]) / POS_STEP_LAT
lng_step = float(northeast[1] - southwest[1]) / POS_STEP_LNG
lat_lngs = [
    (lat, lng)
    for lat in np.linspace(start=southwest[0], stop=northeast[0], num=POS_STEP_LAT, endpoint=True)
    for lng in np.linspace(start=southwest[1], stop=northeast[1], num=POS_STEP_LNG, endpoint=True)
]

for (lat, lng) in lat_lngs:
    address = geocoder.arcgis([lat, lng], method='reverse').address
    print(address)
