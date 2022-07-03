# -*- coding: utf-8 -*-
'''
Create on 2022/6/28 17:37

@author: xiachunhao

@description: 算法主体GA
'''

from strategy import Strategy

import random
import re

random.seed(1)

class GA:

    def __init__(self,instance):
        self.instance = instance
        self.population = []
        self.best_chrom = []
        self.best_obj = 0
        self.population_size = 100
        self.max_iteration = 100
        self.pc = 0.7     # crossover probability
        self.pm = 0.01    # mutation probability


    def solver(self):
        # 求解
        print("开始构造初始解....")
        all_product_operations = 0
        for p in self.instance.unassign_product:
            per_job_operations = len(self.instance.process_flow_dict[self.instance.product_dict[p].route_id])
            self.instance.product_dict[p].all_operations = per_job_operations
            all_product_operations += per_job_operations
        self.init_solution(all_product_operations)
        print("初始解构造完成")


    def init_solution(self,all_product_operations):
        # initialize population with MSOS chromosome represtation
        if len(self.instance.unassign_product) <= 0:
            print("读取产品数据为空，请检查数据")
            return

        while len(self.population) < self.population_size:
            process_time_list = [0]*self.instance.equ_num
            machine_select = [0]*all_product_operations
            operation_select = [0]*all_product_operations

            # r = random.random()
            r = 1
            if r <= 0.6:
                # global selection （0.6）
                Strategy.global_selection_init(self.instance,process_time_list,machine_select,operation_select)
            elif r <= 0.9:
                # local selection （0.3）
                Strategy.local_selection_init(self.instance,process_time_list,machine_select,operation_select)
            else:
                # random selection （0.1）
                Strategy.random_selection_init(self.instance,process_time_list,machine_select,operation_select)
            self.population.append([machine_select,operation_select])



    def algo_to_best_solution(self):
        # 迭代策略进行搜索
        pass


    def update_efficiency_value(self):
        # 更新计划方案评价指标
        for chrom in self.population:
            pass


    def decoding_MSOS(self,chrom):
        # decoding msos chromosome to a feasible and active schedule
        assigned_route_no = []     # 已经安排的工艺id 集合
        while len(assigned_route_no) < len(chrom[1]):
            for i in range(len(chrom[1])):
                product,route_no = chrom[1][i].split('-')
                if chrom[1][i] in assigned_route_no:       # todo 会不会检查太多次
                    continue

                operation = self.instance.process_flow_dict[self.instance.product_dict[product].route_id][int(route_no)-1]
                if operation.before_node == -1 or (product + '-' + (operation.before_node-1)) in assigned_route_no:
                    # precedence node assigned
                    mached_machine = self.instance.equ_dict[operation.equ_type][chrom[0][i]-1]


    def set_start_process_time(self,mached_machine,operation,operation_no):
        '''
        :param mached_machine: 匹配机器设备
        :param operation: 工序
        :param operation_no: 产品+工序号
        :return:
        '''
        # 赋值每个工序公式时间区间
        time_list = re.findall(r'\d+\.?\d*', operation.time)
        if operation.name == '工序B':
            process_time = int(time_list[0])  # todo 假设都无其它因素干扰，选择最短时间

        else:
            process_time = int(time_list[0]) * 60

        # todo 考虑特殊工序B的情况
        if len(mached_machine.processe_operatios) == 0:
            mached_machine.processe_operatios.append(operation_no)
            start_time = 0
            special_operation_type = False


    def check_if_add_ready_time(self):
        # 检查是否增加工序B对应设备准备时间
        # 1.产品工序中第一次出现B
        # 2.当前产品存在多次B，当
        pass

