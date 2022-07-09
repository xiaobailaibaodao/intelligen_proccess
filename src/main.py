# -*- coding: utf-8 -*-
'''
Create on 2022/6/24 16:22

@author: xiachunhao

@description: 程序主入口

'''

import os
import time
import pandas as pd
import numpy as np
from pre_data_process import PreProcess
from model import GA
from result import Result

def run(dir_path):
    dir_path = dir_path + '\\input\\企业数字化-数字化车间智能排产调度挑战赛公开数据\\'
    product_info = pd.read_csv(dir_path+'产品信息.csv',encoding='utf8')
    process_flow = pd.read_csv(dir_path+'工艺路线.csv',encoding='gbk')
    equ_info = pd.read_csv(dir_path+'设备信息.csv',encoding='gbk')

    instance = PreProcess(product_info,process_flow,equ_info)
    model = GA(instance)
    model.solver()

    # --------结果格式化---------
    algo_result = Result(model)
    algo_result.format_algo_best_result('../output/调度结果2.csv')
    print("success!")


if __name__ == "__main__":

    start_time = time.time()
    dir_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    run(dir_path)

    print("程序耗时: ",time.time()-start_time)
