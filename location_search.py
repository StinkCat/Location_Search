# -*- coding: utf-8 -*-
import  time
import csv
import requests
import math

key = '**********'  #百度地图API key
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方

def geocode(address):
    """
    利用百度geocoding服务解析地址获取位置坐标
    :param address:需要解析的地址
    :return:[province , city , district , name , lng , lat]
    """
    geocoding = {'ak': key,
                 'output':'json',
                 'region':'257', #广州
                 'city_limit': 'true',
                 'ret_coordtype':'WGS84',
                 'query': address}
    res = requests.get(
        "http://api.map.baidu.com/place/v2/suggestion", params=geocoding)
    if res.status_code == 200:
        json = res.json()
        status = json.get('status')
        result = json.get('result')
        if status == 0 and len(result) >= 1:
            geocodes = json.get('result')[0]
            province = str(geocodes.get('province')) #省份
            city = str(geocodes.get('city'))#城市
            district = str(geocodes.get('district'))#区
            name = str(geocodes.get('name')) #街道
            try:
                lng = float(geocodes.get('location').get('lng'))#经度
                lat = float(geocodes.get('location').get('lat'))#纬度
            except AttributeError:
                return None
            else:
                return [province , city , district , name , lng , lat]
        else:
            print('状态：'+str(json.get('message')))
            return None
    else:
        return None


def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)


def wgs84_to_bd09(lon, lat):
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

def main():
    csv_list = []
    try:
        csvFile = open("./location.csv", "r")
    except IOError:
        print('！读取文件错误，请检查文件是否存在！')
    else:
        reader = csv.reader(csvFile)
        for item in reader:
            if reader.line_num == 1:  # 忽略第一行
                continue
            csv_list.append(item[0])
    finally:
        csvFile.close()
    if len(csv_list) >=1:
        N = 1
        txtfile = open("./location.txt", "w", encoding='utf8')
        txtfile.write('目标地标\t省\t市\t区\t匹配地标\t百度lng\t百度lat\tGPSlng\tGPSlat\t\n')
        txtfile.close()
        for address in csv_list:
            results = geocode(address)
            time.sleep(0.2)
            txtfile = open("./location.txt", "a", encoding='utf8')
            if results == None:
                txtfile.write(address+'\tNULL')
            else:
                txtfile.write(address + '\t')
                for temp in results:
                    txtfile.write(str(temp) + '\t')
                lng,lat = bd09_to_gcj02(float(results[4]), float(results[5]))#百度转火星
                gps_lng , gps_lat = gcj02_to_wgs84(lng, lat)   #火星转GPS经纬度
                txtfile.write(str(gps_lng)+'\t'+str(gps_lat)+'\t')
            txtfile.write('\n')
            csvFile.close()
            print(N,results)
            N += 1

if __name__ == '__main__':
    main()
print("\n\n\n\n----------感谢使用-----------")
input("地标转经纬度完成，已输出txt文件")
