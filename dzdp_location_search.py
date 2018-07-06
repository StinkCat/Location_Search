# -*- coding: utf-8 -*-
import csv
import  time
import requests
import random
def read_file():
    csvFile = open("louyu.csv", "r")
    reader = csv.reader(csvFile)
    result = []
    for item in reader:
        if reader.line_num == 1:  # 忽略第一行
            continue
        result.append(item[1])  # 添加到列表
    return result
    csvFile.close()
s = requests.Session()
def run(N,valve):
    # print("正在尝试获取经纬度")
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"
    sa = ''
    for i in range(8):
        sa = sa + random.choice(seed)#生成随机字符串
    headers = {
        'Accept':'application/json, text/javascript',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': '',#cookie值
        'Content-Length': '287',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8;',
        'X-Request': 'JSON',
        'Origin': 'http://www.dianping.com',
        'Connection': 'keep-alive',
        'Host': 'www.dianping.com',
        'Referer': 'http://www.dianping.com/search/map/keyword/4/0_'+str(sa),
    }
    data = {
        'cityId':'4',
        'cityEnName':'guangzhou',
        'promoId':'0',
        'shopType':'',
        'categoryId':'',
        'regionId':'',
        'sortMode':'',
        'shopSortItem':'0',
        'keyword':valve,
        'searchType':'2',
        'branchGroupId':'0',
        'aroundShopId':'0',
        'shippingTypeFilterValue':'0',
        'page':'1',
    }
    url = 'http://www.dianping.com/search/map/ajax/json'
    resp = s.post(url,data=data,headers = headers)
    try:
        hopRecordBeanList = resp.json()['shopRecordBeanList'][0]
    except IndexError:
        print(str(N)+':',valve+'\t搜索为空')
        txtfile = open("./dzdp.txt", "a", encoding='utf8')
        txtfile.write(str(valve) + 'NULL\n')
        txtfile.close()
        if N%45 ==0:
            pass
            # time.sleep(120)
    except:
        print(str(N)+':', valve + '\t被防爬了，歇一会...')
        txtfile = open("./dzdp.txt", "a", encoding='utf8')
        txtfile.write(str(valve) + 'NULL\n')
        txtfile.close()
        time.sleep(5)
    else:
    # print(type(hopRecordBeanList))
        districtName = hopRecordBeanList['shopRecordBean']['districtName']
        geoLat = hopRecordBeanList['geoLat']
        geoLng = hopRecordBeanList['geoLng']
        address = hopRecordBeanList['address']
        shopName = hopRecordBeanList['shopName']
        bizRegionName = hopRecordBeanList['shopRecordBean']['bizRegionName']
        categoryName = hopRecordBeanList['shopRecordBean']['categoryName']
        print(str(N)+':',valve+':\t区域：'+str(districtName),'\t纬度：'+str(geoLat),'\t经度：'+str(geoLng),'\t地址：'+str(address),'\t商店名：'+str(shopName),'\t位置：'+str(bizRegionName),'\t主打：'+str(categoryName))
        txtfile = open("./dzdp.txt", "a", encoding='utf8')
        txtfile.write(str(valve) + '\t' + str(districtName) + '\t'+str(geoLng) + '\t' + str(geoLat) + '\t'+str(address) + '\t' + str(shopName) + '\t'+str(bizRegionName) + '\t' + str(categoryName) + '\n')
        txtfile.close()
        if N % 45 == 0:
            pass
            # time.sleep(60)
        N += 1
    # print(address)
def main():
    lyname = read_file()
    N = 1
    for vavle in lyname:
        run(N , vavle)
        N += 1
        time.sleep(random.randint(1, 2))#不能快过1秒，会被封IP
if __name__ == '__main__':
    main()
