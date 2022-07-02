# -*- coding: utf-8 -*-
'''
Create on 2022/6/24 16:53

@author: xiachunhao

@description: 设备类
'''


class Equ:

    def __init__(self,equ_name,equ_type,unit):
        '''
        :param equ_name:
        :param equ_type:
        :param unit:
        '''
        self.equ_name = equ_name
        self.equ_type = equ_type
        self.unit = unit
        self.useable = True     # 是否被占用
        self.processe_operatios = []    # 该机器被分配完成工序列表
        self.per_operation_time = {}    # 对应每个分配到该机器上工序 {工序：[开始，结束]} 时间

