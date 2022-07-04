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

        self.update_efficiency_value()
        print("初始解目标函数值: ",self.best_obj)


    def algo_to_best_solution(self):
        # 迭代策略进行搜索
        pass


    def update_efficiency_value(self):
        # 更新计划方案评价指标
        for chrom in self.population:
            c_process_time, finish_time = self.decoding_MSOS(chrom)
            eval_cost = c_process_time / finish_time
            if eval_cost > self.best_obj:
                self.best_obj = eval_cost
                self.best_chrom = chrom


    def decoding_MSOS(self,chrom):
        # decoding msos chromosome to a feasible and active schedule
        assigned_route_no = []     # 已经安排的工序id 集合
        assigned_product = {}      # 记录每个安排工序 开始结束时间 以及机器设备信息 {工序id: [s,e,equ_name]}
        assigned_machine = {}      # 记录机器已经安排工序  {equ_name:[工序id....] }
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
                    self.set_start_process_time(mached_machine,operation,product,assigned_product,assigned_machine,chrom[1][i])
        print("所有产品加工完成")

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


    def set_start_process_time(self,mached_machine,operation,product_no,assigned_product,assigned_machine,prop_id):
        '''
        :param mached_machine: 匹配机器设备
        :param operation: 工序
        :param product_no: 产品
        :param prop_id: 产品id + '-' + route_id
        :return:
        '''
        # 赋值每个工序公式时间区间
        time_list = re.findall(r'\d+\.?\d*', operation.time)
        special_option = False
        if operation.name == '工序B':
            process_time = int(time_list[0])  # todo 假设都无其它因素干扰，选择最短时间
            special_option = True
        else:
            # todo 工序如果是节 则需要调整计算方式
            process_time = int(time_list[0]) * 60

        # 更新加工时间
        if special_option and self.check_if_add_ready_time(operation,product_no,special_option,mached_machine,assigned_product,assigned_machine):
            ready_time_list = re.findall(r'\d+\.?\d*', operation.ready_time)
            process_time = process_time + float(ready_time_list[0])*60

        operation_start_process_time = self.decision_start_time_node(operation,product_no,mached_machine,process_time,assigned_product,assigned_machine)
        assigned_product[prop_id][0] = operation_start_process_time
        assigned_product[product_no][1] = operation_start_process_time + process_time


    def check_if_add_ready_time(self,operation,product_no,special_option,mached_machine,assigned_product,assigned_machine):
        '''
        :param operation: 当前工序对象
        :param product_no: 产品id
        :param product_first_operation: 是否第一道工序
        :return: true/false
        '''
        if special_option and operation.before_node == -1:
            return True

        # 特殊情况
        # 情况一：产品工序中第一次出现工序B
        first_b_route_no = self.instance.route_flow_first_B[self.instance.product_dict[product_no].route_id]
        if operation.route_no == first_b_route_no:
            return True

        # 情况二：当前产品存在多次工序B，且其使用机器与上一次使用机器不同(上一次处理工序B时使用机器)
        pre_b_operation = -1
        for pf in self.instance.process_flow_dict[self.instance.product_dict[product_no].route_id]:
            if pf == operation:
                break
            if pf.name == '工序B':
               pre_b_operation = pf

        if pre_b_operation == -1:
            print("检查操作有问题......")
            exit(1)
        if mached_machine.equ_name != assigned_product[product_no+'-'+pre_b_operation][2]:
            return True

        # 情况三：当前机器加工的产品与当前机器上一次加工的产品不同
        if mached_machine.equ_name in assigned_machine:
            if mached_machine.equ_name != assigned_machine[mached_machine.equ_name][-1]:
                return True

        return False


    def decision_start_time_node(self,operation,product_no,mached_machine,process_time,assigned_product,assigned_machine):

        # 1.判断当前产品工序上一工序结束时间
        if operation.before_node == -1:
            before_operation_end_time = 0
        else:
            before_operation_end_time = assigned_product[product_no+'-'+str(operation.before_node)][1]

        # 2.判断分配机器可用时间
        if mached_machine.equ_name not in assigned_machine:
            machine_end_time = before_operation_end_time
        else:
            machine_time_dict = {}
            for o in assigned_machine[mached_machine.equ_name]:
                machine_time_dict[o] = assigned_product[o]
            sort_time_machine = sorted(machine_time_dict.items(),key=lambda x:x[1][0])
            # todo 找出第一个可以插入的点,其它偏好选择有可能会变好
            end = -1
            mid_mached = False
            for s in sort_time_machine:
                if end == -1:
                    end = s[1][1]
                    continue
                if s[1][0] - end >= process_time and end >= before_operation_end_time:
                    mid_mached = True
                    machine_end_time = end
                    break
                else:
                    end = s[1][1]
            if sort_time_machine[0][1][0] >= process_time and sort_time_machine[0][1][0] - process_time >= before_operation_end_time:
                machine_end_time = before_operation_end_time
            elif mid_mached:
                # 如果都不能匹配，安排在机器最后
                machine_end_time = sort_time_machine[-1][1][1]
        return machine_end_time



if __name__ == "__main__":
    d = {"1": [100, 2, "3"], "5": [11, 22, "33"], "6": [8, 10, "4"]}
    print("排序前: ",d)
    sort_d = sorted(d.items(),key=lambda x:x[1][0])
    print("排序后: ",sort_d)



