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
        # print("开始结果约束检查: ")
        # self.draw_gantt_chart(submit_df)
        # print("结果约束检查结束")
        self.check_result_constrained(submit_df)

        submit_df.to_csv(save_path,encoding='utf8',index=False)
        # print("success!")


    def check_result_constrained(self,submit_df):
        # 检查结果是否满足各项约束
        # 约束一：每个设备同时只能加工某种产品的某个工序，一旦开始不能中断
        for equ,temp in submit_df.groupby('equ_name'):
            # print("检查机器: ",equ)
            temp = temp.sort_values(by=['start'])
            for i in range(1,len(temp)):
                pre_end_time = temp.iloc[i-1]['end']
                next_start_time = temp.iloc[i]['start']
                if next_start_time < pre_end_time:
                    print("此工序安排有问题: ",temp.iloc[i]['product_id'],temp.iloc[i]['route_No'])

        for product,df in submit_df.groupby('product_id'):
            # 约束二：产品加工顺序严格按照工艺流程，上一道工序完成后，才能开始下道工序
            df = df.sort_values(by=['route_No'])
            for i in range(1, len(df)):
                pre_end_time = df.iloc[i - 1]['end']
                next_start_time = df.iloc[i]['start']
                if next_start_time < pre_end_time:
                    print("违反约束二: ",df.iloc[i]['product_id'],df.iloc[i]['route_No'])

                # 约束四：工序B结束后 是否 立即开始 工序C
                for p in self.instance.process_flow_dict[self.instance.product_dict[df.iloc[i-1]['product_id']].route_id]:
                    if p.route_no == df.iloc[i-1]['route_No'] and p.name == '工序B' and next_start_time != pre_end_time:
                        print("违反约束四: ",df.iloc[i]['product_id'],df.iloc[i]['route_No'])

        # 约束三：每个工序同时只能在一个设备上加工
        # 约束五：以节为单位的工序，必须连续加工

        # 约束六：工序B是否满足准备时间要求(1.工序B完成后立即开始工序C；2.工序B准备时间问题)
        # 1.工序B完成后立即开始工序C
        for product, df in submit_df.groupby('product_id'):
            df = df.sort_values(by=['route_No'])
            for i in range(0,len(df)-1):
                current_name = self.instance.process_flow_dict[self.instance.product_dict[df.iloc[i]['product_id']].route_id][df.iloc[i]['route_No']-1].name
                if current_name != '工序B':
                    continue
                if df.iloc[i]['end'] != df.iloc[i+1]['start']:
                    print("违反约束六-1: ",df.iloc[i]['product_id'],df.iloc[i]['route_No'])
        # 2.工序B准备时间问题
        process_B_machine = []    # 可以加工工序B的机器列表
        checked_equ_type = []
        for product in self.instance.unassign_product:
            route_obj = self.instance.process_flow_dict[self.instance.product_dict[product].route_id]
            for route in route_obj:
                if route.name == '工序B' and route.equ_type not in checked_equ_type:
                    checked_equ_type.append(route.equ_type)
                    for obj in self.instance.equ_dict[route.equ_type]:
                        if obj.equ_name not in process_B_machine:
                            process_B_machine.append(obj.equ_name)

        for equ,df in submit_df.groupby('equ_name'):
            df = df.sort_values(by=['start'])





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

if __name__ == "__main__":
    # 评价指标 - 线上计算一致
    import pandas as pd
    # submit_result_file = '../output/目前最高分结果34.csv'
    submit_result_file = '../output/优化后竟然更低了29.csv'
    # submit_result_file = '../output/调度结果提交.csv'
    submit_df = pd.read_csv(submit_result_file)

    operation_C_df = submit_df[submit_df['equ_name']=='Y-2045']
    all_operation_C_time = operation_C_df['duration'].sum()
    all_product_finish_time = submit_df['end'].max()

    print(all_operation_C_time,all_product_finish_time,all_operation_C_time/all_product_finish_time)


