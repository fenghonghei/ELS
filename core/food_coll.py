import json
import asyncio
import aiohttp

from core.db_engine import dbsession, Shop, Food, Record

FOOD_URL = 'https://h5.ele.me/restapi/shopping/v2/menu'


async def get_foods(shop_id):
    semaphore = asyncio.Semaphore(4)
    params = {'restaurant_id': shop_id}
    with (await semaphore):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(FOOD_URL, params=params) as response:
                    data = await response.text()
                    src_foods = json.loads(data)
                    for src_food in src_foods:
                        src_items = src_food['foods']
                        for src_item in src_items:
                            food_id = src_item['specfoods'][0]['food_id']
                            food_name = src_item['specfoods'][0]['name']
                            original_price = src_item['specfoods'][0]['original_price']
                            price = src_item['specfoods'][0]['price']
                            if original_price is not None and price == 1:
                                price = original_price
                            recent_popularity = src_item['specfoods'][0]['recent_popularity']
                            old_food = dbsession.query(Food).filter(Food.id == food_id).first()
                            if old_food and old_food.recent_popularity != recent_popularity or old_food.price != price:
                                dbsession.add(Record(
                                    food_id=food_id,
                                    old_price=old_food.price,
                                    price=price,
                                    old_popularity=old_food.recent_popularity,
                                    new_popularity=recent_popularity,

                                ))
                            dbsession.merge(Food(
                                id=food_id,
                                name=food_name,
                                shop_id=shop_id,
                                price=price,
                                recent_popularity=recent_popularity
                            ))
                            dbsession.commit()
        except Exception as e:
            print('{}店铺发生了{}'.format(shop_id, e))


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    tasks = [get_foods(shop_id_tuple[0]) for shop_id_tuple in dbsession.query(Shop.id)]
    event_loop.run_until_complete(asyncio.gather(*tasks))

    dbsession.close()
