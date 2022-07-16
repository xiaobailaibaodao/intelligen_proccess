# -*- coding: utf-8 -*-
'''
Create on 2022/6/28 17:42

@author: xiachunhao

@description: 策略集合
'''

import random
import numpy as np

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
        # print("random select machine")
        job_list = instance.unassign_product
        i = 0    # 工序 匹配 机器 的索引对应
        random.shuffle(job_list)    # 1.随机选择job安排
        for id in job_list:
            product_obj = instance.product_dict[id]
            j = 1      # 工序号
            for operation in instance.process_flow_dict[product_obj.route_id]:  # 按照工艺顺序计划，不会违背优先级
                operatio_select[i] = id +"-"+ str(j)       # 同一产品，按照工艺流程顺序安排
                j += 1
                operation_available_machines = instance.equ_dict[operation.equ_type]
                # find shortest time process machine
                machine_id = random.randint(1,len(operation_available_machines))    # 随机选择,记得 减一取值
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


    @classmethod
    def selection_operator(cls,chrom,select_rate):
        '''遗传算法 - 选择算子'''
        mate_pool = []
        while len(mate_pool) < int(select_rate*len(chrom)):
            r_list = list(np.random.randint(low=0,hign=len(chrom),size=3))
            local_best_obj = 0
            local_best_index = 0
            for r in r_list:
                if chrom[r][2] > local_best_obj:
                    local_best_obj = chrom[2]
                    local_best_index = r
            mate_pool.append(chrom[local_best_index])
        return mate_pool


    @classmethod
    def crossover_operator(cls,mate_pool,instance):
        '''交叉算子(等位基因) - 文献中选择了三次，此处选择一次'''
        if len(mate_pool) <= 2:
            print("进化池中个体数量太少....")
            exit(0)
        parent_f_index,parent_m_index = list(np.random.random(low=0,high=len(mate_pool),size=2))
        parent_f = mate_pool[parent_f_index]
        parent_m = mate_pool[parent_m_index]
        crossover_flag = True
        while crossover_flag:
            # Machine Selection part (MS两种) - two point crossover、uniform crossover
            if random.random() < 0.5:
                # two point crossover
                first_position = np.random.random(low=0,high=len(parent_f[0])-1)
                second_position = first_position + 1
            else:
                # uniform crossover
                first_position,second_position = list(np.random.random(low=0,high=len(parent_f[0]),size=2))
            # 检查对应工序是否有这么多候选机器可选，如果没有则重新选择
            if not cls.new_machine_effective(instance,parent_f,parent_m,first_position,second_position):
                continue
            crossover_flag = False


        # Operation Sequence part(OS - POX)
        pass


    @classmethod
    def new_machine_effective(cls,instance,parent_f,parent_m,first_position,second_position):
        '''必须保证交换后，机器对应的是工序候选数量内'''
        if cls.check_alleles_effective(instance,parent_f,parent_m,first_position) and cls.check_alleles_effective(instance,parent_f,parent_m,second_position):
            return True
        return False


    @classmethod
    def check_alleles_effective(cls,instance,parent_f,parent_m,check_position):
        '''检查等位基因是否可以互换'''
        parent_f_product, parent_f_no = parent_f[1][check_position].split('-')
        parent_m_product, parent_m_no = parent_m[1][check_position].split('-')
        parent_f_machine = instance.equ_dict[instance.process_flow_dict[instance.product_dict[parent_f_product].route_id][parent_f_no - 1].equ_type]
        parent_m_machine = instance.equ_dict[instance.process_flow_dict[instance.product_dict[parent_m_product].route_id][parent_m_no - 1].equ_type]
        if len(parent_f_machine) >= parent_m[0][check_position] and len(parent_m_machine) >= parent_f[0][check_position]:
            return True
        return False


    @classmethod
    def mutation_operator(cls,mate_pool,muta_size):
        '''
        变异算子
        :param mate_pool: 子代个体池
        :param muta_size: 需要变异个体数
        :return:
        '''
        pass

