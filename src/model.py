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
            assigned_route_no = []  # 已经安排的工序id 集合
            assigned_product = {}  # 记录每个安排工序 开始结束时间 以及机器设备信息 {工序id: [s,e,equ_name]}
            assigned_machine = {}  # 记录机器已经安排工序  {equ_name:[工序id....] }
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
                    self.set_start_process_time(mached_machine,operation,product,assigned_product,assigned_machine,chrom[1][i],chrom,assigned_route_no)
        # print("所有产品加工完成")

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


    def set_start_process_time(self,mached_machine,operation,product_no,assigned_product,assigned_machine,prop_id,chrom,assigned_route_no):
        '''
        :param mached_machine: 匹配机器设备
        :param operation: 工序
        :param product_no: 产品
        :param prop_id: 产品id + '-' + route_id
        :return:
        '''
        # 赋值每个工序公式时间区间
        special_option = False
        if operation.name == '工序B':
            process_time = operation.get_process_time(self.instance.product_dict[product_no].product_num)
            special_option = True
        else:
            process_time = operation.get_process_time(self.instance.product_dict[product_no].product_num)

        # 更新加工时间
        if special_option and self.check_if_add_ready_time(operation,product_no,special_option,mached_machine,assigned_product,assigned_machine):
            ready_time_list = re.findall(r'\d+\.?\d*', operation.ready_time)
            process_time = process_time + float(ready_time_list[0])*60

        # print("当前处理工序: ",product_no+'-'+str(operation.route_no))
        operation_start_process_time = self.decision_start_time_node(operation,product_no,mached_machine,process_time,assigned_product,assigned_machine,chrom)
        if operation_start_process_time == -1:
            print("决策开始时间有问题.....")
            exit(0)

        # 如果是工序B，同时更新两个工序开始时间；否则，更新一个工序时间
        if special_option:
            next_operation = self.instance.process_flow_dict[self.instance.product_dict[product_no].route_id][operation.after_node - 1]
            next_process_time = next_operation.get_process_time(self.instance.product_dict[product_no].product_num)
            next_position = chrom[1].index(product_no+'-'+str(next_operation.route_no))
            # 选择机器
            next_mached_machine = self.instance.equ_dict[next_operation.equ_type][chrom[0][next_position]-1]
            assigned_product[product_no+'-'+str(operation.after_node)] = [operation_start_process_time+process_time,operation_start_process_time+process_time+next_process_time,next_mached_machine.equ_name]
            assigned_machine.setdefault(next_mached_machine.equ_name, []).append(product_no+'-'+str(next_operation.route_no))
            assigned_route_no.append(product_no+'-'+str(operation.after_node))

        assigned_product[prop_id][0] = operation_start_process_time
        assigned_product[prop_id][1] = operation_start_process_time + process_time


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
            # 工序中第一次出现B
            print("此工序只出现过一次工序B")
            return False

        if mached_machine.equ_name != assigned_product[product_no+'-'+str(pre_b_operation.route_no)][2]:
            return True

        # 情况三：当前机器加工的产品与当前机器上一次加工的产品不同
        if mached_machine.equ_name in assigned_machine and len(assigned_machine[mached_machine.equ_name]) >= 2:
            if mached_machine.equ_name != assigned_machine[mached_machine.equ_name][-2]:        # 最后一个是当前判断工序
                return True

        return False


    def decision_start_time_node(self,operation,product_no,mached_machine,process_time,assigned_product,assigned_machine,chrom):

        # 1.判断当前产品工序上一工序结束时间
        if operation.before_node == -1:
            before_operation_end_time = 0
        else:
            before_operation_end_time = assigned_product[product_no + '-' + str(operation.before_node)][1]

        # 2.判断分配机器可用时间
        machine_end_time = -1
        if  len(assigned_machine[mached_machine.equ_name]) == 1:   # 匹配机器只有当前工序加工计划
            machine_end_time = before_operation_end_time
        else:
            machine_time_dict = {}
            for o in assigned_machine[mached_machine.equ_name][:-1]:
                machine_time_dict[o] = assigned_product[o]
            sort_time_machine = sorted(machine_time_dict.items(),key=lambda x:x[1][0])

            end = -1
            mid_mached = False
            mid_available_position = []     # 记录 当前工序 可插入计划中执行 开始时间节点
            for s in sort_time_machine:
                if end == -1:
                    end = s[1][1]
                    continue
                if s[1][0] - end >= process_time and end >= before_operation_end_time:
                    mid_mached = True
                    machine_end_time = end
                    mid_available_position.append(machine_end_time)
                else:
                    end = s[1][1]

            # 工序B下一个工序对应机器使用情况
            next_operation_2_machine_situation = self.operation_c_machine_situation(product_no,operation,chrom,assigned_product,assigned_machine)

            # 匹配优先级(从高到低)：1.当前机器中第一个工序左边；2.中间；3.当前机器最后
            if sort_time_machine[0][1][0] >= process_time and sort_time_machine[0][1][0] - process_time >= before_operation_end_time and \
                    (next_operation_2_machine_situation == True or self.check_current_start_c(operation,before_operation_end_time,product_no,next_operation_2_machine_situation)):
                # 左边可以插入
                machine_end_time = before_operation_end_time
            elif mid_mached:
                # 中间可以插入
                for end_time in mid_available_position:
                    if next_operation_2_machine_situation == True or self.check_current_start_c(operation,end_time,product_no,next_operation_2_machine_situation):
                        return end_time
            else:
                # 如果都不能匹配，安排在机器最后
                machine_end_time = max(sort_time_machine[-1][1][1],before_operation_end_time)
                if not self.check_current_start_c(operation,machine_end_time,product_no,next_operation_2_machine_situation):
                    machine_end_time = next_operation_2_machine_situation[-1][1][1]
        return machine_end_time


    def operation_c_machine_situation(self,product_no,operation_B,chrom,assigned_product,assigned_machine):
        # 工序C对应机器使用情况
        if operation_B.name != '工序B':
            return True

        after_operation = self.instance.process_flow_dict[self.instance.product_dict[product_no].route_id][operation_B.after_node - 1]
        after_operation_str = product_no + '-' + str(operation_B.after_node)
        after_position = chrom[1].index(after_operation_str)
        after_machine_matched = self.instance.equ_dict[after_operation.equ_type][chrom[0][after_position] - 1]

        # 工序C匹配机器 尚未 使用
        if after_machine_matched.equ_name not in assigned_machine:
            return True

        # 工序C匹配机器 已经 使用
        c_finished_dict = {}
        for c_p in assigned_machine[after_machine_matched.equ_name]:
            c_finished_dict[c_p] = assigned_product[c_p]
        sort_time_machine = sorted(c_finished_dict.items(), key=lambda x: x[1][0])
        return sort_time_machine


    def check_current_start_c(self,operation_B,pre_end_time,product_no,next_operation_2_machine_situation):
        '''
        :param operation_B: 上个工序B（只有工序B才会触发）
        :param pre_end_time: 上个工序B加工结束时间
        :param product_no: 产品id
        :param next_operation_2_machine_situation: 存储下一个工序可行计划时间节点
        :return: true/false
        '''
        # 如果工序B于当前节点完成，是否可以立即执行工序C
        if operation_B.after_node == -1:
            return True
        after_operation = self.instance.process_flow_dict[self.instance.product_dict[product_no].route_id][operation_B.after_node-1]
        if after_operation.name != '工序C':
            return True

        duration_t = after_operation.get_process_time(self.instance.product_dict[product_no].product_num)

        for i in range(len(next_operation_2_machine_situation)):
            if i == 0 and next_operation_2_machine_situation[i][1][0] >= pre_end_time + duration_t:
                return True
            if next_operation_2_machine_situation[i][1][0] >= pre_end_time + duration_t and pre_end_time >= next_operation_2_machine_situation[i-1][1][1]:
                return True
        # 检查是否可以放到最后
        if next_operation_2_machine_situation[-1][1][1] <= pre_end_time:
            return True

        return False



if __name__ == "__main__":
    d = {"1": [100, 2, "3"], "5": [11, 22, "33"], "6": [8, 10, "4"]}
    print("排序前: ",d)
    sort_d = sorted(d.items(),key=lambda x:x[1][0])
    print("排序后: ",sort_d)

    print(d["1"][:-1])


