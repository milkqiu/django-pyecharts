from django.shortcuts import render

# Create your views here.
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
from django.http import HttpResponse

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./demo/templates"))

from pyecharts import options as opts
from pyecharts.charts import Bar


import numpy as np
import pandas as pd
from pyecharts.charts import Bar,Map,Page,Pie,WordCloud
from pyecharts import options as opts

def get_data():
    user_info = pd.read_excel('E:\\用户分群\\user.xlsx',dtype={'kedou_id':'str'})
    # order_info = pd.read_excel('E:\\用户分群\\order.xlsx', dtype={'kedou_id':'str'})
    # dispatch1 = pd.read_excel('E:\\用户分群\\dispatch1.xlsx',dtype={'kedou_id':'str'})
    # dispatch2 = pd.read_excel('E:\\用户分群\\dispatch2.xlsx', dtype={'kedou_id': 'str'})
    # dispatch_info = pd.concat([dispatch1,dispatch2],axis=0)
    user_province = pd.read_excel('E:\\用户分群\\user_information.xlsx')
    return user_info,user_province

# 筛选条件获得云电脑数据
def get_yun_computer_info(user_info):
    yun_computer_user_info = user_info[
        (user_info['buss_line'] == 0) & (user_info['scene'].isin([1, 4])) & (user_info['enterprise_id'] == 5)]
    yun_computer_user_info['date'] = pd.to_datetime(yun_computer_user_info['add_time']).dt.date
    yun_computer_user_info['month'] = yun_computer_user_info['add_time'].astype('datetime64[M]')

    # yun_computer_order_info = order_info[
    #     (order_info['buss_line'] == 0) & (order_info['scene'].isin([1, 4])) & (order_info['enterprise_id'] == 5) & (
    #         order_info['state'].isin([1, 5]))]
    # yun_computer_order_info['date'] = pd.to_datetime(yun_computer_order_info['add_time']).dt.date
    # yun_computer_order_info['month'] = yun_computer_order_info['add_time'].astype('datetime64[M]')
    #
    # yun_computer_dispatch_info = dispatch_info[
    #     (dispatch_info['buss_line'] == 0) & dispatch_info['scene'].isin([1, 4]) & (
    #                 dispatch_info['enterprise_id'] == 5) & (dispatch_info['user_type'].isin([0, 1]))]
    # yun_computer_dispatch_info['date'] = pd.to_datetime(yun_computer_dispatch_info['end_time']).dt.date
    # yun_computer_dispatch_info['month'] = yun_computer_dispatch_info['end_time'].astype('datetime64[M]')

    return yun_computer_user_info



def get_user_bar(yun_computer_user_info):
    user_cnt = yun_computer_user_info.groupby(['date']).agg(user_cnt=('kedou_id','nunique'))[-30::]
    bar = (
        Bar()
        .add_xaxis(user_cnt.index.tolist())
        .add_yaxis('按天',user_cnt.user_cnt.tolist())
        .set_global_opts(title_opts=opts.TitleOpts(title="新增用户分布情况（按天数）",pos_left='right'),
                         xaxis_opts=opts.AxisOpts(
                             name='日期',
                             name_textstyle_opts=opts.TextStyleOpts(
                                 font_size=12
                             )
                         ))
    )
    return bar

def get_map(user_province):
    user_province_cnt = user_province.groupby('省份').agg(user_cnt=('user_id','nunique'))
    map = (
        Map()
        .add("人口分布数据地图", [list(i) for i in zip(user_province_cnt.index.tolist(),user_province_cnt.user_cnt.tolist())], "china")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="人口分布"),
            visualmap_opts=opts.VisualMapOpts(max_=max(user_province_cnt.user_cnt.tolist()), min_=min(user_province_cnt.user_cnt.tolist())),
        )
    )
    return map

def get_education_pie(user_province):
    user_education_cnt = user_province.groupby('education').agg(user_cnt=('user_id', 'nunique'))
    pie = (
        Pie()
        .add('教育水平',[list(i) for i in zip(user_education_cnt.index.tolist(),user_education_cnt.user_cnt.tolist())],
             radius=[100,150])
        .set_global_opts(
            title_opts = opts.TitleOpts(title='用户教育水平分布图',pos_left='center'),
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="right")
        )
    )
    return pie

def get_profession_pie(user_province):
    user_profession_cnt = user_province.groupby('profession').agg(user_cnt=('user_id', 'nunique'))
    pie1 = (
        Pie()
        .add('职业',[list(i) for i in zip(user_profession_cnt.index.tolist(),user_profession_cnt.user_cnt.tolist())])
        .set_global_opts(
            title_opts = opts.TitleOpts(title='用户职业分布图',pos_left='center'),
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="left")
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}%"))
    )
    return pie1

def get_game_prefer_ciyun(user_province):
    game_prefer = pd.concat([user_province['游戏类型1'],user_province['游戏类型1'],user_province['游戏类型1']]).dropna(axis=0)
    game_prefer_df=game_prefer.value_counts()
    wordcloud = (
        WordCloud()
        .add('游戏类型偏好',[list(i) for i in zip(game_prefer_df.index.tolist(),game_prefer_df.tolist())])
        .set_global_opts(title_opts=opts.TitleOpts(title="WordCloud-用户游戏类型偏好"))
    )
    return wordcloud



def index(request):
    user_info, user_province = get_data()
    yun_computer_user_info = get_yun_computer_info(user_info)
    bar = get_user_bar(yun_computer_user_info)
    map = get_map(user_province)
    page = Page(layout=Page.DraggablePageLayout)
    pie = get_education_pie(user_province)
    pie1 = get_profession_pie(user_province)
    wordcloud = get_game_prefer_ciyun(user_province)
    page.add(bar, map, pie, pie1, wordcloud)
    return HttpResponse(page.render_embed())