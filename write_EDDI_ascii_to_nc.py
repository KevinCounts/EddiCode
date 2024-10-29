#!/usr/bin/env python
# coding: utf-8

#Import all relevant modules
import xarray as xr
import numpy as np
import netCDF4
import glob
import sys

#Set input and output paths
indir_wk = ''
indir_mn = ''
outdir = ''

#Read date from command line argument
date=(sys.argv[1])

#Define year, month, and day from date
mnarr = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
yrout = date[0:4]
mnout = mnarr[int(date[4:6])-1]
dyout = date[6:8]

#no_data / missing data

#Create and sort weekly and monthly lists of EDDI files to be converted to a single NetCDF
files_week=sorted(glob.glob(indir_wk+'EDDI_ETrs_*wk_'+str(date)+'.asc'))
files_month=sorted(glob.glob(indir_mn+'EDDI_ETrs_*mn_'+str(date)+'.asc'))
files=files_week + files_month

#Create an evenly spaced list, 1...12
numbers=np.linspace(1,24,24).astype('int')
edData={}

#Loop through all EDDI files in weekly list
for i in range(0,len(files)):
    edData[i]=np.flipud(np.loadtxt(files[i],skiprows=6))

#Stack arrays in sequence along a third axis (time)
    edData=np.dstack(edData[i])

#Read in EDDI header data
with open(files_week[0], 'r') as EDDI_f:
    EDDI_header = EDDI_f.readlines()[:6]
#Read in variables used to define NLDAS grid
EDDI_header = [item.strip().split()[-1] for item in EDDI_header]
EDDI_cols = int(EDDI_header[0])
EDDI_rows = int(EDDI_header[1])
EDDI_xll = float(EDDI_header[2])
EDDI_yll = float(EDDI_header[3])
EDDI_cs = float(EDDI_header[4])
EDDI_nodata = float(EDDI_header[5])

#Create longitude and latitude arrays with appropriate values
lon_array=np.linspace(EDDI_xll,EDDI_xll+(EDDI_cs*EDDI_cols),EDDI_cols)
lat_array=np.linspace(EDDI_yll,EDDI_yll+(EDDI_cs*EDDI_rows),EDDI_rows)

#Create an xarray
dsEDDI = xr.Dataset(
    data_vars=dict(
        EDDI=(["lat","lon","time"], edData),
    ),
    coords=dict(
        time=(["time"],numbers),
        lat=(["lat"], lat_array),
        lon=(["lon"], lon_array),
    ))

#Rearrange dimensions to suit CF-compliance
dsEDDI=dsEDDI.transpose("time", "lat", "lon")

#Mask out all the no_data values
dsEDDI = dsEDDI.where(dsEDDI['EDDI'] > -9999.)


outfile = outdir+'EDDI_'+str(date)+'.nc'
nc = netCDF4.Dataset(outfile,'w',format='NETCDF4_CLASSIC')
#Create the dimensions:
Dtime_nc = nc.createDimension('time',1)
Dlat_nc = nc.createDimension('lat',101)
Dlon_nc = nc.createDimension('lon',201)





#Define attributes of EDDI_wk and EDDI_mn
dsEDDI.EDDI.attrs["units"] = " "
dsEDDI.EDDI.attrs["long_name"] = "Z-score, weekly EDDI"

#Define attributes of time, latitude, and longitude dimensions 
dsEDDI.time.attrs["description"] = "EDDI timescale in weeks or months: times 1-12 are 1-12 weekly EDDI timescales; times 13-24 are 1-12 monthly timescales"
dsEDDI.time.attrs["long_name"] = "EDDI timescale in weeks or 30-day months"
dsEDDI.time.attrs["units"] = "weeks or months"
dsEDDI.lat.attrs["units"] = "degrees_north"
dsEDDI.lat.attrs["long_name"] = "latitude"
dsEDDI.lon.attrs["units"] = "degrees_east"
dsEDDI.lon.attrs["long_name"] = "longitude"

#Define global attributes 
dsEDDI.attrs['Units'] = 'z-score (Standard Normal Distribution: +ve = dry; -ve = wet)'
dsEDDI.attrs['Name'] = 'EDDI for '+date[4:6]+'/'+dyout+'/'+yrout+'.'
dsEDDI.attrs['Long_name'] = 'CONUS-wide Evaporative Demand Drought Index (EDDI) at 24 timescales (1 to 12 weeks, 1 to 12 months) for '+mnout+' '+dyout+', '+yrout+'.'
dsEDDI.attrs['Conventions'] = 'CF-1.8'
dsEDDI.attrs['Coordinate system'] = 'Geographic'

outfile = outdir+'EDDI_'+str(date)+'.nc'
dsEDDI.to_netcdf(path=outfile)
dsEDDI.close()
