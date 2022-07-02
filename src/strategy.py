# -*- coding: utf-8 -*-
'''
Create on 2022/6/28 17:42

@author: xiachunhao

@description: 策略集合
'''
import random


class Strategy:

    def __init__(self):
        pass


    @classmethod
    def global_selection_init(cls,instance,process_time_list,machine_select,operatio_select):
        print("global select machine")
        job_list = instance.unassign_product
        for id in job_list:
            product_obj = instance.product_dict[id]
            for operation in instance.process_flow_dict[product_obj.route_id]:      # 按照工艺顺序计划，不会违背优先级
                operation_available_machines = instance.equ_dict[operation.equ_type]
                # find shortest time process machine



    @classmethod
    def local_selection_init(cls,instance,process_time_list,machine_select,operatio_select):
        print("local select machine")
        job_list = instance.unassign_product
        for id in job_list:
            process_time_list = [0]*len(process_time_list)     # 每个job前都置空


    @classmethod
    def random_selection_init(cls,instance,process_time_list,machine_select,operatio_select):
        print("random select machine")
        job_list = instance.unassign_product
        i = 0    # 工序 匹配 机器 的索引对应
        random.shuffle(job_list)    # 1.随机选择job安排
        for id in job_list:
            product_obj = instance.product_dict[id]
            for operation in instance.process_flow_dict[product_obj.route_id]:  # 按照工艺顺序计划，不会违背优先级
                operatio_select[i] = id        # 同一产品，按照工艺流程顺序安排
                operation_available_machines = instance.equ_dict[operation.equ_type]
                # find shortest time process machine
                machine_id = random.randint(1,len(operation_available_machines)+1)    # 随机选择,记得 减一取值
                machine_select[i] = machine_id
                i += 1



    @classmethod
    def select_shortest_machine(cls,available_machine_list,operation,process_time_list):
        '''
        :param available_machine_list: 工序对应可用机器列表
        :param operation: 工序对象
        :return: 增加加工时长最短的机器 所在 列表中索引位置
        '''
        # todo 1.由于同种设备类型对应机器设备处理时长一样(工序B特殊性后续调整)
        # todo 2.考虑设备负载均衡，后面可以优化一下设备初始化分配； 通过记录每个设备处理工序问题
        # 增加一个设备属性 或者 一个列表用来记录每种设备分配工序情况，选出最短用时
        return random.randint(1,len(available_machine_list)+1)

