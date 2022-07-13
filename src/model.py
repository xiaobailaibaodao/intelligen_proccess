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
        self.best_assigned_route_no = []    # 存储最优解计划
        self.best_assigned_product = {}
        self.best_assigned_machine = {}

        self.population_size = 1
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

        self.update_efficiency_value()
        print("初始解目标函数值: ",self.best_obj)


    def algo_to_best_solution(self):
        # 迭代策略进行搜索
        pass


    def update_efficiency_value(self):
        # 更新计划方案评价指标
        for chrom in self.population:
            assigned_route_no = []  # 已经安排的工序id 集合
            assigned_product = {}  # 记录每个安排工序 开始结束时间 以及机器设备信息 {产品id-工序id: [s,e,equ_name]}
            assigned_machine = {}  # 记录机器已经安排工序  {equ_name:[产品id-工序id....] }
            c_process_time, finish_time = self.decoding_MSOS(chrom,assigned_route_no,assigned_product,assigned_machine)
            eval_cost = c_process_time / finish_time
            if eval_cost > self.best_obj:
                self.best_obj = eval_cost
                self.best_chrom = chrom
                self.best_assigned_route_no = assigned_route_no
                self.best_assigned_product = assigned_product
                self.best_assigned_machine = assigned_machine
        print("解析种群染色体完成")


    def decoding_MSOS(self,chrom,assigned_route_no,assigned_product,assigned_machine):
        # decoding msos chromosome to a feasible and active schedule
        while len(assigned_route_no) < len(chrom[1]):
            for i in range(len(chrom[1])):
                product,route_no = chrom[1][i].split('-')
                if chrom[1][i] in assigned_route_no:
                    continue

                operation = self.instance.process_flow_dict[self.instance.product_dict[product].route_id][int(route_no)-1]
                if operation.before_node == -1 or (product + '-' + str(operation.before_node)) in assigned_route_no:
                    # precedence node assigned
                    mached_machine = self.instance.equ_dict[operation.equ_type][chrom[0][i]-1]
                    # 更新数据
                    assigned_route_no.append(chrom[1][i])
                    assigned_product[chrom[1][i]] = [-1,-1,mached_machine.equ_name]
                    assigned_machine.setdefault(mached_machine.equ_name,[]).append(chrom[1][i])

                    # 决策该工序加工时间
                    # self.set_start_process_time(mached_machine,operation,product,assigned_product,assigned_machine,chrom[1][i],chrom,assigned_route_no)
                    operation.set_operation_process_time(self.instance,mached_machine,operation,assigned_product,assigned_machine,product + '-' + str(operation.route_no),chrom,assigned_route_no)

        # 加入工序B准备时间


        # 计算全部机器最长加工时间,以及工序C在对应设备上的 累计 加工时间
        finish_time = -1
        c_process_time = 0
        for o in assigned_product:
            p,op = o.split('-')
            if self.instance.process_flow_dict[self.instance.product_dict[p].route_id][int(op)-1].name == '工序C':
                pr_time = assigned_product[o][1] - assigned_product[o][0]
                c_process_time += pr_time

            if finish_time == -1:
                finish_time = assigned_product[o][1]
                continue
            if finish_time > assigned_product[o][1]:
                finish_time = assigned_product[o][1]

        return c_process_time,finish_time


    # todo 另一种思路解码尝试


if __name__ == "__main__":
    d = {"1": [100, 2, "3"], "5": [11, 22, "33"], "6": [8, 10, "4"]}
    print("排序前: ",d)
    sort_d = sorted(d.items(),key=lambda x:x[1][0])
    print("排序后: ",sort_d)

    print(d["1"][:-1])


