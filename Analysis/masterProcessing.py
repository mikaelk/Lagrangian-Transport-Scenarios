#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 15:53:54 2020

@author: victoronink
"""
import os
from FileNaming import parameters
from FileNaming import FileNames
#%%
par=parameters(sce=int(os.environ['SCENARIO']),vic=int(os.environ['VICINITY']),
               st=int(os.environ['SHORETIME']),rt=int(os.environ['RESUSTIME']),
               sd=int(os.environ['SHOREDEPEN']),Wmin=int(os.environ['WMIN']),
               inp=int(os.environ['INPUT']),year=int(os.environ['STARTYEAR']),
               stoke=int(os.environ['STOKES']),ens=int(os.environ['ENSEMBLE']),
               simlen=int(os.environ['SIMLEN']))
par.printScenario()
FileNames.printScenario()