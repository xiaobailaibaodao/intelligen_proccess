# -*- coding: utf-8 -*-
'''
Create on 2022/6/28 17:42

@author: xiachunhao

@description: 策略集合
'''

import random
import numpy as np
import copy

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
            r_list = list(np.random.randint(low=0,high=len(chrom),size=3))
            local_best_obj = 0
            local_best_index = 0
            for r in r_list:
                if chrom[r][2] > local_best_obj:
                    local_best_obj = chrom[r][2]
                    local_best_index = r
            mate_pool.append(chrom[local_best_index])
        return mate_pool


    @classmethod
    def crossover_operator(cls,mate_pool,instance):
        '''交叉算子(等位基因) - 文献中选择了三次，此处选择一次'''
        if len(mate_pool) <= 2:
            print("进化池中个体数量太少....")
            exit(0)
        parent_f_index,parent_m_index = list(np.random.randint(low=0,high=len(mate_pool),size=2))
        parent_f = mate_pool[parent_f_index]
        parent_m = mate_pool[parent_m_index]
        child_son = copy.deepcopy(parent_f)
        child_dau = copy.deepcopy(parent_m)
        crossover_flag = True
        while crossover_flag:
            # Machine Selection part (MS两种) - two point crossover、uniform crossover
            if random.random() < 0.5:
                # two point crossover
                first_position = np.random.randint(low=0,high=len(parent_f[0])-1)
                second_position = first_position + 1
            else:
                # uniform crossover
                first_position,second_position = list(np.random.randint(low=0,high=len(parent_f[0]),size=2))
            # 检查对应工序是否有这么多候选机器可选，如果没有则重新选择
            if not cls.new_machine_effective(instance,parent_f,parent_m,first_position,second_position):
                continue
            crossover_flag = False
            child_son[0][first_position] = parent_m[0][first_position]
            child_son[0][second_position] = parent_m[0][second_position]
            child_dau[0][first_position] = parent_f[0][first_position]
            child_dau[0][second_position] = parent_f[0][second_position]
        # Operation Sequence part(OS - POX)
        child_1,child_2 = cls.operation_sequence(child_son,child_dau,instance)
        mate_pool.append(child_1)
        mate_pool.append(child_2)


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
        parent_f_machine = instance.equ_dict[instance.process_flow_dict[instance.product_dict[parent_f_product].route_id][int(parent_f_no) - 1].equ_type]
        parent_m_machine = instance.equ_dict[instance.process_flow_dict[instance.product_dict[parent_m_product].route_id][int(parent_m_no) - 1].equ_type]
        if len(parent_f_machine) >= parent_m[0][check_position] and len(parent_m_machine) >= parent_f[0][check_position]:
            return True
        return False


    @classmethod
    def operation_sequence(cls,child_son,child_dau,instance):
        '''工序部分的交叉'''
        child_corss_1 = cls.POX_method(child_son,child_dau,instance,2)
        child_corss_2 = cls.POX_method(child_dau,child_son,instance,2)
        return child_corss_1,child_corss_2


    @classmethod
    def POX_method(cls,child_son,child_dau,instance,size):
        unassign_product = np.array(instance.unassign_product)
        random_job_index = np.random.randint(low=0,high=len(unassign_product),size=size)
        random_job_list = list(unassign_product[random_job_index])
        child = copy.deepcopy(child_son)
        second_individual_index = 0
        for i in range(len(child_son[0])):
            if child[1][i].split('-')[0] in random_job_list:
                continue
            for j in range(second_individual_index,len(child_dau[1])):
                if child_dau[1][j].split('-')[0] not in random_job_list:
                    second_individual_index = j + 1
                    child[1][i] = child_dau[1][j]
                    child[0][i] = child_dau[0][j]
                    break
        return child


    @classmethod
    def mutation_operator(cls,mate_pool,pm,instance):
        '''
        变异算子
        :param mate_pool: 子代个体池
        :param muta_size: 需要变异个体数
        :param pm: 变异概率
        :return:
        '''
        # MS
        # 1.保持机器加工数量均衡，选择合适机器(因为同一个工序同类型机器加工时间一样，没办法通过最短加工时间区分)
        # 2.细化比较每个机器工作时长也可
        matu_individual = mate_pool[random.randint(0, len(mate_pool)-1)]
        cls.mutation_MS(pm,mate_pool,instance,matu_individual)
        # OS
        cls.mutation_OS(pm,instance,matu_individual)


    @classmethod
    def mutation_MS(cls,pm,mate_pool,instance,matu_individual):
        '''尽量保持每种机器类型下机器加工数量均衡-当前个体'''
        matu_index = -1
        for i in range(len(matu_individual[0])):
            if random.random() <= pm:
                matu_index = i
                break
        if matu_index == -1:
            return

        product_no,route_no = matu_individual[1][matu_index].split('-')
        obj_machine_type = instance.process_flow_dict[instance.product_dict[product_no].route_id][int(route_no)-1].equ_type
        operation_all_available_machine = instance.equ_dict[obj_machine_type]

        # 当前机器类型下 全部机器加工工序情况
        now_machine_situstion = {}
        for prod in matu_individual[1]:
            p,r = prod.split('-')
            check_machine_type = instance.process_flow_dict[instance.product_dict[p].route_id][int(r) - 1].equ_type
            if check_machine_type == obj_machine_type:
                now_machine_situstion.setdefault(str(r),[]).append(prod)

        choose_nachine = -1
        # 如果有未使用机器优先分配
        if len(now_machine_situstion.keys()) == len(operation_all_available_machine):
            sort_dict = sorted(now_machine_situstion.items(),key=lambda x:len(x[1]))
            choose_nachine = int(sort_dict[0][0])
        else:
            for i in range(len(operation_all_available_machine)):
                if str(i+1) not in now_machine_situstion:
                    choose_nachine = i+1
                    break
        matu_individual[0][matu_index] = choose_nachine


    @classmethod
    def mutation_OS(cls,pm,instance,matu_individual):
        os_index = -1
        change_index = -1
        for i in range(len(matu_individual[1])):
            if random.random() < pm:
                os_index = i
                break
        if os_index == -1:
            return
        while True:
            change_index = random.randint(0,len(matu_individual[1])-1)
            if change_index != os_index:
                os_machine = instance.equ_dict[instance.process_flow_dict[instance.product_dict[matu_individual[1][os_index].split('-')[0]].route_id][int(matu_individual[1][os_index].split('-')[1]) - 1].equ_type]
                # print(matu_individual[1][change_index].split('-'))
                change_machine = instance.equ_dict[instance.process_flow_dict[instance.product_dict[matu_individual[1][change_index].split('-')[0]].route_id][int(matu_individual[1][change_index].split('-')[1]) - 1].equ_type]
                if len(os_machine) >= matu_individual[0][change_index] and len(change_machine) >= matu_individual[0][os_index]:
                    break
        # 交换位置
        matu_individual[1][os_index],matu_individual[1][change_index] = matu_individual[1][change_index],matu_individual[1][os_index]


    # -------------特殊问题，特殊策略处理-----------------
    # todo 适当决策工序B加工时长
    # todo 适当拆分 以节 为加工批次的工序
