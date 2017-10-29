#encoding:utf8
__author__="jinjun"

import csv
import matplotlib.pyplot as plt
import copy
from collections import OrderedDict
import cPickle as pickle
# import pickle
import random
import config

def shop_priceshow(data):

    price = {}
    for cont in data:
        tmp_price = int(data[cont]['price'])
        if tmp_price not in price:
            price[tmp_price] = 1
        else:
            price[tmp_price] += 1

    result = sorted(price.items(), key=lambda x: x[0])
    print(result)
    print(price[24])
    plt.plot(price.keys(), price.values())
    plt.show()

def usershow(datauser, datashop):
    shop = {}
    for cont in datashop:
        tmp_shop = datashop[cont]['shop_id']
        if tmp_shop not in shop:
            shop[tmp_shop] = int(datashop[cont]['price'])
    print("usershow0")
    user = {}
    for cont in datauser:
        tmp_user = datauser[cont]['user_id']
        tmp_shop = datauser[cont]['shop_id']
        # if tmp_shop not in shop:
        #     continue

        if tmp_user not in user:
            user[tmp_user] = {}
            user[tmp_user]["num"] = 1
            user[tmp_user]['price'] = shop[tmp_shop]
        else:
            user[tmp_user]["num"] += 1
            user[tmp_user]["price"] += shop[tmp_shop]
    print("usershow1")
    price = {}
    for u in user:
        tmp_price = user[u]['price'] / user[u]['num']
        if tmp_price not in price:
            price[tmp_price] = 1
        else:
            price[tmp_price] += 1
    print("usershow2")
    result = sorted(price.items(), key=lambda x: x[0])
    print(result)
    print(price)
    plt.plot(price.keys(), price.values())
    plt.show()


#---------------------------数据转换--------------------
def readcsv(filename):
    # 读取csv文件，有去重功能
    # data是一个dict类型，cont是文件记录
    data = {}
    datalis = {} # 字典的查找效率比list高
    with open(filename, "rb") as f:
        readers = csv.reader(f)
        cont = 0
        feature = []
        for row in readers:
            if cont == 0:
                for col in row:
                    feature.append(col)
                cont += 1
            else:
                index = 0
                tmplis = ""
                tmpdata = {}
                for col in row:
                    tmpdata[feature[index]] = col
                    tmplis += " "+col
                    index += 1
                # print(tmplis,datalis)
                # input()
                if tmplis not in datalis:
                    datalis[copy.deepcopy(tmplis)] = 1
                    data[cont] = copy.deepcopy(tmpdata)
                    cont += 1

    os = open("../data/"+filename[0:-4]+".pkl", "wb")
    pickle.dump(data, os, True)
    os.close()
    return data

def openpkl(filename):
    # 打开pkl文件
    os = open(filename, "rb")
    data = pickle.load(os)
    os.close()
    return data


def createtrain(datauser, datashop):
    shop = dict()
    for cont in datashop:
        tmp_shopid = datashop[cont]["shop_id"]
        tmp_mailid = datashop[cont]["mall_id"]

        if tmp_shopid not in shop:
            shop[tmp_shopid] = tmp_mailid

    for cont in datauser:
        tmp_shopid = datauser[cont]["shop_id"]
        datauser[cont]["maill_id"] = shop[tmp_shopid]

    contlis = random.sample(datauser.keys(), int(len(datauser.keys())/5))
    condic = {}
    for cont in contlis:
        condic[cont] = 1
    print(contlis)
    print(len(contlis), len(datauser.keys()))
    data_train = {}
    data_test = {}
    for cont in datauser:
        if cont not in condic:
            data_test[cont] = datauser[cont]
        else:
            data_train[cont] = datauser[cont]

    os = open("../data/train_train.pkl", "wb")
    pickle.dump(data_train, os, True)
    os.close()

    os = open("../data/train_test.pkl", "wb")
    pickle.dump(data_test, os, True)
    os.close()
    pass


def randomcreatedata():
    datashop = openpkl(config.trainshopinfo)
    datauser = openpkl(config.trainuserinfo)

    createtrain(datauser, datashop)


def readdata():
    datatrain = openpkl(config.traindata)
    datatest = openpkl(config.testdata)
    return datatrain, datatest


if __name__=="__main__":
    # ..\data\train-ccf_first_round_user_shop_behavior.csv
    # ..\data\ABtest-evaluation_public.csv
    # ..\data\train-ccf_first_round_shop_info.csv
    print("111111111111111")
    filenameshop = r"..\data\train-ccf_first_round_shop_info.csv"
    datashop = readcsv(filenameshop)
    print("222222222222222")
    shop_priceshow(datashop)
    filenameuser = r"..\data\train-ccf_first_round_user_shop_behavior.csv"
    datauser = readcsv(filenameuser)
    print("3333333333333333")
    usershow(datauser, datashop)

    pass