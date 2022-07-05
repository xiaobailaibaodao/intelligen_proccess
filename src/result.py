# -*- coding: utf-8 -*-
'''
Create on 2022/7/5 10:56

@author: xiachunhao

@description: 算法结果格式化
'''

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm


class Result:

    def __init__(self,model):
        self.instance = model.instance
        self.best_chrom = model.best_chrom
        self.best_obj = model.best_obj
        self.best_assigned_route_no = model.best_assigned_route_no
        self.best_assigned_product = model.best_assigned_product
        self.best_assigned_machine = model.best_assigned_machine


    def format_algo_best_result(self,save_path):
        # 格式化算法结果成标准格式
        submit_info_list = []
        for pr in self.instance.product_dict:
            for op in self.instance.process_flow_dict[self.instance.product_dict[pr].route_id]:
                route_no = op.route_no
                equ_name = self.best_assigned_product[pr+'-'+str(route_no)][2]
                start = self.best_assigned_product[pr+'-'+str(route_no)][0] / 60
                end = self.best_assigned_product[pr+'-'+str(route_no)][1] / 60
                duration = (self.best_assigned_product[pr+'-'+str(route_no)][1] - self.best_assigned_product[pr+'-'+str(route_no)][0]) / 60
                submit_info_list.append([pr,route_no,equ_name,start,duration,end])

        submit_df = pd.DataFrame(submit_info_list,columns=['product_id','route_No','equ_name','start','duration','end'])

        # ------------结果约束检查-----------
        print("开始结果约束检查: ")
        self.draw_gantt_chart(submit_df)
        print("结果约束检查结束")

        submit_df.to_csv(save_path,encoding='utf8',index=False)
        # print("success!")


    def check_result_constrained(self,submit_df):
        # 检查结果是否满足各项约束
        # 约束一：每个产品是否满足 紧前工序完成后 才能开始后续工序
        # 约束二：同一台机器同一时间只能加工一个工序
        # 约束三：工序B结束后 是否 立即开始 工序C
        pass


    def draw_gantt_chart(self,submit_df):
        # 将结果通过 甘特图 展示
        # 尝试四种不同的调色板，分别生成颜色列表
        all_product_type = set(submit_df['product_id'])
        cmap_names = ["viridis", "RdBu", "Set1", "jet","Spectral"]
        # 必须通过引入 import matplotlib.cm , 通过 mpl.cm 报错找不到cm模块
        cmap = matplotlib.cm.get_cmap(cmap_names[2], len(all_product_type))       # 创建colormap对象，颜色列表长度和柱子的数量相同
        plt.colormaps()
        color_dict = {}
        category_colors = cmap(np.linspace(0.15, 0.85, len(set(submit_df['product_id'])) ))
        for p,c in zip(set(submit_df['product_id']),category_colors):
            color_dict[p] = c
        submit_df['color'] = submit_df['product_id'].apply(lambda x: color_dict[x])

        fig, ax = plt.subplots(1, figsize=(20,10))
        ax.barh(submit_df.product_id, submit_df.duration, left=submit_df.start,color=submit_df.color)
        plt.savefig('../output/调度甘特图.png')
        # plt.show()

