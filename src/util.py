# -*- coding: utf-8 -*-
'''
Create on 2022/7/11 20:12

@author: xiachunhao

'''

# 存储一些过往代码记录

def decision_B_start_time(self, instance, operation, product_no, mached_machine, process_time, assigned_product,
                          assigned_machine, chrom, before_B_operation_end_time, assigned_route_no):
    '''决策B工序的加工开始时刻, 基本原来同上，只是需要同时考虑工序C加工'''
    # B工序后面C工序匹配机器加工情况
    after_operation = instance.process_flow_dict[instance.product_dict[product_no].route_id][operation.after_node - 1]
    C_process_time = after_operation.get_process_time(instance.product_dict[product_no].product_num)
    after_C_sort_time_machine, C_machine = self.operation_c_machine_situation(instance, product_no, operation, chrom,
                                                                              assigned_product, assigned_machine)
    machine_availabel_time = -1
    if len(assigned_machine[mached_machine.equ_name]) == 1:  # 匹配机器只有当前工序加工计划,还未加工其它工艺
        if len(after_C_sort_time_machine) == 0:
            machine_availabel_time = before_B_operation_end_time
        else:
            # 工序B分配机器未使用，因此只要工序C可以加工即可
            machine_availabel_time = self.decision_operation_time_C(C_machine,
                                                                    before_B_operation_end_time + process_time,
                                                                    C_process_time, assigned_product, assigned_machine,
                                                                    after_C_sort_time_machine)
            machine_availabel_time = machine_availabel_time - process_time
    else:
        # todo 是不是可以完全替代全部判断
        B_sort_time_machine = self.machine_process_situation(assigned_machine, mached_machine, assigned_product)
        B_available_time_list = self.machine_available_time_list(B_sort_time_machine, process_time,
                                                                 before_B_operation_end_time)
        C_available_time_list = self.machine_available_time_list(after_C_sort_time_machine, C_process_time,
                                                                 before_B_operation_end_time + process_time)  # todo 这里是否有问题，因为事先不知道上一个工序结束时间
        find_flag = False
        for b in B_available_time_list:
            if find_flag:
                break
            b_end = list(map(lambda x: x + process_time, b))
            for c in C_available_time_list:
                if max(b_end[0], c[0]) <= min(b_end[1], c[1]):  # 有交集
                    machine_availabel_time = max(b_end[0], c[0]) - process_time
                    find_flag = True
                    break


    def machine_available_time_list(self,sort_time_machine,operation_process_time,before_operation_end_time):
        '''机器可用时间点集合'''
        available_time_list = []
        if len(sort_time_machine) == 0:
            available_time_list.append([before_operation_end_time,np.inf])
            return available_time_list
        if sort_time_machine[0][1][0] - operation_process_time >= before_operation_end_time:
            available_time_list.append([0,sort_time_machine[0][1][0]-operation_process_time-before_operation_end_time])
        for i in range(1,len(sort_time_machine)):
            if self.machine_process_or_not(sort_time_machine[i-1][1][1],sort_time_machine[i][1][0],operation_process_time,before_operation_end_time):
                available_time_list.append([sort_time_machine[i-1][1][1],sort_time_machine[i][1][0]-operation_process_time])
        available_time_list.append([sort_time_machine[-1][1][1],np.inf])
        return available_time_list

