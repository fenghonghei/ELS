import json
import asyncio
import aiohttp

from core.db_engine import dbsession, Shop, Food, Record, FoodConcept

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
                            if old_food and (old_food.recent_popularity != recent_popularity or old_food.price != price):
                                dbsession.add(Record(
                                    food_id=food_id,
                                    old_price=old_food.price,
                                    price=price,
                                    old_popularity=old_food.recent_popularity,
                                    new_popularity=recent_popularity,
                                    concept_ids='',
                                ))
                            dbsession.merge(Food(
                                id=food_id,
                                name=food_name,
                                shop_id=shop_id,
                                price=price,
                                concept_ids='',
                                recent_popularity=recent_popularity
                            ))
                            dbsession.commit()
                            return
        except Exception as e:
            print('{}店铺发生了{}'.format(shop_id, e))
            return


class FoodClassifier:
    def __init__(self):
        self.__concepts = dbsession.query(FoodConcept).all()

    def classify_food(self, food_name):
        for concept in self.__concepts:
            for word in concept.key_words.split(','):
                if word in food_name:
                    return concept.id
        return -1


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    tasks = [get_foods(shop_id_tuple[0]) for shop_id_tuple in dbsession.query(Shop.id)]
    event_loop.run_until_complete(asyncio.gather(*tasks))

    # 通过分类器生成菜品表
    ## 遍历foods
    ### 将foods的record传入分类器得到菜品id
    food_classifer = FoodClassifier()
    foods = dbsession.query(Food).all()
    for food in foods:
        class_id = food_classifer.classify_food(food.name)
        if class_id >= 0:
            dbsession.merge(Food(
                id=food.id,
                name=food.name,
                shop_id=food.shop_id,
                price=food.price,
                concept_ids=str(class_id),
                recent_popularity=food.recent_popularity
            ))
            dbsession.commit()
    dbsession.close()
