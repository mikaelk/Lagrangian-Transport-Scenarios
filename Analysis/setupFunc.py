#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 16:07:51 2020

@author: victoronink
"""
from netCDF4 import Dataset
import numpy as np
from parcels import ParticleSet,GeographicPolar,Geographic,FieldSet,Field
from particleClasses import AdvDifParticle,vicinityParticle,StochasticParticle


def FileNames(rootodirec,scenario,ensemble,startyear,Input,restart,run,
              vicinity=0,shoreTime=10,resusTime=69,shoreDepen=0,stokes=0):
    """
    A function that returns the filename of the outputfile and the restart file
    for a parcels run. 
    
    
    Parameters
    ----------
    rootodirec : string
        root directory in which everything is saved.
    scenario : int
        which beaching scenario. 0 = Advection & Diffusion Only
                                 1 = Coastal vicinity
                                 2 = Stochastic
                                 3 = Shore dependent resuspension
    ensemble : int
        Which ensemble member.
    startyear : int
        Start year of the entire simulation.
    Input : int
        Which input scenario. 0 = Jambeck
                              1 = Lebreton
    restart : int
        Which restart this is
    run : int
        Which particle subset are we dealing with.
    vicinity : int, optional
        Coastal vicinity cutoff for beaching (days). The default is 0.
    shoreTime : int, optional
        Beaching e-folding timescale (days). The default is 10.
    resusTime : int, optional
        Resuspension e-folding timescale (days). The default is 69.
    shoreDepen : int, optional
        Which shore-dependent resuspension scenario are we considering. The default is 0.
    stokes : int, optional
        Do we include stokes drift. The default is 0. 0 = Include Stokes
                                                      1 = Do not include Stokes

    Returns
    -------
    ofile, rfile = Output file name, restart file name

    """
    if scenario==0:
        prefix='AdvDifOnly'
        if stokes==1:
            prefix+='_NS'
        odirec=rootodirec+"AdvDifOnly_e_"+str(ensemble)+"/"
        ofile=odirec+prefix+"_y="+str(startyear)+"_I="+str(Input)+"_r="+str(restart)+"_run="+str(run)+".nc"
        rfile=odirec+prefix+"_y="+str(startyear)+"_I="+str(Input)+"_r="+str(restart-1)+"_run="+str(run)+".nc"
    elif scenario==1:
        prefix='Prox'
        if stokes==1:
            prefix+='_NS'
        odirec=rootodirec+"coastal_v_"+str(vicinity)+"_e_"+str(ensemble)+"/"
        ofile=odirec+prefix+"_v="+str(vicinity)+"_y="+str(startyear)+"_I="+str(Input)+"_r="+str(restart)+"_run="+str(run)+".nc"
        rfile=odirec+prefix+"_v="+str(vicinity)+"_y="+str(startyear)+"_I="+str(Input)+"_r="+str(restart-1)+"_run="+str(run)+".nc"
    elif scenario==2:
        prefix='Stochastic'
        if stokes==1:
            prefix+='_NS'
        odirec=rootodirec+"st_"+str(shoreTime)+"_rs_"+str(resusTime)+"_e_"+str(ensemble)+"/"
        ofile=odirec+prefix+"_st="+str(shoreTime)+"_rt="+str(resusTime)+"_y="+str(startyear)+"_I="+str(Input)+"_r="+str(restart)+"_run="+str(run)+".nc"
        rfile=odirec+prefix+"_st="+str(shoreTime)+"_rt="+str(resusTime)+"_y="+str(startyear)+"_I="+str(Input)+"_r="+str(restart-1)+"_run="+str(run)+".nc"
    elif scenario==3:
        prefix='SDResus'
        if stokes==1:
            prefix+='_NS'
        odirec=rootodirec+"SDResus_"+str(shoreDepen)+"/st_"+str(shoreTime)+"_rt_"+str(resusTime)+"_e_"+str(ensemble)+"/"
        ofile=odirec+prefix+"_dep="+str(shoreDepen)+"_st="+str(shoreTime)+"_rt="+str(resusTime)+"_y="+str(startyear)+"_I="+str(Input)+"_r="+str(restart)+"_run="+str(run)+".nc"
        rfile=odirec+prefix+"_dep="+str(shoreDepen)+"_st="+str(shoreTime)+"_rt="+str(resusTime)+"_y="+str(startyear)+"_I="+str(Input)+"_r="+str(restart-1)+"_run="+str(run)+".nc"

    return ofile, rfile

def removeNan(dataset,variable,lastSelec,finalTime,lastTimeSelec):
    """
    This function inputs a dataset object for the rfile. We then take the last
    non-masked value for each row, which we then use to initialise the new ofile 
    run. However, in some cases a particle has been deleted during the rfile run,
    and while that particle does stay deleted, we do need to incorporate it in
    the ofile run so that we don't misalign the rows. Therefore, in cases where
    a particle is deleted, we return varSelec with 2 for all those particles,
    since particles where particle.beach==2 will not be advected or be resuspended.
    
    Parameters
    ----------
    dataset : netcdf4 dataset object
        the dataset object we get the variable field from.
    variable : string
        name of the variable we wish to examine.
    lastSelec : int
        For each row, the index of the last unmasked cell. If there are no
        masked cells, it indicates the last cell of the .
    finalTime : datetime object
        The last timestep of the previous restart file.
    lastTimeSelec : datetime object
        the time of the last unmasked call, as indicated by the index from 
        lastSelec.

    Returns
    -------
    varSelec : array Nx1
        The restart array for the given variable to start up the ofile run.

    """
    var=np.array(dataset.variables[variable][:])
    varSelec=var[lastSelec[0],lastSelec[1]]
    varSelec[lastTimeSelec!=finalTime]=2
    return varSelec

def restartInitialPosition(rfile,restart,scenario):
    """
    Parameters
    ----------
    rfile : string
        restart file name.
    restart : int
        Which restart this is
    scenario : int
        which beaching scenario. 0 = Advection & Diffusion Only
                                 1 = Coastal vicinity
                                 2 = Stochastic
                                 3 = Shore dependent resuspension

    Returns
    -------
    TYPE
        lon_reset,lat_reset,beach_reset,age_reset,prox_reset,weight_reset
        restart arrays for longitude, latitude, beached status, particle weight,
        particle age, particle proximity to shore (for scenario 1 only)

    """
    dataset=Dataset(rfile)
    time=dataset.variables['time'][:]
    finalTime=time[0,-1]
    lastSelec=np.ma.notmasked_edges(time,axis=1)[1]
    lastTimeSelec=time[lastSelec[0],lastSelec[1]]

    lon_reset=removeNan(dataset,'lon',lastSelec,finalTime,lastTimeSelec)
    lat_reset=removeNan(dataset,'lat',lastSelec,finalTime,lastTimeSelec)
    beach_reset=removeNan(dataset,'beach',lastSelec,finalTime,lastTimeSelec)
    age_reset=removeNan(dataset,'age',lastSelec,finalTime,lastTimeSelec)
    weight_reset=removeNan(dataset,'weights',lastSelec,finalTime,lastTimeSelec)
    if scenario==1:
        prox_reset=removeNan(dataset,'prox',lastSelec,finalTime,lastTimeSelec)
    #Returning the relevant arrays    
    if scenario==1:
        return lon_reset,lat_reset,beach_reset,age_reset,prox_reset,weight_reset
    else:
        return lon_reset,lat_reset,beach_reset,age_reset,weight_reset

def CreatePSET(scenario,lons,lats,beached,age_par,weights,starttime,
               repeatStep,fieldset,prox_par=0):
    """
    Creating the

    Parameters
    ----------
    scenario : int
        which beaching scenario. 0 = Advection & Diffusion Only
                                 1 = Coastal vicinity
                                 2 = Stochastic
                                 3 = Shore dependent resuspension
    lons : array Nx1
        starting longitudes.
    lats : array Nx1
        starting latitude.
    beached : array Nx1
        started beached status. 0 = Afloat
                                1 = Beached
                                2 = Removed from simulation
    age_par : array Nx1
        particle age (s).
    weights : array Nx1
        particle weight (tons).
    prox_par : array Nx1, optional
        time spent in vicinity of coast (s). The default is 0.
    starttime : datetime
        starting date of the simulation.
    repeatStep : timedelta
        Period with which particles are released. None = particles only released
        at the beginning of the simulation
    fieldset : parcels fieldset
        fieldset containing all the relevant fields.

    Returns
    -------
    pset.

    """
    pclass={0:AdvDifParticle,1:vicinityParticle,2:StochasticParticle,3:StochasticParticle}
    if scenario==1:
        pset = ParticleSet(fieldset=fieldset, pclass=pclass[scenario], 
                           lon=lons, lat=lats,beach=beached,age=age_par,
                           prox=prox_par,weights=weights,
                           time=starttime, repeatdt=repeatStep)
    else:
        pset = ParticleSet(fieldset=fieldset, pclass=pclass[scenario], 
                           lon=lons, lat=lats,beach=beached,age=age_par,
                           weights=weights,
                           time=starttime, repeatdt=repeatStep)
    return pset

def CreateFieldSet(server,stokes,scenario):
    """
    Creating the fieldset object containing all the fields

    Parameters
    ----------
    server : int
        The server I'm running my simulations on. 0 = alphadata04
                                                  1 = ubelix
    stokes : int
        Do we include stokes drift. The default is 0. 0 = Include Stokes
                                                      1 = Do not include Stokes
    scenario : int
        which beaching scenario. 0 = Advection & Diffusion Only
                                 1 = Coastal vicinity
                                 2 = Stochastic
                                 3 = Shore dependent resuspension

    Returns
    -------
    fieldset.

    """
    #Defining the folders in which all the data is stored on the different servers
    if server==0:
        datadirec="/alphadata04/onink/lagrangian_sim/"
        dataInputdirec="/alphadata04/onink/lagrangian_sim/BeachingSim/Input/"
    elif server==1:
        datadirec="/home/ubelix/climate/shared/onink/"
        dataInputdirec="/home/ubelix/climate/shared/onink/Input/"
    
    #Loading in the surface currents and Stokes drift
    filenames = {'U': datadirec+"HYCOM/HYCOM*20*.nc",
                 'V': datadirec+"HYCOM/HYCOM*20*.nc",
                 'Ust': datadirec+"WaveWatchIIIstokes/ww3.20*_uss.nc",
                 'Vst': datadirec+"WaveWatchIIIstokes/ww3.20*_uss.nc",
                    }
    variables = {'U': 'water_u',
                 'V': 'water_v',
                 'Ust': 'uuss',
                 'Vst': 'vuss',
                    }
    dimensions = {'U':{'lat': 'lat','lon': 'lon','time': 'time','depth':'depth'},
                  'V':{'lat': 'lat','lon': 'lon','time': 'time','depth':'depth'},
                  'Ust':{'lat': 'latitude','lon': 'longitude','time': 'time'},
                  'Vst':{'lat': 'latitude','lon': 'longitude','time': 'time'},
                  }
    
    fieldset = FieldSet.from_netcdf(filenames, variables, dimensions,allow_time_extrapolation=True)
    
    ###########################################################################
    # Adding the Stokes drift to the HYCOM currents                           #
    ###########################################################################
    if stokes==0:
        fieldset.Ust.units = GeographicPolar()
        fieldset.Vst.units = Geographic()
        fieldset=FieldSet(U=fieldset.U+fieldset.Ust,
                         V=fieldset.V+fieldset.Vst,
                         )
    else:
        fieldset=FieldSet(U=fieldset.U,
                         V=fieldset.V
                         )
    ###########################################################################
    # Adding the border current, which applies for all scenarios except for 0 #
    ###########################################################################
    if scenario!=0:
        datasetBor=Dataset(dataInputdirec+'boundary_velocities_HYCOM.nc')
        borU=datasetBor.variables['MaskUvel'][:]
        borU[borU!=0]=borU[borU!=0]/abs(borU[borU!=0])
        borV=datasetBor.variables['MaskVvel'][:]
        borV[borV!=0]=borV[borV!=0]/abs(borV[borV!=0])
        borMag=np.sqrt(np.square(borU)+np.square(borV))
        nonzeroMag=borMag>0
        borMag[borMag==0]=1
        borU=np.divide(borU,borMag)
        borV=np.divide(borV,borMag)
        lonBor,latBor=datasetBor.variables['lon'][:],datasetBor.variables['lat'][:]
        fieldset.add_field(Field('borU', borU,lon=lonBor,lat=latBor,mesh='spherical'))
        fieldset.add_field(Field('borV', borV,lon=lonBor,lat=latBor,mesh='spherical'))
        fieldset.borU.units = GeographicPolar()
        fieldset.borV.units = Geographic()
    ###########################################################################
    # Adding the horizontal diffusion                                         #
    ###########################################################################
    kh=10 #m^2 s^-1, following Lacerda et al. (2019) and Liubertseva et al. (2018)
    dataset=Dataset(datadirec+'HYCOM/HYCOM_Surface_3h_2000-01-01.nc')
    uo=dataset.variables['water_u'][0,0,:,:]
    lat_kh=dataset.variables['lat'][:]
    lon_kh=dataset.variables['lon'][:]
    kh_f=kh*np.ones(uo.shape)
    kh_f[uo.mask==True]=0
    fieldset.add_field(Field('Kh_zonal', kh_f,lon=lon_kh,lat=lat_kh,mesh='spherical'))
    fieldset.add_field(Field('Kh_meridional', kh_f,lon=lon_kh,lat=lat_kh,mesh='spherical'))
    ###########################################################################
    # Adding in the  land cell identifiers                                    #
    ###########################################################################
    if scenario==0:
        landID=np.load(dataInputdirec+'land_cell_identifier.npy')
        fieldset.add_field(Field('landID', landID,lon=lonBor,lat=latBor,mesh='spherical'))
    ###########################################################################
    # Distance to the shore                                                   #
    ###########################################################################
    datasetCoast=Dataset(dataInputdirec+'distance2coast.nc')
    distance=datasetCoast.variables['distance'][0,:,:]
    lonD,latD=datasetCoast.variables['lon'][:],datasetCoast.variables['lat'][:]
    fieldset.add_field(Field('distance2shore', distance,lon=lonD,lat=latD,mesh='spherical'))
    
    ###########################################################################
    # and finally (for now), the coastline type                               #
    ###########################################################################
    if scenario==3:
        coasttype=np.load(dataInputdirec+'coastline_sand_vs_not_sand.npy')
        fieldset.add_field(Field('coasttype', coasttype,lon=lon_kh,lat=lat_kh,mesh='spherical'))
    ###########################################################################
    # Now the periodic halo for when we go across the 180/-180 degree line    #
    ###########################################################################
    fieldset.add_periodic_halo(zonal=True)

    return fieldset




