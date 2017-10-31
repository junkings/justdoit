#encoding:utf8
__author__="jinjun"

import config
from algorithm import dataprocessiong as dp
import numpy as np
import gc

datatrain, data_test = dp.readdata()
# print(datatrain)
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
        shop[shop_id]['mall_id'] = datashop[cont]['mall_id']
del shop

# 特征处理
def sumdic(datatrain):
    # wifi字典 key是wifi名，value是位置
    wifi = {}
    wificont = 0
    for cont in datatrain:
        listwifi = datatrain[cont]['wifi_infos'].split(';')
        for info in listwifi:
            each = info.split('|')[0]
            if each not in wifi:
                wifi[each] = {}
                wifi[each] = wificont
                wificont += 1
    return wifi
# 特征选择 时间

def featrue_processing(data, dlen =None):
    result = {}
    if dlen ==None:
        dlen = -1
    else:
        print(dlen)
    limit = 0
    for cont in data:
        result[cont] = {}
        result[cont]['label'] = data[cont]['shop_id']
        # result[cont]['feature'] = {}
        listwifi = data[cont]['wifi_infos'].split(';')
        for info in listwifi:
            each = info.split('|')
            result[cont][each[0]] = float(each[1])

        limit += 1
        if dlen != -1 and limit > dlen:
            break

    return result

def discal(d1, d2):
    lis = list(set(d1.keys()+d2.keys()))
    sum = 0
    for wf in lis:
        if wf == "label":
            continue
        sum += pow(abs(d1.get(wf,0) - d2.get(wf,0)), 2)

    return pow(sum, 0.5)

# wifi = sumdic(datatrain)
train_feature = featrue_processing(datatrain, len(datatrain.keys()))
del datatrain
gc.collect()
test_feature = featrue_processing(data_test, len(data_test.keys())/4)
print("============================================")
falsenum = 0
num = 0
del data_test

for cont_test in test_feature:
    mb_shop = ""
    mb_dis = 1000000000
    for cont_train in train_feature:
        dis = discal(train_feature[cont_train],test_feature[cont_test])
        if dis <mb_dis:
            mb_dis = dis
            mb_shop = train_feature[cont_train]['label']

    if mb_shop != test_feature[cont_test]['label']:
        falsenum += 1
    num += 1

print(float(falsenum) /num)



