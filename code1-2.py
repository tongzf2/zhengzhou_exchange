# coding: utf-8
"""
作者： tongzhifang
日期： 2022年03月26日
"""

import pandas as pd
import numpy as np

if __name__ == '__main__':
    data_tmp = []
    for m in range(1, 13):
        name = "month_{0}_result_data.csv".format(m)
        df = pd.read_csv(name, parse_dates=["日期"], index_col=["品种/合约", "日期"])
        data_tmp.append(df)
    data = pd.concat(data_tmp)
    idx = pd.IndexSlice
    MA = data.loc[idx["甲醇MA", :, :]][["会员简称", "成交量（手）"]]
    MA["成交量（手）"] = pd.to_numeric(MA["成交量（手）"])
    result = MA.groupby("会员简称").agg({"成交量（手）":'sum'})
    result = result.sort_values(by=["成交量（手）"], ascending=False)
    print("甲醇MA期货2021年总成交量最大的期货公司是{0}，总计{1}手".format(result.iloc[0].name, result.iloc[0]["成交量（手）"]))