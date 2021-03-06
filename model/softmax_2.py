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
    x = 0.0
    for f in feature:
        if f == "label":
            continue
        x += sita[word[f]]*feature[f]

    x += sita[feature_num]
    # print x
    return x
    return np.exp(x)

def getloss(feature, word, shop, sita, feature_num):
    # m组数据
    m = len(feature.keys())
    # n组类别
    n = len(shop.keys())

    sum_1 = 0.0

    # 计算梯度
    for i in xrange(m):
        tmp_shopid = feature[i]['label']
        # fenzi = sigmod(sita[tmp_shopid], word,feature[i], feature_num)
        fenmu = 0.0
        if tmp_shopid not in shop:
            print tmp_shopid, shop
            input()
        # for shopid in shop:
        #     fenmu += sigmod(sita[shopid], word, feature[i], feature_num)
        W = {}
        W_m = 0.0
        for shopid in shop:
            W[shopid] = sigmod(sita[shopid], word, feature[i], feature_num)
            if W[shopid] > W_m:
                W_m = W[shopid]
        try:
            fenzi = np.exp(W[tmp_shopid] - W_m)
            for shopid in shop:
                fenmu += np.exp(W[shopid] - W_m)
        except RuntimeWarning:
            print "1111111", W[tmp_shopid], W_m
            input()
        # print fenzi, fenmu, (1-fenzi/fenmu)
        if fenmu != fenmu or abs(fenmu - 0.0) < 0.0000000000000001:
            fenzi = 0.0
            fenmu = 1.0
        # input()
        try:
            sum_1 += np.log((fenzi / fenmu))
        except RuntimeWarning:
            print fenmu, fenzi
            input()

    return -sum_1 / m

def function_tidu(feature, word, shop, sita, feature_num, a):
    # m组数据
    m = len(feature.keys())
    # n组类别
    n = len(shop.keys())

    sum_1 = {}
    for shopid in shop:
        sum_1[shopid] = [0.0 for i in xrange(feature_num + 1)]

    # 计算梯度
    for i in xrange(m):
        tmp_shopid = feature[i]['label']
        # fenzi = sigmod(sita[tmp_shopid], word,feature[i], feature_num)
        fenmu = 0.0
        if tmp_shopid not in shop:
            print tmp_shopid, shop
            input()
        # for shopid in shop:
        #     fenmu += sigmod(sita[shopid], word, feature[i], feature_num)
        W = {}
        W_m = 0.0
        for shopid in shop:
            W[shopid] = sigmod(sita[shopid], word, feature[i], feature_num)
            if W[shopid] > W_m:
                W_m = W[shopid]
        try:
            fenzi = np.exp(W[tmp_shopid] - W_m)
            for shopid in shop:
                fenmu += np.exp(W[shopid] - W_m)
        except RuntimeWarning:
            print "1111111",W[tmp_shopid], W_m
            input()
        # print fenzi, fenmu, (1-fenzi/fenmu)
        if fenmu != fenmu or abs(fenmu - 0.0) < 0.0000000000000001:
            fenzi = 0.0
            fenmu = 1.0
        # input()
        for f in feature[i]:
            if f == "label":
                continue

            sum_1[tmp_shopid][word[f]] += (1-fenzi/fenmu) * feature[i][f]
        sum_1[tmp_shopid][feature_num] += (1-fenzi/fenmu)

    for i in sum_1:
        for j in xrange(feature_num+1):
            sum_1[i][j] = - sum_1[i][j] / m

    # a = 0.01

    for i in sita:
        for j in xrange(feature_num+1):
            sita[i][j] = sita[i][j] - a* sum_1[i][j]

    return sita


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
            sita[shopid] = [0.00000001 for i in xrange(feature_num+1)]
        # 参数迭代
        print getloss(train_feature[mallid], wordic[mallid], shopdic[mallid],sita, feature_num)
        a = 0.01
        for i in xrange(1000):
            sita_tmp = function_tidu(train_feature[mallid], wordic[mallid], shopdic[mallid],sita, feature_num, a)
            sita = sita_tmp
            if i% 200 == 0:
                a = a/10
                print "diedai", i,getloss(train_feature[mallid], wordic[mallid], shopdic[mallid],sita, feature_num)

        # 最优化计算
        test = {'b_15322575': -69.0, 'b_26536694': -70.0, 'b_40839621': -50.0, 'b_15340607': -73.0, 'b_49978742': -58.0, 'label': 's_2887645', 'b_38348513': -68.0, 'b_50347535': -74.0, 'b_26487153': -68.0, 'b_39847233': -65.0, 'b_39423573': -51.0}
        result = {}
        m = 0.0
        label = ""
        os = open("sita1_tmp.pkl","wb")
        import pickle
        pickle.dump(sita, os)
        os.close()
        for shopid in shopdic[mallid]:
            result[shopid] = sigmod(sita[shopid], wordic[mallid], test,feature_num)
            if result[shopid] > m:
                m = result[shopid]
                label = shopid
        print(m, label)
        input()

# wifi = sumdic(datatrain)
# train_feature, wordic, shopdic = featrue_processing(datatrain, len(datatrain.keys()))
# store = {}
# store["train_feature"] = train_feature
# store["wordic"] = wordic
# store["shopdic"] = shopdic
# os = open("data.pkl", "wb")
# import pickle
# pickle.dump(store, os)
# os.close()

os = open("data.pkl", "rb")
import pickle
store = pickle.load(os)
os.close()
train_feature = store["train_feature"]
wordic = store["wordic"]
shopdic = store["shopdic"]
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
