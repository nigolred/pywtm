# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 17:34:39 2020

@author: Golinucci
"""

def wtm(WIOT,f):
    import pymrio
    import pandas as pd
    
    # build the needed matrices
    
        takeall = slice(None)
    
   
    self.Y_wtm = pd.DataFrame(0, index=self.Y_agg.index, columns=self.Y_agg.columns)
    for i in self.Reg_lis:
        self.Y_wtm.loc[(i,takeall),i] = sum(self.Y_agg.loc[(j,takeall),i].values for j in self.Reg_lis)

    self.z_wtm = pd.DataFrame(0, index=self.z.index, columns=self.z.columns)
    for i in self.Reg_lis:
        self.z_wtm.loc[(i,takeall),(i,takeall)] = sum(self.z.loc[(j,takeall),(i,takeall)].values for j in self.Reg_lis)
            
    self.e_wtm = pd.DataFrame(0, pd.MultiIndex.from_product([self.Reg_lis,self.e.index]), columns=self.e.columns)
    for i in self.Reg_lis:
        self.e_wtm.loc[(i,takeall),i] = self.e.loc[takeall,(i,takeall)].values
    
    self.F_wtm = pd.DataFrame(0, pd.MultiIndex.from_product([self.Reg_lis,self.F_sect.index]), columns=self.F_sect.columns)
    for i in self.Reg_lis:
        self.F_wtm.loc[(i,takeall),i] = self.F_sect.loc[takeall,(i,takeall)].values  
  
    for i in self.Reg_lis:
        for j in self.Sec_lis:
            if sum(self.z_wtm.loc[(i,takeall),(i,j)]) == 0:
                self.z_wtm.loc[(i,takeall),(i,j)] = 9999
        
