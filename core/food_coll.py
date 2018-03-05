import asyncio
import json

import aiohttp

import core.ip_coll as ip_coll
from core.db_engine import dbsession, Shop, Food, Record, FoodConcept

FOOD_URL = 'https://h5.ele.me/restapi/shopping/v2/menu'

semaphore = asyncio.Semaphore(2)


class FoodClassifier:
    def __init__(self):
        self.__concepts = dbsession.query(FoodConcept).all()

    def classify_food(self, food_name):
        for concept in self.__concepts:
            for word in concept.key_words.split(','):
                if word in food_name:
                    return concept.id
        return -1


async def get_foods(session, shop_id, ip):
    with (await semaphore):
        params = {'restaurant_id': shop_id}
        print('剩余店铺量： {}'.format(len(shop_ids)))
        headers = {
            r'Host': r'h5.ele.me',
            r'Connection': r'keep-alive',
            r'User-Agent': r'Mozilla/5.0 (Linux; U; Android 5.1; zh-CN; MZ-m2 note Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/40.0.2214.89 MZBrowser/6.10.2 UWS/2.11.0.33 Mobile Safari/537.36',
            r'x-shard': r'shopid={};loc=114.273573,30.590624'.format(shop_id),
            r'Accept': r'*/*',
            r'Referer': r'https://h5.ele.me/shop/',
            r'Accept-Encoding': r'gzip, deflate, br',
            r'Accept-Language': r'zh-CN,en-US;q=0.8',
            r'Cookie': r'ubt_ssid=nbouvov5sdvl4nbniquai795jrvi0vub_2018-02-27; perf_ssid=rn3toaudzil6ti5ru0y7hzq2dvbaipv5_2018-02-27; _utrace=a1d39d357cd6f361e1d3c461f7cfc236_2018-02-27',
        }
        try:
            async with session.get(FOOD_URL, headers=headers, params=params, proxy=ip, timeout=10) as response:
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
                        class_id = food_classifer.classify_food(food_name)
                        old_food = dbsession.query(Food).filter(Food.id == food_id).first()
                        if old_food and old_food.recent_popularity != recent_popularity:
                            dbsession.add(Record(
                                food_id=food_id,
                                food=food_name,
                                price=price,
                                concept_ids=str(class_id),
                                old_popularity=old_food.recent_popularity,
                                new_popularity=recent_popularity,
                            ))
                        dbsession.merge(Food(
                            id=food_id,
                            name=food_name,
                            shop_id=shop_id,
                            price=price,
                            concept_ids=str(class_id),
                            recent_popularity=recent_popularity
                        ))
                        try:
                            dbsession.commit()
                        except:
                            dbsession.rollback()
                if len(src_foods):
                    shop_ids.remove(shop_id)
                    with open('shops.txt', 'at') as f:
                        f.writelines(str(shop_id) + '\n')
                else:
                    print('********fail*********')
        except Exception as e:
            print('{},{}'.format(shop_id, e))


async def creat_session(ip):
    async with aiohttp.ClientSession() as session:
        tmp_sids = [sid for sid in shop_ids]
        tasks = [get_foods(session, sid, ip) for sid in tmp_sids]
        await asyncio.gather(*tasks)


async def start_batch_coll(ip):
    print('开始新批次')
    task = asyncio.ensure_future(creat_session(ip))
    await task


def main():
    # 创建分类器
    global food_classifer
    food_classifer = FoodClassifier()

    event_loop = asyncio.get_event_loop()

    global shop_ids
    shop_ids = [t[0] for t in dbsession.query(Shop.id)]
    # ips = ip_coll.get_success_ips()
    # ips.insert(0, None)
    # ix = 0
    while len(shop_ids) > 0:
        # ip = ips[ix % len(shop_ids)]
        event_loop.run_until_complete(start_batch_coll(None))
        # ix += 1
    dbsession.close()
