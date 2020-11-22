# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 17:53:35 2020

@author: Golinucci
"""

import pandas as pd
import pymrio
import World_Trade_Model

database = r'C:\Users\golinucci\Documents\Database\EXIOBASE\ixi\exiobase_3.4_iot_2011_ixi.zip'
case = r'Inputs\Inputs.xlsx'
World = pymrio.parse_exiobase3(database)
World.calc_all()

#%% Choose aggregations and factors

agg_sec = pd.read_excel(case, sheet_name='Sectors')
agg_reg = pd.read_excel(case, sheet_name='Regions')
Factors = pd.read_excel(case, sheet_name='Factors')

Fac_dis = Factors.loc[:,'Disaggregated_factors']
Fac_agg = Factors.loc[:,'Macro_factor']
Fac_uni = Factors.loc[:,'Unit_of_measure']

sat_index = pd.MultiIndex.from_arrays([Fac_dis.values,Fac_agg.values,Fac_uni.values])
World.satellite.F.index = sat_index
World.satellite.F = World.satellite.F.groupby(level=[1,2], axis=0, sort=False).agg('sum').drop('unused')        

World.aggregate(agg_reg, agg_sec)
World.calc_all()
F = World.satellite.F


