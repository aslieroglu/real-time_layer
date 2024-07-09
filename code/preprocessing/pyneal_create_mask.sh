#!/bin/bash
#requires: FSL
outdir=$1
baseline_ref=$2
baseline_mask=$3
run_ref_img=$4
xfrm_file=$5
mask_out=$6

cd $outdir

flirt -ref $run_ref_img -in $baseline_ref -omat $xfrm_file
flirt -in $baseline_mask -ref $run_ref_img -o $mask_out -init $xfrm_file -applyxfm

