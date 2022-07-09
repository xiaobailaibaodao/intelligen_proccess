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


    def set_operation_process_time(self,instance,mached_machine,operation,assigned_product,assigned_machine,prop_id,chrom,assigned_route_no):
        '''
        :param instance: 基础数据
        :param mached_machine: 当前工序匹配机器
        :param operation: 当前工序
        :param assigned_product: 已分配产品id-route_no
        :param assigned_machine: 每个机器分配处理工序情况
        :param prop_id: 产品id + '-' + route_id
        :param chrom: 染色体
        :param assigned_route_no: 记录已分配prop_id
        :return:
        '''

        # 更新工序加工时间 (区分工序B、非工序B)
        # 赋值每个工序公式时间区间
        special_option = False
        if operation.name == '工序B':
            process_time = operation.get_process_time(self.instance.product_dict[product_no].product_num)
            special_option = True
        else:
            process_time = operation.get_process_time(self.instance.product_dict[product_no].product_num)

        # 更新加工时间
        if special_option and self.check_if_add_ready_time(operation, product_no, special_option, mached_machine,assigned_product, assigned_machine):
            ready_time_list = re.findall(r'\d+\.?\d*', operation.ready_time)
            process_time = process_time + float(ready_time_list[0]) * 60
