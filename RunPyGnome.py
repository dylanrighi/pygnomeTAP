#!/usr/bin/env python

import os, sys, string, math
from datetime import datetime, timedelta
import importlib

import gnome
from gnome.spill import point_line_release_spill
from gnome.outputters import Renderer, NetCDFOutput

from TAP_Setup import setup

#from batch_gnome import batch_gnome

# create command file dir if it doesn't exist
print "RootDir is", setup.RootDir

def make_dir(name):
    path = os.path.join(setup.RootDir, name)
    if not os.path.exists(path):
        os.makedirs(path)

# print "Setting up Master Command File"
# cfile = batch_gnome.CommandFile()
# cfile.SaveFilePath   = os.curdir
# cfile.SaveFileName   = setup.SaveFileName
# cfile.RunLength      = setup.TrajectoryRunLength
# cfile.NumLEs         = setup.NumLEs
# cfile.ModelTimeStep  = setup.ModelTimeStep

# NumCubes = len(setup.CubeStartSites)
NumStarts = setup.NumStarts
NumSeasons = len(setup.StartTimeFiles)

## load up our run script
sys.path.append(setup.RootDir)
script = importlib.import_module(setup.PyGnome_script)

print script
print dir(script)

model = script.make_model()

start_positions = open(os.path.join(setup.RootDir,
                                    setup.CubeStartSitesFilename)).readlines()
start_positions = [pos.split(',') for pos in start_positions]
start_positions = [( float(pos[0]), float(pos[1]) ) for pos in start_positions]

release_duration = timedelta(hours=setup.ReleaseLength)

run_time = timedelta(hours=setup.TrajectoryRunLength)
model.duration = run_time


# # loop through seasons
for Season in setup.StartTimeFiles:
    SeasonName = Season[1]
    start_times = open(Season[0],'r').readlines()[:setup.NumStarts]
    #start_times = open(os.path.join(setup.RootDir, "All_yearStarts.txt")).readlines()

    print Season

    start_dt = []
    for start_time in start_times:
        start_time = [int(i) for i in start_time.split(',')]
        start_time = datetime(start_time[2],
                              start_time[1],
                              start_time[0],
                              start_time[3],
                              start_time[4],
                              )
        start_dt.append(start_time)


    make_dir(os.path.join(setup.RootDir,setup.TrajectoriesPath,SeasonName))

    for pos_idx, start_position in enumerate(start_positions):
        OutDir = os.path.join(setup.RootDir,setup.TrajectoriesPath,SeasonName,'pos_%03i'%(pos_idx+1))
        make_dir(OutDir)

        for time_idx, start_time in enumerate(start_dt):
            print pos_idx, time_idx
            print "Running: start time:", start_time,
            print "At start location:",   start_position

            ## set the spill to the location
            spill = point_line_release_spill(num_elements=setup.NumLEs,
                                             start_position=( start_position[0], start_position[1], 0.0 ),
                                             end_position=( start_position[0]+0.4, start_position[1]+0.2, 0.0 ),
                                             release_time=start_time,
                                             end_release_time=start_time+release_duration
                                             )

            # set up the renderer location
            image_dir = os.path.join(setup.RootDir, 'Images',SeasonName, 'images_pos_%03i-time_%03i'%(pos_idx+1, time_idx))
            renderer = Renderer(os.path.join(setup.RootDir, setup.MapFileName),
                                image_dir,
                                image_size=(800, 600),
                                output_timestep=timedelta(hours=12))
            renderer.graticule.set_DMS(True)
            #renderer.viewport = ((-120.6666, 33.75),(-119.25, 34.5)) 
            make_dir(image_dir)

            # print "adding netcdf output"
            netcdf_output_file = os.path.join(OutDir,
                                              'pos_%03i-time_%03i.nc'%(pos_idx+1, time_idx),
                                              )


            model.start_time = start_time

            ## clear the old outputters
            model.outputters.clear()
#            model.outputters += renderer
            model.outputters += NetCDFOutput(netcdf_output_file,output_timestep=timedelta(hours=4))

            # clear out the old spills:
            model.spills.clear()
            model.spills+=spill

            model.full_run(rewind=True)
            # for i, step in enumerate(model):
            #     print i, step
                # print
                # for sc in model.spills.items():
                #     print "status_codes:", sc['status_codes']
                #     print "positions:", sc['positions']
                #     print "lw positions:", sc['last_water_positions']




