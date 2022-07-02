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
        self.process_flow_dict = self.deal_process_flow(process_flow)
        self.equ_dict = self.deal_equ_info(equ_info)
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
        for id,temp in process_flow.groupby('route_id'):
            for index,row in temp.iterrows():
                pf = ProcessFlow(id,row['route_No'],row['name'],row['equ_type'],row['time'],row['unit'],row['ready_time'])
                process_flow_dict.setdefault(id,[]).append(pf)
            process_flow_dict[id].sort()
        print("deal process flow finished")
        return process_flow_dict


    def deal_equ_info(self,equ_info):

        equ_dict = {}
        for index,row in equ_info.iterrows():
            e = Equ(row['equ_name'],row['equ_type'],row['unit'])
            equ_dict.setdefault(row['equ_type'],[]).append(e)
        print("deal equ info finished")
        return equ_dict
