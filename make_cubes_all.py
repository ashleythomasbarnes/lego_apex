## Source gildas installation - outside of python
# source /vol/software/software/astro/gildas/initgildas-nov18a.sh
## Add gildas installation to python path
# export PYTHONPATH=$PYTHONPATH:/vol/software/software/astro/gildas/gildas-exe-nov18a/x86_64-ubuntu18.04-gfortran/python
##

## Import  pygildas  modeules
import pygildas
import pyclass
##

## General imports
from glob import glob
import numpy as np
import os
##

### Initial
# get the gildas command line interpreter to issue commands quickly
sic = pyclass.comm
# get the pyclass.gdict object for easy Gildas variable access
g = pyclass.gdict
# sic('SIC MESSAGE GLOBAL ON') # or OFF for less noise
###

###
inputdir = './../data/'
inputfiles = glob('%s/*.apex' %inputdir)

# These files have problems - I can not understand how to fix - ingnore for now.
ignorefiles = ['./../data/M-0104.F-9511A-2019-2019-09-26.apex', './../data/M-0104.F-9511A-2019-2019-10-03.apex']
#ignorefiles = ['']

source = 'W49'
freqs = {
        'hcn_266':  265886.180,
        'n2hp_280': 279511.701,
        '12co_231': 230538.000,
        'c18o_220': 219560.3541,
        '13co_220': 220398.6842,
         #'sio_217':  217104.9800, #not covered
        'cs_245':   244935.5565,
        'sio_261':  260518.0200,
        'hcop_268': 267557.6259,
        'hnc_272':  271981.1420
         }

lines = freqs.keys()
beff = 0.8
# https://www.apex-telescope.org/telescope/efficiency/?orderBy=mApertureEff&planetBy=all&yearBy=2019&sortAs=DESC
# Beff taken from PI230 - 2019 - Jupiter - following the outline online

for line in lines:

    print('[INFO] Reducing line: %s' %line)

    #Get frequency
    freq = freqs[line]

    ###Define output
    outputfile = './../data_processed/%s' %line
    os.system('rm %s.*' %outputfile)
    sic('file out %s.apex m' %outputfile)
    print('[INFO] Removing old output file')
    print('[INFO] Making new output file: %s' %outputfile)
    ####

    ###Loop through files - one file per date
    for inputfile in inputfiles:

        if inputfile in ignorefiles:
            print('[INFO] Ignoring file: %s' %inputfile)
            continue

        #print(inputfile)
        #continue

        #Load file and det defaults
        sic('file in %s' %inputfile)
        sic('set source %s' %source)
        sic('set tele %s' %'*')
        sic('set line %s' %'*')

        #Open and check file
        sic('find /frequency %s' %freq) #only obs with refrenecy
        if g.found == 0:
            #raise RuntimeError('No data found!')
            continue

        #Loop through spectral, baseline, and output
        inds = g.idx.ind
        sic('sic message class s-i') #! Speed-up long loops by avoiding too many screen informational messages
        for ind in inds:
            sic('get %s' %ind)
            sic('modif freq %s' %freq)
            sic('@set_apex_beam_efficiency %s' %beff)
            sic('set unit v')
            sic('extract -160 160 v') #cut out a small part of the spectra
            sic('set mo x -150 150') #only do baseline on this part
            #sic('plot')
            sic('set win -10 80')
            try:
                sic('base 1')
            except:
                continue
            sic('write')
        sic('sic message class s+i') #! Toggle back screen informational messages


    ###Regrid and output to fits file
    sic('file in %s.apex' %outputfile)
    sic('find /all')
    sic('table %s new /RESAMPLE 220 0 -100 1 velo /NOCHECK' %outputfile)
    sic('xy_map %s' %outputfile)
    sic('vector\\fits %s.fits from %s.lmv' %(outputfile, outputfile))
    ###
