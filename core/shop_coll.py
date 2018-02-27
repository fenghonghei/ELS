import json
import asyncio
import aiohttp

from core.db_engine import dbsession, Shop, Latlng

CITY_LATLNG_PATH = '../dependence/city_latlng.json'
SHOP_URL = 'https://h5.ele.me/restapi/shopping/v3/restaurants'


async def get_shops(city, params, latlng_id, latlng):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SHOP_URL, params=params) as response:
                data = await response.text()
                restaurant__json = json.loads(data)
                print(restaurant__json)
                restaurant__list = restaurant__json['items']
                for restaurant in restaurant__list:
                    restaurant = restaurant['restaurant']
                    shop_id = restaurant['id']
                    shop_name = restaurant['name']
                    shop_address = restaurant['address']
                    shop_openning_hours = ''.join(restaurant['opening_hours'])
                    shop_phone = restaurant['phone']
                    shop_flavor_ids = ''
                    for flavor in restaurant['flavors']:
                        shop_flavor_ids += str(flavor['id'])
                        shop_flavor_ids += ','
                    dbsession.merge(Shop(
                        id=shop_id,
                        name=shop_name,
                        address=shop_address,
                        city=city,
                        latlng_id=latlng_id,
                        latlng=latlng,
                        flavors=shop_flavor_ids[:-1],
                        openning_hours=shop_openning_hours,
                        phone=shop_phone
                    ))
                    dbsession.commit()
    except Exception as e:
        print('{},{}'.format(params, e))


async def get_pos_shops(latlng_id, latlng, city):
    semaphore = asyncio.Semaphore(4)
    with (await semaphore):
        lat_lng = latlng.split(',')
        params = {
            'latitude': lat_lng[0],
            'longitude': lat_lng[1],
            'offset': 0,
            'limit': 10,
            'terminal': 'h5',
            'order_by': 6,
        }
        await get_shops(city, params, latlng_id, latlng)


def get_city_shops():
    # 协程
    event_loop = asyncio.get_event_loop()
    tasks = [
        get_pos_shops(latlng_id, latlng, city)
        for latlng_id, latlng, city in dbsession.query(Latlng.id, Latlng.lat_lng, Latlng.city)
    ]
    event_loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == '__main__':
    get_city_shops()
    # 关闭Session
    dbsession.close()
