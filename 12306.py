import requests
import os
from lxml import etree
from prettytable import PrettyTable
import re
import json
import time

if __name__ == "__main__":
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    #获取城市名称对应的编码,数据为字典形式 {城市：编码}
    name_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8971'
    name_id = requests.get(url=name_url,headers=headers).text
    name_stations = dict(re.findall(r'([\u4e00-\u9fa5]+).*?([A-Z]+)', name_id))

    #创建session()对象s获取cookie
    s = requests.session()
    s_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%E5%8C%97%E4%BA%AC,BJP&ts=%E4%B8%8A%E6%B5%B7,SHH&date=' + time.strftime('%Y-%m-%d',time.localtime()) + '&flag=N,N,Y'
    s.get(s_url)

    #输入出发地和目的地，并加入异常处理防止输入错误时程序终止
    while True:
        try:
            chufadi = name_stations[input('出发地：')]
            mudidi = name_stations[input('目的地：')]
            riqi = input('日期(yyyy-mm-dd)：')
            if len(riqi) != 10:
                continue
            break
        except:
            pass

    #车次数据的链接的组成
    url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=' + riqi + '&leftTicketDTO.from_station=' + chufadi +'&leftTicketDTO.to_station=' + mudidi +'&purpose_codes=ADULT'
    #爬取数据,提取后建立可视化表格
    response = s.get(url).text
    json_data = json.loads(response)
    # 将提取后的数据进行可视化表格,提取到的数据里城市是编号的形式，编号-城市
    # 所以将上面获取到的城市-编号的字典进行反转
    station_name = dict(zip(name_stations.values(),name_stations.keys()))
    table_list = '车次 出发站 到达站 出发时间 到达时间 历时 商务座 一等座 二等座 高级软卧 软卧 动卧 硬卧 软座 硬座 无座 其他 备注'
    tb = PrettyTable(table_list.split(' '))
    for i in json_data['data']['result']:
        name = [
            "train_code",
            "from_station_name",
            "to_station_name",
            "start_time",
            "arrive_time",
            "lishi",
            "swz",
            "first",
            "second",
            "dw",
            "gjrw",
            "rw",
            "yw",
            "rz",
            "yz",
            "wz",
            "qt",
            "note"
        ]
        # 将各项信息提取并赋值
        item = i.split('|')  # 使用“|”进行分割
        data = {
            "train_code": item[3],  # 获取车次信息，在3号位置
            "from_station_name": item[6],  # 出发站信息在6号位置
            "to_station_name": item[7],  # 终点站信息在7号位置
            "start_time": item[8],  # 出发时间在8号位置
            "arrive_time": item[9],  # 到达时间在9号位置
            "lishi": item[10],  # 经历时间在10号位置
            "swz": item[32] or item[25],  # 特别注意，商务座在32或25位置
            "first": item[31],  # 一等座信息在31号位置
            "second": item[30],  # 二等座信息在30号位置
            "gjrw": item[21],  # 高级软卧信息在21号位置
            "rw": item[23],  # 软卧/一等卧信息在23号位置
            "yw": item[28],  # 硬卧信息在28号位置
            "dw": item[27],  # 动卧信息在27号位置
            "rz": item[24],  # 软座信息在24号位置
            "yz": item[29],  # 硬座信息在29号位置
            "wz": item[26],  # 无座信息在26号位置
            "qt": item[22],  # 其他信息在22号位置
            "note": item[1],  # 备注信息在1号位置
        }
        #车次的某些信息是‘’，以防数据可视化产生异常，将其赋值‘-’
        for j in name:
            if data[j] == "":
                data[j] = "-"
        tb.add_row([data["train_code"],station_name[data["from_station_name"]],station_name[data["to_station_name"]],data["start_time"],data["arrive_time"],data["lishi"],data["swz"],data["first"],data["second"],data["gjrw"],data["rw"],data["yw"],data["dw"],data["rz"],data["yz"],data["wz"],data["qt"],data["note"]])

#打印表格
print(tb)




