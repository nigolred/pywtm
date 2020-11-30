# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 17:53:35 2020

@author: nigolred
"""

import pymrio
import pywtm as wtm

exiobase3_path = r'C:\Users\Gollinucci\Desktop\Nicolò\Lavoro\FEEM\Databases\exiobase_3.4_iot_2011_ixi.zip'
Agg = r'Inputs\Aggregation.xlsx'
World = pymrio.parse_exiobase3(exiobase3_path)
World.calc_all()

#%% Choose aggregations and factors
wtm.aggregate(World, Agg)
World.calc_all()

#%% Building the needed matrices
wtm.prepare(World)

#%% Running the model and saving the results
import pandas as pd

Cases = ['Baseline',
         'EU_CT',
         'EU_ETS']

allCases = Cases + ['Exiobase']
Sectors = list(World.get_sectors())
Regions = list(World.get_regions())
Factors = list(World.satellite.F.index.get_level_values(level=0))
GDP = pd.DataFrame(0, index=pd.MultiIndex.from_product([allCases,Regions], names=['Case','Region']), columns=Sectors)
CO2 = pd.DataFrame(0, index=pd.MultiIndex.from_product([allCases,Regions], names=['Case','Region']), columns=Sectors)
AllResults = {}

for s in Sectors:
    for r in Regions:
        GDP.loc[('Exiobase',r),s] = World.satellite.F.loc['Value Added',(r,s)].values
        CO2.loc[('Exiobase',r),s] = World.satellite.F.loc['CO2',(r,s)].values/(10**12)

for c in Cases:
    Input_file = 'Inputs/Cases/'+c+'.xlsx'
    WTM_World = wtm.run(World, Input_file, rexp=True)
    Results = World.wtm_results
    AllResults[c] = Results
    
    for s in Sectors:
        for r in Regions:
            GDP.loc[(c,r),s] = Results['FU'].loc['Value Added',(r,s)].values
            CO2.loc[(c,r),s] = Results['FU'].loc['CO2',(r,s)].values/(10**12)