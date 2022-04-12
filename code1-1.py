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
import calendar

edge_options = EdgeOptions()
edge_options.use_chromium = True
edge_options.add_argument('--disable-blink-features=AutomationControlled')
browser = Edge(executable_path='msedgedriver.exe', options=edge_options)


def get_page(url):
    browser.get(url)
    windows = browser.window_handles
    time.sleep(2)
    if len(windows) > 1:
        browser.close()
    html = browser.page_source
    day_data = get_table_data(html)
    return day_data


def get_table_data(html):
    all_data = []
    df = pd.read_html(html)
    data = df[0].to_json(orient='table', force_ascii=False)
    data = json.loads(data)
    all_data += data['data']
    return all_data


def tidy_db(data):
    d = []
    category = ''
    date = ''
    for i in data:
        if "日期" in i['0']:
            try:
                category = i['0'].split('  ')[0].split('：')[1]
                date = i['0'].split('  ')[1].split('：')[1]
            except:
                category = i['0'].split(' ')[0].split('：')[1]
                date = i['0'].split(' ')[1].split('：')[1]
        elif i['0'] in ['名次', '合计']:
            continue
        else:
            item = [category, date]
            i.pop('index')
            item += i.values()
            d.append(item)
    df = pd.DataFrame(data=d,
                       columns=['品种/合约', '日期', '名次', '会员简称', '成交量（手）', '增减量', '会员简称', '持买仓量', '增减量', '会员简称', '持卖仓量',
                                '增减量'])
    return df


def find_trade_day(Test_begin, Test_end):
    holiday_day = []
    trade_day = []
    while Test_begin <= Test_end:
        if is_holiday(Test_begin) or Test_begin.weekday() >= 5:
            holiday_day.append(Test_begin)
        else:
            trade_day.append(Test_begin)
        Test_begin += datetime.timedelta(days=1)
    return trade_day


def main(year):
    for m in range(1, 13):
        test_begin = datetime.date(year, m, 1)
        if m in [1, 3, 5, 7, 8, 10, 12]:
            test_end = datetime.date(year, m, 31)
        elif m in [4, 6, 9, 11]:
            test_end = datetime.date(year, m, 30)
        elif m == 2:
            if calendar.isleap(year):
                test_end = datetime.date(year, m, 29)
            else:
                test_end = datetime.date(year, m, 28)
        trading_date = find_trade_day(test_begin, test_end)
        url_list = []
        for i in trading_date:
            tmp = "http://www.czce.com.cn/cn/DFSStaticFiles/Future/" + str(year) + "/" + str(
                i.strftime('%Y%m%d')) + "/FutureDataHolding.htm"
            url_list.append(tmp)
        month_data = []
        for i in url_list:
            print(i)
            month_data_tmp = get_page(i)
            month_data_tmp_dataframe = tidy_db(month_data_tmp)
            month_data.append(month_data_tmp_dataframe)
        month_data = pd.concat(month_data)
        month_data.to_csv('month_{0}_result_data.csv'.format(m))
    browser.quit()


if __name__ == '__main__':
    year = 2021
    main(year)
