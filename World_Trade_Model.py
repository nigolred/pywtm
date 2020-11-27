# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 17:34:39 2020

@author: Golinucci
"""

def aggregate(WIOT, agg_file):
    import pandas as pd
    
    agg_sec = pd.read_excel(agg_file, sheet_name='Sectors')
    agg_reg = pd.read_excel(agg_file, sheet_name='Regions')
    Factors = pd.read_excel(agg_file, sheet_name='Factors')
    Fac_dis = Factors.loc[:,'Disaggregated_factors']
    Fac_agg = Factors.loc[:,'Macro_factor']
    Fac_uni = Factors.loc[:,'Unit_of_measure']
    
    sat_index = pd.MultiIndex.from_arrays([Fac_dis.values,Fac_agg.values,Fac_uni.values])
    WIOT.satellite.F.index = sat_index
    WIOT.satellite.F = WIOT.satellite.F.groupby(level=[1,2], axis=0, sort=False).agg('sum').drop('unused')        
    WIOT.aggregate(agg_reg, agg_sec)

def prepare(WIOT, print_input_file=False):
    import pandas as pd
    
    takeall = slice(None)
    reg = list(WIOT.get_regions())
    sec = list(WIOT.get_sectors())

    # build the needed matrices
    
    WIOT.Y_reg = WIOT.Y.groupby(level=0, axis=1).sum()
    WIOT.Y_wtm = pd.DataFrame(0, index=WIOT.Y_reg.index, columns=WIOT.Y_reg.columns)
    
    for i in reg:
        WIOT.Y_wtm.loc[(i,takeall),i] = sum(WIOT.Y_reg.loc[(j,takeall),i].values for j in reg)

    WIOT.A_wtm = pd.DataFrame(0, index=WIOT.A.index, columns=WIOT.A.columns)
    for i in reg:
        WIOT.A_wtm.loc[(i,takeall),(i,takeall)] = sum(WIOT.A.loc[(j,takeall),(i,takeall)].values for j in reg)
          
    for i in reg:
        for j in sec:
            if sum(WIOT.A_wtm.loc[(i,takeall),(i,j)]) == 0:
                WIOT.A_wtm.loc[(i,takeall),(i,j)] = 9999
    
    WIOT.satellite.F_wtm = pd.DataFrame(0, index=pd.MultiIndex.from_product([reg,list(WIOT.satellite.S.index)]), columns=WIOT.satellite.S.columns)
    for i in reg:
        WIOT.satellite.F_wtm.loc[(i,takeall),i] = WIOT.satellite.S.loc[takeall,(i,takeall)].values

    # print the constraints file
    
    if print_input_file:
        f_reg = pd.DataFrame(999999999, index=WIOT.satellite.S.index, columns=reg)
        p_glo = pd.DataFrame(0, index=WIOT.satellite.S.index, columns=['Price of factors'])
        with pd.ExcelWriter(r'Inputs/WTM_Inputs.xlsx', mode='w') as writer:
            f_reg.to_excel(writer, sheet_name = 'Regional Endowments')
            p_glo.to_excel(writer, sheet_name = 'Global Price of factors')
            

def run(WIOT, Constraints):
    import cvxpy as cv
    import numpy as np
    import pandas as pd
    
    # importing constraint file
    
    pi = pd.read_excel(Constraints, sheet_name='Global Price of factors', index_col = [0,1])
    F_reg = pd.read_excel(Constraints, sheet_name='Regional Endowments', index_col = [0,1]).unstack([0,1]).to_frame()
    
    WIOT.pi = pi
    WIOT.F_reg = F_reg
    
    # get number of sectors and regions
    reg = list(WIOT.get_regions())
    sec = list(WIOT.get_sectors())
    r = len(reg)
    s = len(sec)
    
    X = cv.Variable((r*s, 1), nonneg=True)
    T = cv.Variable((r*s, r), nonneg=True)
    
    EX = cv.sum(T, 1, keepdims=True)              # exports (by sector, by country)
    IM = np.zeros([s,r])                          # imports (by sector, by country)
    
    for i in range(r):
        IM += T[(i*s):(i*s+s), :]
    
    IM = cv.reshape(IM,(r*s, 1))
    
    ObjFun = cv.matmul(cv.matmul(pi.T,WIOT.satellite.S), X) #Minimization of global factor cost
    objective = cv.Minimize(ObjFun)
    
    constraints = []
    constraints.append(X >= cv.matmul(WIOT.A_wtm, X) - IM + EX + np.sum(WIOT.Y_wtm.values, 1, keepdims=True))
    constraints.append(cv.matmul(WIOT.satellite.F_wtm, X) <= F_reg)
                   
    prob = cv.Problem(objective, constraints)
    WIOT.WTM_result = prob.solve(solver=cv.GUROBI, verbose=True)
    
    WIOT.wtm_results = {
        'GDP': pd.DataFrame(objective.value/10**6, index=['World'], columns=['GDP [T€]']),
        'X': pd.DataFrame(X.value, index=WIOT.x.index, columns=['Production [M€]']),
        'T': pd.DataFrame(T.value, index=WIOT.A.index, columns=reg),
        'EX': pd.DataFrame(EX.value, index=WIOT.A.index, columns=['Exports [M€]']),
        'IM': pd.DataFrame(IM.value, index=WIOT.A.index, columns=['Imports [M€]']),
        'p': pd.DataFrame(constraints[0].dual_value, index=WIOT.x.index, columns=['Prices [M€/M€]']),
        'r':pd.DataFrame(constraints[1].dual_value, index=WIOT.F_reg.index, columns=['Scarcity Rents [M€/unit]'])
        }

    # nic = pymrio.IO(x=X,)    
    
