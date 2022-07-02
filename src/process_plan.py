# -*- coding: utf-8 -*-
'''
Create on 2022/6/28 17:22

@author: xiachunhao

@description: 计划结果
'''


class ProcessPlan:

    def __init__(self,product_id,route_No,equ_name,start,duration,end):
        '''
        :param product_id: 产品id
        :param route_No: 工艺路线
        :param equ_name: 设备
        :param start: 开始时间
        :param duration: 加工时间
        :param end: 结束时间
        '''
        self.product_id = product_id
        self.route_no = route_No
        self.equ_name = equ_name
        self.start = start
        self.duration = duration
        self.end = end




