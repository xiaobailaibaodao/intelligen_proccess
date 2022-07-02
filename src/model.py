# -*- coding: utf-8 -*-
'''
Create on 2022/6/28 17:37

@author: xiachunhao

@description: 算法主体GA
'''

from strategy import Strategy

import random

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
        pass

