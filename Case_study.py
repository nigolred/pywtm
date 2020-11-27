# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 17:53:35 2020

@author: nigolred
"""

import pymrio
import World_Trade_Model as wtm

exiobase3_path = r'C:\Users\Gollinucci\Desktop\Nicolò\Lavoro\FEEM\Databases\exiobase_3.4_iot_2011_ixi.zip'
Agg = r'Inputs\Aggregation.xlsx'
World = pymrio.parse_exiobase3(exiobase3_path)
World.calc_all()

#%% Choose aggregations and factors
wtm.aggregate(World, Agg)
World.calc_all()
GDP = World.satellite.F.loc['Value Added',:].sum().sum()/10**6
#%% Building the needed matrices
wtm.prepare(World)

#%% Running the model and saving the results
WTM_World = wtm.run(World, r'Inputs\WTM_Inputs.xlsx')
Results = World.wtm_results
GDP_wtm = Results['GDP'].sum().sum()
GDP_p = (GDP_wtm-GDP)*100/GDP

# for world in world_dict.keys()
