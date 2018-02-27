import geocoder
from math import radians, cos, sin, asin, sqrt
import numpy as np

# ele区域范围 单位:公里
from core.db_engine import dbsession, Latlng

ELE_DISTANCE = 5
CITY = '武汉'


def geodistance(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlon = lng2 - lng1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    dis = 2 * asin(sqrt(a)) * 6371
    return dis


def get_latlngs(city):
    g = geocoder.arcgis(city)
    northeast = g.bbox['northeast']
    southwest = g.bbox['southwest']
    # 东西向距离
    lat_dis = geodistance(northeast[0], southwest[1], northeast[0], northeast[1])
    # 东西向每步距离
    lat_step_dis = lat_dis
    # 东西向步数
    lat_step = 0
    while lat_step_dis > ELE_DISTANCE:
        lat_step += 1
        lat_step_dis = lat_dis / lat_step
    # 南北向距离
    lng_dis = geodistance(northeast[0], southwest[1], southwest[0], southwest[1])
    # 南北向每步距离
    lng_step_dis = lng_dis
    # 南北向步数
    lng_step = 0
    while lng_step_dis > ELE_DISTANCE:
        lng_step += 1
        lng_step_dis = lng_dis / lng_step
    lat_lngs = [
        '{},{}'.format(lat, lng)
        for lat in np.linspace(start=southwest[0], stop=northeast[0], num=lat_step, endpoint=True)
        for lng in np.linspace(start=southwest[1], stop=northeast[1], num=lng_step, endpoint=True)
    ]

    for lat_lng in lat_lngs:
        latlng = lat_lng.split(',')
        address = geocoder.arcgis([latlng[0], latlng[1]], method='reverse').address
        print(address)
        old_lat_lng = dbsession.query(Latlng).filter(Latlng.lat_lng == lat_lng).first()
        if old_lat_lng is None:
            dbsession.add(Latlng(
                address=address,
                city=CITY,
                lat_lng=lat_lng
            ))
        dbsession.commit()


if __name__ == '__main__':
    get_latlngs(CITY)
    dbsession.close()
