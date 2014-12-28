#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
import json
import codecs

# 欄位
#  0食品分類(18)
#     調味料及香辛料類 堅果及種子類 加工調理食品類 肉類 澱粉類 豆類 穀物類
#     嗜好性飲料類 蛋類 油脂類 糕餅點心類 糖類 魚貝類 水果類 藻類 乳品類
#     菇類 蔬菜類
#  1資料類別(2)
#     樣品基本資料 樣品平均值
#  2整合編號(1970)
#  3樣品名稱(1969)
#  4俗名
#  5樣品英文名稱
#  6內容物描述
#  7廢棄率
#  8分析項分類(9)
#     脂肪酸組成 維生素A 維生素E 維生素B群&C 糖質分析 一般成分 水解胺基酸組成
#     其他 礦物質
#  9分析項(91)
# 10含量單位(5)
#     mg
#     I.U.
#     ug
#     g
#     kcal
# 11每100克含量
# 12樣本數
# 13標準差
# 14每單位含量
# 15每單位重
# 16每單位重含量

nutrition_class_order = [u'', u'一般成分', u'脂肪酸組成', u'維生素A', 
        u'維生素E', u'維生素B群  & C', u'糖質分析', u'水解胺基酸組成', 
        u'礦物質', u'其他']

def cmp_nutrition(x, y):
    cmp_class = cmp(nutrition_class_order.index(x['class']), 
            nutrition_class_order.index(y['class']))
    if cmp_class != 0:
        return cmp_class
    else:
        return cmp(x['name'], y['name'])


if len(sys.argv) <= 1:
    raise(Exception('not enough arguments'))

if sys.argv[1] == 'distinct':
    if len(sys.argv) <= 2:
        raise(Exception('not enough arguments for distinct'))
    col_ind = int(sys.argv[2])
    unique = set()
    with open('nutrition.csv', 'r') as f:
        csvr = csv.reader(f, delimiter="\t");
        for row in csvr:
            unique.add(row[col_ind])
    for u in unique:
        print u
    print "tot:", len(unique)
elif sys.argv[1] == 'json':
    food = {}
    nutrition_dict = {}
    nutrition_classes = set()
    count = 0
    with codecs.open('nutrition.csv', 'r', encoding='utf-8-sig') as f:
        for line in f:
            row = line.split('\t')
            category = row[0].strip()
            dtype = row[1].strip()
            name = row[3].strip()
            nutrition_class = row[8].strip()
            nutrition = row[9].strip()
            unit = row[10].strip()
            quantity = row[11].strip()
            # sktip 樣品平均值
            if dtype == u'樣品平均值':
                continue
            # skip empty quantity
            if not quantity:
                continue
            # check nutrition
            if nutrition == 'P/M/S': # ignore 脂肪酸比值
                continue
            # check quantity
            quantity = float(quantity)
            if quantity == 0.0:
                continue
            if unit == 'g':
                pass
            elif unit == 'mg':
                unit = 'g'
                quantity *= 0.001
            elif unit == 'ug':
                unit = 'g'
                quantity *= 0.000001
            # record quantity
            if not food.has_key(category):
                food[category] = {}
            if not food[category].has_key(name):
                food[category][name] = {}
            food[category][name][nutrition] = quantity
            # record nutrition
            if not nutrition_dict.has_key(nutrition):
                nutrition_dict[nutrition] = {
                        'name': nutrition, 
                        'class': nutrition_class,
                        'min': quantity,
                        'max': quantity,
                        'unit': unit
                        }
            else:
                if nutrition_dict[nutrition]['min'] > quantity:
                    nutrition_dict[nutrition]['min'] = quantity
                if nutrition_dict[nutrition]['max'] < quantity:
                    nutrition_dict[nutrition]['max'] = quantity
            # record nutrition class
            if nutrition_class not in nutrition_classes:
                nutrition_classes.add(nutrition_class)

            count += 1
        f.close()
    # print the numbers of food in each category
    for k, v in food.items():
        print k, len(v)

    # convert food to a structure appropriate for d3.js treemap
    food = {'name': u'所有食品', 'children': \
            [{'name': k, 'children': \
            [dict({'name': k2}, **v2) for k2, v2 in v.items()]\
            } for k, v in food.items()]}
    # save as json
    with codecs.open('food.json', 'w', encoding='utf-8') as f:
        json.dump(food, f, ensure_ascii=False, indent=True)
        f.close()

    # make meta data for nutritions
    nutrition_list = [v for v in nutrition_dict.values()]
    # add nutrition classes as dummy nutritions
    nutrition_list.extend({'name': None, 'class': c} 
            for c in nutrition_classes)
    nutrition_list.append({'name': u'等值', 'class': ''})
    nutrition_list.sort(cmp=cmp_nutrition)
    # save meta as json
    with codecs.open('meta.json', 'w', encoding='utf-8') as f:
        json.dump(nutrition_list, f, ensure_ascii=False, indent=True)
        f.close()
