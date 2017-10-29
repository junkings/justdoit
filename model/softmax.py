#encoding:utf8
__author__="jinjun"

import config
from algorithm import dataprocessiong as dp
import numpy as np

datatrain, data_test = dp.readdata()
# print(datatrain)
del data_test
datashop = dp.openpkl(config.trainshopinfo)
shop = dict()
lb = []
for cont in datashop:
    shop_id = datashop[cont]['shop_id']
    if shop_id not in lb:
        lb.append(shop_id)

    if shop_id not in shop:
        shop[shop_id] = {}
        shop[shop_id]["latitude"] = datashop[cont]['latitude']
        shop[shop_id]["longitude"] = datashop[cont]["longitude"]

# 特征处理
falsenum = 0
num = 0
for cont in datatrain:
    datatrain[cont]['time_stamp'] = datatrain[cont]['time_stamp'].strip(' ')[1]
    datatrain[cont]["dis"] = {}
    mindis = 10000.0
    r_shop = ""
    for shop_id in shop:

        tmp_latitude = float(shop[shop_id]['latitude']) - float(datatrain[cont]['latitude'])
        tmp_longitude = float(shop[shop_id]['longitude']) - float(datatrain[cont]['longitude'])
        dis = np.sqrt(tmp_latitude*tmp_latitude+tmp_longitude*tmp_longitude)
        datatrain[cont]["dis"][shop_id] = dis
        if mindis > dis:
            mindis = dis
            r_shop = shop_id

    if r_shop != datatrain[cont]['shop_id']:
        falsenum += 1
    num += 1

print(falsenum /num)



