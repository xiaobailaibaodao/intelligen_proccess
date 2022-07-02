# -*- coding: utf-8 -*-
'''
Create on 2022/6/24 16:50

@author: xiachunhao

@description: 产品信息类

'''


class Product:

    def __init__(self,product_id,product_num,route_id):
        '''
        :param product_id: 产品id
        :param product_num: 节数量
        :param route_id: 工艺路线
        '''
        self.product_id = product_id
        self.product_num = product_num
        self.route_id = route_id
        self.all_operations = 0


    def __str__(self):
        return "产品id: %s, 节数量: %s, 工艺路线: %s" % (self.product_id,self.product_num,self.route_id)




