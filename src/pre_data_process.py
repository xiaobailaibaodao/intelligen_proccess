# -*- coding: utf-8 -*-
'''
Create on 2022/6/28 15:33

@author: xiachunhao

@description: 数据预处理
'''

import pandas as pd
import numpy as np
from product import Product
from process import ProcessFlow
from equipment import Equ

class PreProcess:

    def __init__(self,product_info,process_flow,equ_info):
        self.unassign_product,self.product_dict = self.deal_product_info(product_info)
        self.process_flow_dict,self.route_flow_first_B = self.deal_process_flow(process_flow)
        self.equ_dict,self.equ_name_2_info = self.deal_equ_info(equ_info)
        self.equ_num = len(equ_info)    # 设备数量
        self.product_num = len(self.unassign_product)   # 产品数量


    def deal_product_info(self,product_info):
        # 处理产品数据
        unassign_product = []
        product_dict = {}
        for index,row in product_info.iterrows():
            unassign_product.append(row['product_id'])
            p = Product(row['product_id'],row['product_num'],row['route_id'])
            product_dict[row['product_id']] = p
        print("deal product info finished")
        return unassign_product,product_dict


    def deal_process_flow(self,process_flow):

        process_flow_dict = {}
        route_flow_first_B = {}    # 每个工艺流程中第一次出现工序B
        for id,temp in process_flow.groupby('route_id'):
            first_b = False
            for index,row in temp.iterrows():
                pf = ProcessFlow(id,row['route_No'],row['name'],row['equ_type'],row['time'],row['unit'],row['ready_time'])
                if not first_b and pf.name == '工序B':
                    route_flow_first_B[id] = pf.route_no
                    first_b = True
                process_flow_dict.setdefault(id,[]).append(pf)
            process_flow_dict[id].sort()
            # 更新节点信息
            for i in range(len(process_flow_dict[id])-1):
                if i == 0:
                    process_flow_dict[id][i].after_node = process_flow_dict[id][i+1].route_no
                else:
                    process_flow_dict[id][i].after_node = process_flow_dict[id][i+1].route_no
                    process_flow_dict[id][i].before_node = process_flow_dict[id][i-1].route_no
            process_flow_dict[id][len(process_flow_dict[id])-1].before_node = process_flow_dict[id][len(process_flow_dict[id])-2].route_no
        print("deal process flow finished")
        return process_flow_dict,route_flow_first_B


    def deal_equ_info(self,equ_info):

        equ_dict = {}
        equ_name_2_info = {}
        for index,row in equ_info.iterrows():
            e = Equ(row['equ_name'],row['equ_type'],row['unit'])
            equ_dict.setdefault(row['equ_type'],[]).append(e)
            equ_name_2_info[row['equ_name']] = e
        print("deal equ info finished")
        return equ_dict,equ_name_2_info
