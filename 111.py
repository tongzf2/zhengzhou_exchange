# coding: utf-8
"""
作者： tongzhifang
日期： 2022年03月25日
"""

import json
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
import time
import pandas as pd
import datetime
from chinese_calendar import is_holiday

edge_options = EdgeOptions()
edge_options.use_chromium = True
edge_options.add_argument('--disable-blink-features=AutomationControlled')
browser = Edge(executable_path='msedgedriver.exe', options=edge_options)

all_data = []


def get_page(url):
    browser.get(url)
    windows = browser.window_handles
    time.sleep(2)
    if len(windows) > 1:
        browser.close()
    html = browser.page_source
    get_table_data(html)


def get_table_data(html):
    global all_data
    df = pd.read_html(html)
    data = df[0].to_json(orient='table', force_ascii=False)
    data = json.loads(data)
    all_data += data['data']


def save_db(data):
    d = []
    category = ''
    date = ''
    for i in data:
        if "日期" in i['0']:
            category = i['0'].split('  ')[0].split('：')[1]
            date = i['0'].split('  ')[1].split('：')[1]
        elif i['0'] in ['名次', '合计']:
            continue
        else:
            item = [category, date]
            i.pop('index')
            item += i.values()
            d.append(item)
    df2 = pd.DataFrame(data=d,
                       columns=['品种/合约', '日期', '名次', '会员简称', '成交量（手）', '增减量', '会员简称', '持买仓量', '增减量', '会员简称', '持卖仓量',
                                '增减量'])
    df2.to_csv('result_data.csv')


def find_trade_day(Test_begin, Test_end):
    holiday_day = []
    trade_day = []
    while Test_begin <= Test_end:
        if is_holiday(Test_begin) or Test_begin.weekday() > 5:
            holiday_day.append(Test_begin)
        else:
            trade_day.append(Test_begin)
        Test_begin += datetime.timedelta(days=1)
    return trade_day


def main(year):
    Test_begin = datetime.date(year, 1, 1)
    Test_end = datetime.date(year, 6, 31)
    Trading_Date = find_trade_day(Test_begin, Test_end)
    url_list = []
    for i in Trading_Date:
        tmp = "http://www.czce.com.cn/cn/DFSStaticFiles/Future/" + str(year) + "/" + str(i.strftime('%Y%m%d')) + "/FutureDataHolding.htm"
        url_list.append(tmp)
    for i in url_list:
        get_page(i)
    save_db(all_data)
    browser.quit()


if __name__ == '__main__':
    year = 2021
    main(year)
    print("hello world")