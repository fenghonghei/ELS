import json
import asyncio
import aiohttp

from core.db_engine import dbsession, Shop

CITY_LATLNG_PATH = '../dependence/city_latlng.json'
SHOP_URL = 'https://h5.ele.me/restapi/shopping/v3/restaurants'


async def get_shops(city, params):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SHOP_URL, params=params) as response:
                data = await response.text()
                restaurant__json = json.loads(data)
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
                        flavors=shop_flavor_ids[:-1],
                        openning_hours=shop_openning_hours,
                        phone=shop_phone
                    ))
                    dbsession.commit()
    except Exception as e:
        print('{},{}'.format(params, e))


async def get_pos_shops(city, latlng):
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
        await get_shops(city, params)


def get_poses(city):
    with open(CITY_LATLNG_PATH, 'r') as f:
        city_latlngs = json.load(f)
        return city_latlngs[city]


def get_city_shops(city):
    city_latlngs = get_poses(city)
    # 协程
    event_loop = asyncio.get_event_loop()
    tasks = [get_pos_shops(city, latlng) for latlng in city_latlngs]
    event_loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == '__main__':
    # 获取当前城市的店铺数据并写入数据库
    get_city_shops('武汉')
    # 关闭Session
    dbsession.close()
