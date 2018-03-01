import asyncio
import re

import aiohttp
import chardet
import requests

FOOD_URL = 'https://h5.ele.me/restapi/shopping/v2/menu'

HEADERS = {
    'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
}


def get_ip_list(url):
    html = requests.get(url, headers=HEADERS).content
    html = html.decode(chardet.detect(html)['encoding'])
    pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}'
    return re.findall(pattern, html)


async def ip_test(proxy, success_ips):
    try:
        async with aiohttp.ClientSession() as session:
            proxy = 'http://' + proxy
            params = {'restaurant_id': 157172045}
            async with session.get(FOOD_URL, params=params, proxy=proxy, timeout=4) as response:
                print(response.status)
                if response.status == 200:
                    success_ips.append(proxy)
    except Exception:
        pass


def get_success_ips():
    ip_list = get_ip_list('http://m.66ip.cn/mo.php?tqsl={proxy_number}'.format(proxy_number=5000))
    success_ip_list = []
    event_loop = asyncio.get_event_loop()
    tasks = [ip_test(proxy, success_ip_list) for proxy in ip_list]
    event_loop.run_until_complete(asyncio.gather(*tasks))
    return success_ip_list
