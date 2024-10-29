#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by Mike Hobbins
Created on Nov 30, 2023
"""
import calendar
import os
import numpy as np
import cartopy.crs as ccrs
from matplotlib import pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.colors import ListedColormap
import cartopy.feature as cfeature
from metpy.plots import USCOUNTIES
import geopandas as gpd

#List of all stakeholders to be iterated. Switch comment with next line to focus on one stakeholder
stakeholders = ['ACF_DEWS','CBRFC','CC_DEWS','CN_DEWS','CO','DRI','DW','GCTrust','IMW_DEWS','MARFC','MCO','MN','MO','MORB_DEWS','MW_DEWS','NE_DEWS','NWS_WFO_ABQ_EPZ','NWS_WFO_EKA','NWS_WFO_PIH','NWS_WFO_RIW','NWS_WFO_TFX','NWS_WFO_UNR','PNW_DEWS','Rosebud','SE_DEWS','SOPL_DEWS','TWDB','UCRB_DEWS','USDM','USFS_CA','USFS_CA2','USFS_NWOR','USGS_NCCSC','WACLIM','WADOE','WindRiver','WWA']
#stakeholders = ['PNW_DEWS']

#Custom colormap declaration
def customdivergecolormap(clevs):
  colors = ['#730000','#E60000','#FFAA00','#FFD37F','#FFFF00','#FFFFFF','#8CCDEF','#00BFFF','#1D90FF','#4169E1','#0000FF']
  cmap = ListedColormap(colors)
  norm = BoundaryNorm(boundaries=clevs,ncolors=len(clevs)-1)
  return cmap,norm

# Parse date and time-scale parameters from filename
def parsefile(infile):
    TStype=infile[-15:-13]
    TSnum=infile[-17:-15]
    YYYY=infile[-12:-8]
    MM=infile[-8:-6]
    DD=infile[-6:-4]
    if TStype=='mn':
        TSout = 'month'
    elif TStype=='wk':
        TSout = 'week'
    else:
        print('error, timescale type not recognized')
    date=YYYY+MM.zfill(2)+(DD).zfill(2)
    outfile = "EDDI_"+str(TSnum).zfill(2)+str(TStype)+"_"+str(date)+".png"
    return outfile, TSout, TSnum, MM, DD, YYYY

# Set geographic parameters from data header
def geoparam(datain_str = []):
    nr = len(datain_str)-6
    nc = len(datain_str[6].split( ))
    ncols = int(datain_str[0][6:])
    nrows = int(datain_str[1][6:])
    xllcorner = float(datain_str[2][9:])
    yllcorner = float(datain_str[3][9:])
    cellsize = float(datain_str[4][8:])

    # Ingest EDDI data and change the sign (to force colorbar's drought->wet order)
    invar = np.zeros((nr,nc),'f')
    xx = 0
    for i in range(6,nr,1):
        split_istr = datain_str[i].split( )
        for j in range(nc):
            invar[xx,j]=-1.*float(split_istr[j])
        xx+=1
    lonin=np.linspace(xllcorner,xllcorner+(cellsize*ncols),ncols)
    latin=np.linspace(yllcorner,yllcorner+(cellsize*nrows),nrows)
    latin=np.flip(latin)
    return lonin, latin, invar

#Set the config for each stakeholder for unique differences
#Each stakeholder has a region (latlon), shapefile config lists, and if counties should be displayed (blncounties)
def getstakeholderconfig(stakeholder):
    shapedir = ''
    shapefiles = []
    color = []
    lw = []
    blncounties = True
    match stakeholder:
        case 'ACF_DEWS':
            latlon = [271.5,280,24.5,35.25]
        case 'CBRFC':
            latlon = [245.75,251.25,36.75,42.25]
        case 'CC_DEWS':
            latlon = [275.75,284.5,32.0,36.75]
        case 'CN_DEWS':
            latlon = [235.5,246,32.5,42.25]
        case 'CO':
            latlon = [250.25,258.75,36.25,41.75]
        case 'DRI':
            latlon = [235,293,25.0,53.0]
            blncounties = False
        case 'DW':
            latlon = [253.25,255.5,38.5,40.5]
            shapefiles.append(shapedir+'DW/DW_Collection_SystemWGS84.shp')
            color.append('blue')
            lw.append(.5)
            shapefiles.append(shapedir+'DW/DW_Reservoirs_WGS84.shp')
            color.append('blue')
            lw.append(.5)
            shapefiles.append(shapedir+'DW/DW_Service_WGS84.shp')
            color.append('black')
            lw.append(.5)
        case 'GCTrust':
            latlon = [245.5,253.25,33.5,41.0]
            shapefiles.append(shapedir+'GrandCanyonTrust/Plateau_Boundary/ColoradoPlateauBoundary.shp')
            color.append('green')
            lw.append(1)
        case 'IMW_DEWS':
            latlon = [244.75,258.25,31.0,45.25]
        case 'MARFC':
            latlon = [279,286.5,36.5,43.5]
        case 'MCO':
            latlon = [243.75,256.25,44.25,49.25]
        case 'MN':
            latlon = [262.5,270.75,43.25,49.5]
        case 'MO':
            latlon = [263.75,271.5,35.5,41.0]
        case 'MORB_DEWS':
            latlon = [243.75,271,35.75,49.5]
        case 'MW_DEWS':
            latlon = [264,279.5,35.75,49.75]
        case 'NE_DEWS':
            latlon = [279.25,293.25,38.75,47.5]
        case 'NWS_WFO_ABQ_EPZ':
            latlon = [250.5,257.5,28.75,37.25]
        case 'NWS_WFO_EKA':
            latlon = [234.5,238,38.75,42.50]
        case 'NWS_WFO_PIH':
            latlon = [242.47,249.25,41.81,45.54]
        case 'NWS_WFO_RIW':
            latlon = [248.75,256.25,40.75,45.25]
        case 'NWS_WFO_TFX':
            latlon = [243.5,256.5,44.0,49.5]
            shapefiles.append(shapedir+'NWS_WFO_UNR/EDDI-cities.shp')
            color.append('black')
            lw.append(.5)
            shapefiles.append(shapedir+'NWS_WFO_UNR/intrstat.shp')
            color.append('blue')
            lw.append(.5)
        case 'NWS_WFO_UNR':
            latlon = [253.96,263.7,42.49,46.04]
            shapefiles.append(shapedir+'NWS_WFO_UNR/intrstat.shp')
            color.append('blue')
            lw.append(.5)
            shapefiles.append(shapedir+'NWS_WFO_UNR/EDDI-cities.shp')
            color.append('black')
            lw.append(.5)
        case 'PNW_DEWS':
            latlon = [235.5,249,41.75,53.0]
            shapefiles.append(shapedir+'WWA/CD_2011.shp')
            color.append('grey')
            lw.append(.5)
        case 'Rosebud':
            latlon = [258.5,261.25,42.8,44.0]
            shapefiles.append(shapedir+'NWS_WFO_UNR/EDDI-cities.shp')
            color.append('black')
            lw.append(.5)
            shapefiles.append(shapedir+'NWS_WFO_UNR/intrstat.shp')
            color.append('black')
            lw.append(.5)
            shapefiles.append(shapedir+'Rosebud/Rosebud.shp')
            color.append('black')
            lw.append(.5)
        case 'SE_DEWS':
            latlon = [271.5,284.25,24.5,39.5]
        case 'SOPL_DEWS':
            latlon = [251,266.25,25.75,37.25]
        case 'TWDB':
            latlon = [253.25,266.75,25.75,36.75]
        case 'UCRB_DEWS':
            latlon = [246.5,257.5,36,46]
        case 'USDM':
            latlon = [235,293,25.0,53.0]
            blncounties = False
        case 'USFS_CA':
            latlon = [235,246.5,32.0,42.5]
            shapefiles.append(shapedir+'USFS_CA/psa_7_day.shp')
            color.append('green')
            lw.append(.5)
            shapefiles.append(shapedir+'USFS_CA/CA_FDRA_2005.shp')
            color.append('black')
            lw.append(.5)
            blncounties = False
        case 'USFS_CA2':
            latlon = [235,246.5,32.0,42.5]
            shapefiles.append(shapedir+'USFS_CA/NOPS_PSAs.shp')
            color.append('red')
            lw.append(.5)
        case 'USFS_NWOR':
            latlon = [235.5,239.75,43.25,46.75]
            shapefiles.append(shapedir+'NorthOregonCoastRangeFDRA/NorthOregonCoastRangeFDRA.shp')
            color.append('black')
            lw.append(.5)
        case 'USGS_NCCSC':
            latlon = [243.5,270.5,36.5,49.5]
        case 'WACLIM':
            latlon = [234.443875,244.339305,44.755850,49.694841]
        case 'WADOE':
            latlon = [234.443875,244.339305,44.755850,49.694841]
            shapefiles.append(shapedir+'WA/WRIA_poly.shp')
            color.append('blue')
            lw.append(.5)
            blncounties = False
        case 'WindRiver':
            latlon = [249.875,252.875,42.375,44.500]
            shapefiles.append(shapedir+'WR/Cities_WindRiver.shp')
            color.append('black')
            lw.append(.5)
            shapefiles.append(shapedir+'WR/USHighways_WindRiver.shp')
            color.append('black')
            lw.append(.25)
            shapefiles.append(shapedir+'WR/Wind_River_new_boundary.shp')
            color.append('black')
            lw.append(.5)
            shapefiles.append(shapedir+'WR/WR_and_UpperBigHorn_Basin.shp')
            color.append('blue')
            lw.append(.5)
            shapefiles.append(shapedir+'WR/WindRiver_subbasins_HU8.shp')
            color.append('blue')
            lw.append(.25)
        case 'WWA':
            latlon = [245.5,258.5,36.7,45.2]
    return latlon, shapefiles, color, lw, blncounties

def plotgen(latlon,shapefiles,color,lw,blncounties,path,dir_list,stakeholder):
    #Create one figure for each stakeholder. Set up projection to be centered in the region, extent, and shapes
    #Plots can be standard per stakholder, then the data can be added later
    proj = ccrs.LambertConformal(central_longitude=(latlon[0]+latlon[1])/2,central_latitude=(latlon[2]+latlon[3])/2)
    fig = plt.figure()
    ax = fig.add_subplot(111,projection=proj)
    ax.set_extent(latlon,crs=ccrs.PlateCarree())

    clevs1 = [-3.,-2.05374891,-1.6448363,-1.28155157,-0.8416212,-0.52440051,0.52440051,0.8416212,1.28155157,1.6448363,2.05374891,3.]
    cmap1,norm1=customdivergecolormap(clevs1)
    
    #Begin adding shapes to the map. Start with oceans, lakes, and borders
    ocean = cfeature.NaturalEarthFeature(category='physical',name='ocean',scale='50m')
    ax.add_feature(ocean,facecolor='lightgray',edgecolor='none',lw=1,zorder=15)
    lakes = cfeature.NaturalEarthFeature(category='physical',name='lakes',scale='110m')
    ax.add_feature(lakes,facecolor='lightgray',edgecolor='none',lw=1,zorder=2)
    ax.add_feature(cfeature.STATES,edgecolor='black',lw=0.5,zorder=3)
    ax.add_feature(cfeature.BORDERS,edgecolor='black',lw=0.5,zorder=4)
    #Check if counties should be displayed, then add
    if blncounties:
        ax.add_feature(USCOUNTIES.with_scale('20m'),lw=.2,zorder = 5)

    #Create loop for unique shapefiles per stakeholder. x will be used to iterate through the list of files, colors, and lineweights
    #Not all shapefiles are in the correct coordinate system. Use geopandas to re-project them to WGS84 (same as EPSG 4326)
    x=0
    for shapefile in shapefiles:
        shdf = gpd.read_file(shapefile)
        if shdf.crs != "EPSG:4326" and shdf.crs != "EPSG:4269":
            shdf = shdf.to_crs("EPSG:4326")
        SHAPES = cfeature.ShapelyFeature(shdf.geometry,ccrs.PlateCarree())
        ax.add_feature(SHAPES,facecolor='none',edgecolor=color[x],lw=lw[x])
        x+=1

    fig.text(0.9,0.00,'Generated by NOAA/OAR/Physical Sciences Laboratory',fontsize=6,va='bottom',ha='right',color='dimgrey')

    #Now that the base figure has been created, loop through all data files and plot data
    #The plot data will get overwritten every loop to create a new plot, but colorbar needs to be cleared
    for file in dir_list:
        if file.startswith("EDDI_ETrs_") and file.endswith("20240606.asc"):
            infile = path + file

            #Get file data and set figure title accordingly
            outfile, TSout, TSnum, MM, DD, YYYY = parsefile(infile)
            fin = open(infile,'r')
            datain_str = fin.readlines()
            fin.close()
            lonin, latin, invar = geoparam(datain_str)
            month_name = calendar.month_name[int(MM)]
            lonin2d, latin2d = np.meshgrid(lonin,latin)
            ax.set_title(str(int(TSnum))+"-"+TSout+' EDDI categories for '+month_name+" "+str(int(DD))+", "+YYYY, fontsize=9,weight='normal',y=1.0)
            conf = ax.pcolormesh(lonin2d,latin2d,invar,transform=ccrs.PlateCarree(),norm=norm1,cmap=cmap1)

            #Create colorbar to match data. Colorbar will be placed automatically, but labels need to be positioned specifically
            cbar = fig.colorbar(conf,ax=ax,orientation='horizontal',ticks=clevs1)
            ax.tick_params(labelsize=6,width=0.25,gridOn='True',grid_color='black',grid_lw=0.25,length=2,pad=1)
            cbar.outline.set_linewidth(0.25)
            ax.set_zorder(1)
            cbar.ax.set_xticklabels(['100%','98%','95%','90%','80%','70%','30%','20%','10%','5%','2%','0%'],fontsize=7)
            cbar.ax.text(-2.51,0.2,'ED4',fontsize=8,va='bottom',ha='center',color='white')
            cbar.ax.text(-1.85,0.2,'ED3',fontsize=8,va='bottom',ha='center',color='white')
            cbar.ax.text(-1.47,0.2,'ED2',fontsize=8,va='bottom',ha='center',color='white')
            cbar.ax.text(-1.06,0.2,'ED1',fontsize=8,va='bottom',ha='center',color='black')
            cbar.ax.text(-0.68,0.2,'ED0',fontsize=8,va='bottom',ha='center',color='black')
            cbar.ax.text(0.7,0.2,'EW0',fontsize=8,va='bottom',ha='center',color='black')
            cbar.ax.text(1.06,0.2,'EW1',fontsize=8,va='bottom',ha='center',color='black')
            cbar.ax.text(1.47,0.2,'EW2',fontsize=8,va='bottom',ha='center',color='white')
            cbar.ax.text(1.85,0.2,'EW3',fontsize=8,va='bottom',ha='center',color='white')
            cbar.ax.text(2.51,0.2,'EW4',fontsize=8,va='bottom',ha='center',color='white')

            # Add text to the colorbar
            cbar.ax.text(-3,1.1,'Drought categories',fontsize=8,va='bottom',ha='left',color='black')
            cbar.ax.text(3,1.1,'Wetness categories',fontsize=8,va='bottom',ha='right',color='black')
            cbar.ax.text(-3,-1.25,'(EDDI-percentile category breaks: 100% = driest; 0% = wettest)',fontsize=7,va='bottom',ha='left',color='black')

            #Save this figure and remove colorbar before moving on to next datafile
            plt.savefig((stakeholder + '/' +outfile),dpi=500)
            cbar.remove()
    #Close plot to free up some memory
    plt.close()

def main():
    path=''
    dir_list = os.listdir(path) # this needs to be the path where the EDDI*.asc file reside - if in that path already delete argument. May adjust argument to choose the ascii file I want.
    #Loop through all of the stakeholders and create base figure for each. Datafiles will be looped through later
    for stakeholder in stakeholders:
        latlon, shapefiles, color,lw, blncounties = getstakeholderconfig(stakeholder)
        plotgen(latlon, shapefiles, color, lw, blncounties,path,dir_list,stakeholder)

if __name__ == '__main__':
    main()