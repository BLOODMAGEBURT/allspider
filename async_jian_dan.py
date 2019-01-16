# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import logging
import base64
from contextlib import closing
import os
import aiohttp
import asyncio
"""
-------------------------------------------------
   File Name：     async_jian_dan
   Description :
   Author :       burt
   date：          2019-01-16
-------------------------------------------------
   Change Activity:
                   2019-01-16:
-------------------------------------------------
"""
logging.basicConfig(level=logging.INFO)

target_url = r'http://jandan.net/ooxx/page-%s'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    'Host': 'jandan.net',
    'Referer': 'http://jandan.net/top'
}


def download_one_page(page):
    req = requests.get(url=target_url % str(page), headers=headers)
    # print(req.text)
    if req.status_code == 200:
        html = req.text
        # print(html)
        # 'ol > li > div > div > div.text > p > span.img-hash'
        bs = BeautifulSoup(html, features='html.parser')
        span_ls = bs.select('div.text > p > span.img-hash')
        # print(span_ls)
        # logging.info(type(span_ls[0]))
        hash_ls = ['http:' + str(base64.b64decode(hash_img.string), encoding='utf-8') for hash_img in span_ls]
        print(hash_ls)
        # logging.info(type(hash_ls[0]))
        # logging.info(len(hash_ls[0]))
        # download images

        # in a sync way
        # for img_url in hash_ls:
        #     # if exits
        #     if not os.path.exists('%s' % img_url[-10:]):
        #         logging.info('download new img ……')
        #         with closing(requests.get(url=img_url, stream=True)) as res:
        #             with open('%s' % img_url[-10:], 'wb') as f:
        #                 for chunk in res.iter_content(1024):
        #                     if chunk:
        #                         f.write(chunk)
        #     else:
        #         logging.info('already have it,do not need to download anymore')

        # in a async way
        tasks = [async_get_img(img_url) for img_url in hash_ls]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))


async def async_get_img(image_url):
    async with aiohttp.ClientSession() as session:
        # if exits
        logging.info('downloading new img')
        if not os.path.exists('%s' % image_url[-10:]):
            async with session.get(image_url) as resp:
                assert resp.status == 200
                with open('%s' % image_url[-10:], 'wb') as fb:
                    while True:
                        chunk = await resp.content.read(10)
                        if not chunk:
                            break
                        fb.write(chunk)
        else:
            logging.info('already have it,do not need to download anymore')


if __name__ == '__main__':
    logging.info('start to download the img')
    for page_num in [35, 34, 33]:
        download_one_page(page_num)
    logging.info('all the images have been downloaded')