#encoding:utf8
__author__="jinjun"

import config
from algorithm import dataprocessiong as dp
import numpy as np
import gc

datatrain, data_test = dp.readdata()
# print(datatrain)
def shopinfo():
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
    wordic = {}
    shopdic = {}
    if dlen ==None:
        dlen = -1
    else:
        print(dlen)
    limit = 0
    for cont in data:
        tmp_mallid = (data[cont].get("mall_id", False) and data[cont].get("mall_id") or data[cont].get("maill_id"))
        # 样本用例
        if tmp_mallid not in result:
            result[tmp_mallid] = {}
            result[tmp_mallid][0] = {}
            result[tmp_mallid][0]['label'] = data[cont]['shop_id']
            listwifi = data[cont]['wifi_infos'].split(';')
            for info in listwifi:
                each = info.split('|')
                result[tmp_mallid][0][each[0]] = float(each[1])
        else:
            l = len(result[tmp_mallid].keys())
            result[tmp_mallid][l] = {}
            result[tmp_mallid][l]['label'] = data[cont]['shop_id']
            listwifi = data[cont]['wifi_infos'].split(';')
            for info in listwifi:
                each = info.split('|')
                result[tmp_mallid][l][each[0]] = float(each[1])

        # 每个mall的字典
        if tmp_mallid not in wordic:
            wordic[tmp_mallid] = {}
            index = 0
            listwifi = data[cont]['wifi_infos'].split(';')
            for info in listwifi:
                each = info.split('|')
                if each[0] not in wordic[tmp_mallid].keys():
                    wordic[tmp_mallid][each[0]] = index
                    index += 1

            wordic[tmp_mallid]["num"] = index
        else:
            index  = wordic[tmp_mallid].get("num", 0)
            listwifi = data[cont]['wifi_infos'].split(';')
            for info in listwifi:
                each = info.split('|')
                if each[0] not in wordic[tmp_mallid].keys():
                    wordic[tmp_mallid][each[0]] = index
                    index += 1
            wordic[tmp_mallid]["num"] = index

        # 每个mall的类别，店铺
        if tmp_mallid not in shopdic:
            shopdic[tmp_mallid] = {}
            shopid = data[cont]['shop_id']
            shopdic[tmp_mallid][shopid] = 1
        else:
            shopid = data[cont]['shop_id']
            if shopid not in shopdic[tmp_mallid]:
                shopdic[tmp_mallid][shopid] = 1

        limit += 1
        if dlen != -1 and limit > dlen:
            break

    return result,wordic,shopdic

# 距离函数
def discal(d1, d2):
    lis = set(d1.keys()+d2.keys())
    sum = 0
    for wf in lis:
        if wf == "label" or wf == "mall_id":
            continue
        sum += pow(abs(d1.get(wf,0) - d2.get(wf,0)), 2)

    return pow(sum, 0.5)

def discos(d1, d2):
    tmp_lis = [val for val in d1 if val in d2]
    lis =set(tmp_lis)
    sum = 0
    sum1 = 0
    sum2 = 0
    for wf in lis:
        if wf == "label" or wf == "mall_id":
            continue
        sum += d1.get(wf,0) * d2.get(wf,0)

    for val in d1:
        if val == "label" or val == "mall_id":
            continue
        sum1 += pow(d1.get(val,0),2)

    for val in d2:
        if val == "label" or val == "mall_id":
            continue
        sum2 += pow(d2.get(val,0),2)

    if abs(sum1 - 0) < 0.0001 or abs(sum2 - 0) < 0.0001:
        print d1,d2
        return 0
    return sum/(pow(sum1,0.5)*pow(sum2,0.5))


def sigmod(sita, word, feature,feature_num):
    x = 0
    for f in feature:
        if f == "label":
            continue
        x += sita[word[f]]*feature[f]

    x += sita[feature_num]

    return np.exp(x)


def function_tidu(feature, word, shop, sita, feature_num):
    m = len(feature.keys())
    sum = [0 for i in xrange(feature_num)]
    for i in xrange(m):
        tmp_shopid = feature[m]['label']
        fenzi = sigmod(sita[tmp_shopid], word[tmp_shopid],feature[tmp_shopid], feature_num)
        fenmu = 0
        # for
    pass


def softmax(train_feature, wordic, shopdic):
    # train_feature  主key是mallid，每个mallid下面不同的记录
    # wordic 主key是mallid，每个mall下面，不同的特征，wifi信号
    # shopdic 主key是mallid， 每个mall下面，商店
    # 目标是对每个mall下，进行商店的多分类
    for mallid in train_feature:
        feature_num = len(wordic[mallid].keys())
        sita = {}
        # 初始化参数
        for shopid in shopdic[mallid]:
            sita[shopid] = [1 for i in xrange(feature_num+1)]
        # 参数迭代
        for i in xrange(100000):
            sita_tmp = function_tidu(train_feature[mallid], wordic[mallid], shopdic[mallid],sita, feature_num)
            print(sita, sita_tmp)
            sita = sita_tmp

        print train_feature[cont]
        print wordic[cont]
        print shopdic[cont]
        input()

# wifi = sumdic(datatrain)
train_feature, wordic, shopdic = featrue_processing(datatrain, len(datatrain.keys()))
# print train_feature
softmax(train_feature,wordic,shopdic)
# del datatrain
# gc.collect()
# test_feature = featrue_processing(data_test, len(data_test.keys())/40)
# print("============================================")
# del data_test

def get_badcase(train_feature, test_feature):
    falsenum = 0
    num = 0

    for cont_test in test_feature:
        mb_shop = ["","",""]
        mb_dis = [0,0,0]
        mb_cont = [0,0,0]
        for cont_train in train_feature:
            if test_feature[cont_test]["mall_id"] != train_feature[cont_train]["mall_id"]:
                continue
            dis = discos(train_feature[cont_train],test_feature[cont_test])
            tmp_dis= min(mb_dis)
            if dis > tmp_dis:
                index = 0
                for d in mb_dis:
                    if abs(d-tmp_dis) < 0.0001:
                        mb_dis[index] = dis
                        mb_cont[index] = cont_train
                        mb_shop[index] = train_feature[cont_train]['label']
                        break
                    index += 1
        # print mb_shop, test_feature[cont_test]['label']
        # input()
        min_dis = max(mb_dis)
        index = 0
        for d in mb_dis:
            if abs(d - min_dis) < 0.0001:
                break
            index += 1
        if mb_shop[index] != test_feature[cont_test]['label']:
            print(mb_dis)
            print(train_feature[mb_cont[0]])
            print(train_feature[mb_cont[1]])
            print(train_feature[mb_cont[2]])
            print(test_feature[cont_test])
            input()
            falsenum += 1
        num += 1

    print(float(falsenum) /num)

def getaccury(train_feature, test_feature):
    falsenum = 0
    num = 0

    for cont_test in test_feature:
        mb_shop = ""
        mb_dis = 0.0
        mb_cont = 0
        for cont_train in train_feature:
            if test_feature[cont_test]["mall_id"] != train_feature[cont_train]["mall_id"]:
                continue
            # dis = discal(train_feature[cont_train], test_feature[cont_test])
            dis = discos(train_feature[cont_train], test_feature[cont_test])
            if dis > mb_dis:
                mb_dis = dis
                mb_cont = cont_train
                mb_shop = train_feature[cont_train]['label']

        # print mb_shop, test_feature[cont_test]['label']
        # input()

        if mb_shop != test_feature[cont_test]['label']:
            falsenum += 1
        num += 1

    print(float(falsenum) / num)


# get_badcase(train_feature, test_feature)
