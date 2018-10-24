
#  -*- coding: utf-8 -*-

"""
普量学院量化投资课程系列案例源码包
普量学院版权所有
仅用于教学目的，严禁转发和用于盈利目的，违者必究
©Plouto-Quants All Rights Reserved

普量学院助教微信：niuxiaomi3
"""

from pymongo import ASCENDING
from database import DB_CONN
from datetime import datetime, timedelta
import tushare as ts


def get_trading_dates(begin_date=None, end_date=None):
    """
    获取指定日期范围的按照正序排列的交易日列表
    如果没有指定日期范围，则获取从当期日期向前365个自然日内的所有交易日

    :param begin_date: 开始日期
    :param end_date: 结束日期
    :return: 日期列表
    """
    # 开始日期，默认今天向前的365个自然日
    now = datetime.now()
    if begin_date is None:
        one_year_ago = now - timedelta(days=365)
        begin_date = one_year_ago.strftime('%Y-%m-%d')

    # 结束日期默认为今天
    if end_date is None:
        end_date = now.strftime('%Y-%m-%d')
    
    # 下面这个方法是很好，起码是本地的，不需要联网，前提是有下载这段时间的数据
    # 因为默认下载的是2015年的，所以需要再下载2017年的数据
    daily_cursor = DB_CONN.daily.find(
        {'code': '000001', 'date': {'$gte': begin_date, '$lte': end_date}, 'index': True},
        sort=[('date', ASCENDING)],
        projection={'date': True, '_id': False})

    dates = [x['date'] for x in daily_cursor]
    
    if len(dates) == 0:
        all_trade_dates = ts.trade_cal()
        trade_dates = all_trade_dates[(all_trade_dates.isOpen == 1) & \
                                     (all_trade_dates.calendarDate >= begin_date) & \
                                     (all_trade_dates.calendarDate <= end_date)]
        dates = trade_dates.calendarDate.tolist()

    return dates


def get_all_codes(date=None):
    """
    获取某个交易日的所有股票代码列表，如果没有指定日期，则从当前日期一直向前找，直到找到有
    数据的一天，返回的即是那个交易日的股票代码列表

    :param date: 日期
    :return: 股票代码列表
    """

    datetime_obj = datetime.now()
    if date is None:
        date = datetime_obj.strftime('%Y-%m-%d')

    codes = []
    while len(codes) == 0:
        code_cursor = DB_CONN.basic.find(
            {'date': date},
            projection={'code': True, '_id': False})

        codes = [x['code'] for x in code_cursor]

        datetime_obj = datetime_obj - timedelta(days=1)
        date = datetime_obj.strftime('%Y-%m-%d')

    return codes
