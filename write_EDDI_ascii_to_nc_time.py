#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import numpy as np
import netCDF4
import datetime
import sys

def main():
    input_directory = 'path/to/ascii/files/'
    output_directory = 'path/to/output/netcdf/'
    #Read date from command line argument
    datestr=sys.argv[1]
    date = datetime.datetime.strptime(datestr,'%Y%m%d')
    # Process each ASCII file in the directory
    filenames = sorted([file for file in os.listdir(input_directory) if file.endswith('.asc')])
    ascii_file = os.path.join(input_directory, filenames[0])
    netcdf_file = os.path.join(output_directory, 'EDDI_ETrs_' + datestr + '.nc')

    datestr= ascii_file[-12:-4]

    #Read in EDDI header data
    with open(ascii_file, 'r') as EDDI_f:
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
    lon_array = np.arange(EDDI_xll,EDDI_xll+(EDDI_cs*EDDI_cols),EDDI_cs)
    lat_array = np.arange(EDDI_yll,EDDI_yll+(EDDI_cs*EDDI_rows),EDDI_cs)

    nc = netCDF4.Dataset(netcdf_file,'w',format='NETCDF4_CLASSIC')
    #Create the dimensions:
    nc.createDimension('lat',EDDI_rows)
    nc.createDimension('lon',EDDI_cols)

    ## Create the variables
    longitude_nc = nc.createVariable('lon','f8',('lon',))
    longitude_nc.long_name = 'Longitude'
    longitude_nc.units = "degrees_east"

    latitude_nc = nc.createVariable('lat','f8',('lat',))
    latitude_nc.long_name = 'Latitude'
    latitude_nc.units = 'degrees_north'

    latitude_nc[:] = lat_array
    longitude_nc[:] = lon_array

    for filename in filenames:
        ascii_file = os.path.join(input_directory, filename)
        TStype=ascii_file[-15:-13]
        TSnum=ascii_file[-17:-15]
        data = np.flipud(np.loadtxt(ascii_file,skiprows=6))
        variable_nc = nc.createVariable('EDDI_'+TSnum+TStype,'f8',('lat','lon'),fill_value=EDDI_nodata)
        variable_nc.long_name = "EDDI Z-score"
        variable_nc.units = " "
        variable_nc[:,:] = data

    ## Attributes of the NetCDF:
    nc.Name = 'EDDI for '+date.strftime('%Y/%m/%d')+'.'
    nc.Long_name = 'CONUS-wide Evaporative Demand Drought Index (EDDI) at 24 timescales (1 to 12 weeks, 1 to 12 months) for '+date.strftime("%B %d, %Y")+'.'
    nc.Units = 'z-score (Standard Normal Distribution: +ve = dry; -ve = wet)'
    nc.Conventions = "CF-1.8"
    nc.Coordinate_system = 'Geographic'

    nc.close()

main()