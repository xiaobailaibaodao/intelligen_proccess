# -*- coding: utf-8 -*-
'''
Create on 2022/6/24 16:52

@author: xiachunhao

@description: 工艺流程
'''

import re
import numpy as np

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
        product_no,route_n = prop_id.split('-')
        special_option = False
        if operation.name == '工序B':
            process_time = operation.get_process_time(instance.product_dict[product_no].product_num)
            special_option = True
        else:
            process_time = operation.get_process_time(instance.product_dict[product_no].product_num)

        # 设置工序加工时间
        # 1.工艺流程约束： 判断 当前产品工序 上一工序结束时间
        if operation.before_node == -1:
            before_operation_end_time = 0
        else:
            before_operation_end_time = assigned_product[product_no + '-' + str(operation.before_node)][1]
        if special_option:
            # 工序B
            self.decision_B_start_time(instance,operation,product_no,mached_machine,process_time,assigned_product,assigned_machine,chrom,before_operation_end_time,assigned_route_no)
        else:
            # 非工序B
            self.decision_nonB_start_time(prop_id,mached_machine,process_time,assigned_product,assigned_machine,before_operation_end_time)


    def decision_nonB_start_time(self,prop_id,mached_machine,process_time,assigned_product,assigned_machine,before_operation_end_time):
        '''
        决策非B工序的加工开始时刻,取 产品流程、机器可用时间 两者最大值
        '''
        machine_availabel_time = self.decision_operation_time(mached_machine,before_operation_end_time,process_time,assigned_product,assigned_machine)
        # 更新资源数据
        assigned_product[prop_id][0] = machine_availabel_time
        assigned_product[prop_id][1] = machine_availabel_time + process_time


    def decision_operation_time(self,mached_machine,before_operation_end_time,process_time,assigned_product,assigned_machine):
        # 2.机器加工时间约束：判断 当前工序 分配机器可用时间
        machine_availabel_time = -1
        if len(assigned_machine[mached_machine.equ_name]) == 1:  # 匹配机器只有当前工序加工计划,还未加工其它工艺
            machine_availabel_time = before_operation_end_time
        else:
            sort_time_machine = self.machine_process_situation(assigned_machine, mached_machine, assigned_product)
            mid_mached, mid_available_position = self.candidate_insert_position(sort_time_machine, process_time, before_operation_end_time)
            # 匹配优先级(从高到低)：1.当前机器中第一个工序左边；2.中间；3.当前机器最后
            if sort_time_machine[0][1][0] >= process_time and sort_time_machine[0][1][0] - process_time >= before_operation_end_time:
                machine_availabel_time = before_operation_end_time
            elif mid_mached:
                machine_availabel_time = mid_available_position[0]  # todo 这里可以选择一个最匹配的，间隙时间利用最好的
            else:
                # 如果都不能匹配，安排在机器最后
                machine_availabel_time = max(sort_time_machine[-1][1][1], before_operation_end_time)
        return machine_availabel_time


    def decision_operation_time_C(self,mached_machine,before_operation_end_time,process_time,assigned_machine,after_C_sort_time_machine):
        # 2.机器加工时间约束：判断 当前工序 分配机器可用时间
        machine_availabel_time = -1
        if mached_machine.equ_name not in assigned_machine:  # 匹配机器只有当前工序加工计划,还未加工其它工艺
            machine_availabel_time = before_operation_end_time
        else:
            mid_mached, mid_available_position = self.candidate_insert_position(after_C_sort_time_machine, process_time, before_operation_end_time)
            # 匹配优先级(从高到低)：1.当前机器中第一个工序左边；2.中间；3.当前机器最后
            if after_C_sort_time_machine[0][1][0] >= process_time and after_C_sort_time_machine[0][1][0] - process_time >= before_operation_end_time:
                machine_availabel_time = before_operation_end_time
            elif mid_mached:
                machine_availabel_time = mid_available_position[0]  # todo 这里可以选择一个最匹配的，间隙时间利用最好的
            else:
                # 如果都不能匹配，安排在机器最后
                machine_availabel_time = max(after_C_sort_time_machine[-1][1][1], before_operation_end_time)
        return machine_availabel_time


    def decision_B_start_time(self,instance,operation,product_no,mached_machine,process_time,assigned_product,assigned_machine,chrom,before_B_operation_end_time,assigned_route_no):
        '''决策B工序的加工开始时刻, 基本原来同上，只是需要同时考虑工序C加工'''
        # todo B工序加工时间是个范围主要是考虑到 完成后立即执行工序C，这个优化点
        after_operation = instance.process_flow_dict[instance.product_dict[product_no].route_id][operation.after_node - 1]
        C_process_time = after_operation.get_process_time(instance.product_dict[product_no].product_num)
        after_C_sort_time_machine,C_machine = self.operation_c_machine_situation(instance,product_no,operation,chrom,assigned_product,assigned_machine)
        machine_availabel_time = -1
        if len(assigned_machine[mached_machine.equ_name]) == 1:  # 工序B匹配机器只有当前工序加工计划,还未加工其它工艺
            if len(after_C_sort_time_machine) == 0:
                machine_availabel_time = max(before_B_operation_end_time,0.5*60)
            else:
                # 工序B分配机器未使用，因此只要工序C可以加工即可
                machine_availabel_time = self.decision_operation_time_C(C_machine,before_B_operation_end_time+process_time,C_process_time,assigned_machine,after_C_sort_time_machine)
                machine_availabel_time = max(machine_availabel_time - process_time,0.5*60)
        else:
            # todo 是在不行 改为粗暴遍历查找;(每个机器一个时间维度)
            B_sort_time_machine = self.machine_process_situation(assigned_machine, mached_machine, assigned_product)
            B_available_time_list = self.machine_available_time_list(B_sort_time_machine,process_time)
            C_available_time_list = self.machine_available_time_list(after_C_sort_time_machine,C_process_time)
            find_flag = False
            for b in B_available_time_list:
                if find_flag:
                    break
                if b[1] < before_B_operation_end_time:
                    continue
                sub_b = [max(b[0],before_B_operation_end_time),b[1]]
                b_end = list(map(lambda x:x+process_time,sub_b))    # 逻辑有点绕
                ready_time = 0
                for c in C_available_time_list:
                    if max(b_end[0],c[0]) <= min(b_end[1],c[1]):  # 有交集
                        machine_availabel_time = max(b_end[0],c[0]) - process_time
                        if self.B_ready_time(instance,operation,product_no,mached_machine,assigned_product,assigned_machine,B_available_time_list,b[0],B_sort_time_machine):
                            ready_time = 0.5*60
                        # todo (贪心)插入位置 后一个位置一定满足0.5h,前一个可以判断是否预留,这样才能不改变原有集合；这里可以细化一下
                        if ready_time + b[0] <= machine_availabel_time and machine_availabel_time+process_time+0.5*60 <= b[1]:
                            find_flag = True
                            break
                        if machine_availabel_time + 0.5*60 >= ready_time + b[0] and machine_availabel_time+0.5*60+process_time+0.5*60 <= b[1] and machine_availabel_time+0.5*60+process_time+0.5*60 <= c[1]:
                            machine_availabel_time = machine_availabel_time + 0.5*60
                            find_flag = True
                            break

            if find_flag == False:
                print("程序判断有问题: ",product_no+'-'+str(operation.route_no))
                exit(1)

        # 更新工序B资源
        assigned_product[product_no+'-'+str(operation.route_no)][0] = machine_availabel_time
        assigned_product[product_no+'-'+str(operation.route_no)][1] = machine_availabel_time + process_time
        # 更新工序C资源
        assigned_machine.setdefault(C_machine.equ_name, []).append(product_no + '-' + str(after_operation.route_no))
        assigned_product[product_no + '-' + str(after_operation.route_no)] = [machine_availabel_time + process_time,machine_availabel_time + process_time + C_process_time,C_machine.equ_name]
        assigned_route_no.append(product_no + '-' + str(after_operation.route_no))


    def machine_available_time_list(self,sort_time_machine,operation_process_time):
        '''机器可用时间点集合'''
        available_time_list = []
        if len(sort_time_machine) == 0:
            available_time_list.append([0,np.inf])
            return available_time_list
        if sort_time_machine[0][1][0] >= operation_process_time:
            available_time_list.append([0,sort_time_machine[0][1][0]-operation_process_time])
        for i in range(1,len(sort_time_machine)):
            if sort_time_machine[i][1][0] - sort_time_machine[i-1][1][1] >= operation_process_time:
                available_time_list.append([sort_time_machine[i-1][1][1],sort_time_machine[i][1][0]-operation_process_time])
        available_time_list.append([sort_time_machine[-1][1][1],np.inf])
        return available_time_list


    def B_ready_time(self,instance,operation,product_no,mached_machine,assigned_product,assigned_machine,B_available_time_list,start_point,sort_time_machine):
        # 判断是否增加准备时间(跟插入位置有关,插入位置的前一个工序)
        if len(B_available_time_list) == 1:
            return False
        if start_point == 0:
            return False
        machine_pre_operation = -1
        for i in range(0, len(sort_time_machine)):
            if sort_time_machine[i][1][1] == start_point:
                machine_pre_operation = sort_time_machine[i][0]
                break
        if machine_pre_operation == -1:
            print("搜寻机器前一个加工工序 报错")
            exit(1)
        pre_product = machine_pre_operation.split('-')[0]
        if self.check_if_add_ready_time(instance,operation,product_no,mached_machine,assigned_product,assigned_machine,pre_product):
            return True
        return False


    def machine_process_or_not(self,start,end,process_time,before_operation_end_time):
        '''判断机器相邻两个加工工序之间，是否可以插入当前工序'''
        if end - start < process_time:
            return False
        if before_operation_end_time >= end:
            return False
        if before_operation_end_time + process_time > end:
            return False

        return True


    def if_process_C(self,instance,product_no,B_end_time,C_opration,after_C_sort_time_machine):
        '''检查此刻是否可以开始加工工序C'''
        C_duration = C_opration.get_process_time(instance.product_dict[product_no].product_num)
        if B_end_time + C_duration <= after_C_sort_time_machine[0][1][0]:
            return True
        if B_end_time >= after_C_sort_time_machine[-1][1][1]:
            return True
        for i in range(1,len(after_C_sort_time_machine)):
            if B_end_time >= after_C_sort_time_machine[i-1][1][1] and B_end_time + C_duration <= after_C_sort_time_machine[i][1][0]:
                return True
        return False


    def operation_c_machine_situation(self, instance,product_no, operation_B, chrom, assigned_product, assigned_machine):
        # 工序C对应机器使用情况
        sort_time_machine = []
        after_operation = instance.process_flow_dict[instance.product_dict[product_no].route_id][operation_B.after_node - 1]
        after_operation_str = product_no + '-' + str(operation_B.after_node)
        after_position = chrom[1].index(after_operation_str)
        after_machine_matched = instance.equ_dict[after_operation.equ_type][chrom[0][after_position] - 1]

        # 工序C匹配机器 尚未 使用
        if after_machine_matched.equ_name not in assigned_machine:
            return sort_time_machine,after_machine_matched

        # 工序C匹配机器 已经 使用
        c_finished_dict = {}
        for c_p in assigned_machine[after_machine_matched.equ_name]:
            c_finished_dict[c_p] = assigned_product[c_p]
        sort_time_machine = sorted(c_finished_dict.items(), key=lambda x: x[1][0])
        return sort_time_machine,after_machine_matched


    def machine_process_situation(self,assigned_machine,mached_machine,assigned_product):
        '''当前机器已分配工序加工情况'''
        machine_time_dict = {}
        for o in assigned_machine[mached_machine.equ_name][:-1]:
            machine_time_dict[o] = assigned_product[o]
        sort_time_machine = sorted(machine_time_dict.items(), key=lambda x: x[1][0])
        return sort_time_machine


    def candidate_insert_position(self,sort_time_machine,process_time,before_operation_end_time):
        '''
        该机器可插入时间点,只记录中间可插入位置（插入工序后，会影响插入位置后面工序B是否需要准备时长的状态,因此最后统一调整）
        :param sort_time_machine: 当前工序匹配机器分配加工时间 按照开始时间升序排序
        :param process_time: 当前工序加工时间
        :param before_operation_end_time: 该工序按照工艺流程上一个工序完成时间
        :return: list
        '''
        end = -1
        mid_mached = False
        mid_available_position = []  # 记录 当前工序 可插入计划中执行 开始时间节点
        for s in sort_time_machine:
            if end == -1:
                end = s[1][1]
                continue
            if s[1][0] - end >= process_time and end >= before_operation_end_time:
                mid_mached = True
                machine_end_time = end
                mid_available_position.append(machine_end_time)
            end = s[1][1]
        return mid_mached,mid_available_position


    def check_if_add_ready_time(self,instance,operation,product_no,mached_machine,assigned_product,assigned_machine,pre_product):
        '''
        :param operation: 当前工序对象
        :param product_no: 产品id
        :param product_first_operation: 是否第一道工序
        :return: true/false
        '''

        # 情况一：产品工序中第一次出现工序B
        first_b_route_no = instance.route_flow_first_B[instance.product_dict[product_no].route_id]
        if operation.route_no == first_b_route_no:
            # print("情况一  工序B {} 需要准备时间".format(product_no + '-' + str(operation.route_no)))
            return True

        # 情况二：当前产品存在多次工序B，且其使用机器与上一次使用机器不同(上一次处理工序B时使用机器)
        pre_b_operation = -1
        for pf in instance.process_flow_dict[instance.product_dict[product_no].route_id]:
            if pf == operation:
                break
            if pf.name == '工序B':
               pre_b_operation = pf

        if pre_b_operation == -1:
            # 工序中第一次出现B
            print("此工序只出现过一次工序B")
            return False

        if mached_machine.equ_name != assigned_product[product_no+'-'+str(pre_b_operation.route_no)][2]:
            # print("情况二  工序B {} 需要准备时间".format(product_no + '-' + str(operation.route_no)))
            return True

        # 情况三：当前机器加工的产品与当前机器上一次加工的产品不同
        if mached_machine.equ_name in assigned_machine and len(assigned_machine[mached_machine.equ_name]) >= 2:
            # pre_product = assigned_machine[mached_machine.equ_name][-2].split('-')    # 最后一个是当前判断工序
            if product_no != pre_product:
                # print("情况三  工序B {} 需要准备时间".format(product_no + '-' + str(operation.route_no)))
                return True

        # 不增加准备时间
        if mached_machine.equ_name == assigned_product[product_no+'-'+str(pre_b_operation.route_no)][2]:
            print("工序B {} 不需要准备时间".format(product_no+'-'+str(operation.route_no)))
            return False
        print("第二种情况 工序B {} 不需要准备时间", product_no + '-' + str(operation.route_no))
        return False


