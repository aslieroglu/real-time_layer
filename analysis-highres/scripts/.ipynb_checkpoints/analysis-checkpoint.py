import sys
import logging
import io
import contextlib
from subprocess import run
import subprocess
import os
from datetime import datetime
from copy import deepcopy
import pandas as pd

import zmq
import numpy as np
import nibabel as nib
from nipy.algorithms.registration import HistogramRegistration, Rigid, resample
from fsl.wrappers import flirt, mcflirt, LOAD, fslmaths

#data folders
scandir = "/data/pt_02900/analysis-highres/NIFTY"
scan_lowres = ""
full = "40135.5a-07-func_bold_ref_acq-highres-full.nii"
slab = "40135.5a-08-func_bold_ref_acq-highres.nii"

baseline_scan_list = "/data/pt_02900/analysis-highres/scripts/baseline_scans.txt"
scan_types = ['high_res_full','high_res_slab','low_res_full']
subjects = { 'sub-57': '40135.5a',
            '27993.cb': '27993.cb'}
data_dir = "/data/pt_02900/analysis-highres/data"
nifty_dir = "NIFTY"
results_dir = "results"

def calculate_tSNR(fname):
    infile = nib.load(fname)
    mean = fslmaths(infile).Tmean().run()
    std = fslmaths(infile).Tstd().run()
    tsnr = fslmaths(mean).div(std).run()
    return tsnr

def process_baseline_scan(row):
    scan_resolution = 'high_res' if 'high' in row['scan_type'] else 'low_res'
    if 'full' in row['scan_type']:
        masks = dict(gm='roi_gm.nii',superior='roi_layer2.nii',deep='roi_layer1.nii')
    elif 'slab' in row['scan_type']:
        masks = dict(gm='roi_gm_slab.nii',superior='roi_layer2_slab.nii',deep='roi_layer1_slab.nii')

    tsnr = calculate_tSNR(os.path.join(data_dir,row['subj'],nifty_dir,row['file']))
    fname = os.path.join(data_dir,row['subj'],results_dir,f"tsnr_{row['scan_type']}.nii")
    nib.save(tsnr,fname)
    tsnr_data = tsnr.get_fdata()
    for mask_name,mask_file in masks.items():
        mask = nib.load(os.path.join(data_dir,row['subj'],results_dir,scan_resolution,mask_file))
        mask_data = mask.get_fdata()
        mask_tsnr = tsnr_data[ mask_data > 0 ]
        np.save(os.path.join(data_dir,row['subj'],results_dir,f"tsnr_{row['scan_type']}_{mask_name}.npy"),mask_tsnr)
        print(f"{row['subj']} mask {mask_name} {mask_tsnr.shape}")


basescan_df = pd.read_csv(baseline_scan_list)
basescan_df.apply(process_baseline_scan, axis=1)

"""
full_tsnr = calculate_tSNR(os.path.join(scandir,full))
slab_tsnr = calculate_tSNR(os.path.join(scandir,slab))

nib.save(full_tsnr,"full_tsnr.nii")
nib.save(slab_tsnr,"slab_tsnr.nii")
"""







