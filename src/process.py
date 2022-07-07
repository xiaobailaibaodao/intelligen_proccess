# -*- coding: utf-8 -*-
'''
Create on 2022/6/24 16:52

@author: xiachunhao

@description: 工艺流程
'''

import re

class ProcessFlow:

    def __init__(self,route_id,route_No,name,equ_type,time,unit,ready_time):
        '''
        :param route_id: 工艺路线
        :param route_No: 工序号
        :param name: 工序名称
        :param equ_type: 可使用设备类型
        :param time: 单位加工时间(时间点或区间)
        :param unit: 加工单位
        :param ready_time: 设备准备时间
        '''
        self.route_id = route_id
        self.route_no = route_No
        self.name = name
        self.equ_type = equ_type
        self.time = time
        self.process_duration = list(map(float,re.findall(r'\d+\.?\d*', self.time)))
        self.unit = unit
        self.ready_time = ready_time
        self.before_node = -1    # 前一个节点
        self.after_node = -1     # 后一个节点


    def __str__(self):
        return "工艺路线: %s, 工序号: %s, 工序名称: %s, 可使用设备类型: %s, 单位加工时间: %s, 加工单位: %s, 设备准备时间: %s" % (
            self.route_id,self.route_no,self.name,self.equ_type,self.time,self.unit,self.ready_time)


    def __lt__(self, other):
        return self.route_no < other.route_no

    # def __gt__(self, other):
    #     # 单纯与上面函数取反，不定义也可
    #     return self.route_no > other


    def get_process_time(self,product_num):
        '''
        :param product_num: 节数量
        :return: 加工时长(根据传进来节数量，可小于产品要求值)
        '''
        if self.unit == '批' and self.name == '工序B':
            return self.process_duration[0]
        if self.unit == '批' and self.name != '工序B':
            return self.process_duration[0] * 60
        return product_num*self.process_duration[0]*60
