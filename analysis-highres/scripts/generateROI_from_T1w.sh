#!/bin/bash
#requires: AFNI, FSL, FREESURFER 7.4,LAYNII 
#generates RoIs from anatomical. 
#Same process as online NFB runc but instead of EPI uses T1w scan for creating RoIs

export FSLOUTPUTTYPE=NIFTI

# pre-generated files in standard space:
standard_img=/data/pt_02900/Neurofeedback/templates/synthseg/MNI152_T1_1mm.nii.gz
# generate standard_synthseg:
# mri_synthseg --i $standard_img --o $standard_synthseg --parc --threads 8
standard_synthseg=/data/pt_02900/Neurofeedback/templates/synthseg/mni_synthseg.nii
standard_roi=/data/pt_02900/Neurofeedback/templates/synthseg/SMA_std.nii


outdir=/data/pt_02900/analysis-highres/results/rois
anatfile=/data/pt_02900/analysis-highres/data/sub-57/anat/anat_T1w.nii
epi_base_full=/data/pt_02900/analysis-highres/data/sub-57/proc/epi_mc_avg.nii
epi_base_slab=/data/pt_02900/analysis-highres/data/sub-57/proc/epi_slab_ref.nii
slabfile="40135.5a-08-func_bold_ref_acq-highres" #to be set  "na" if slab scans not done for e.g. low res NFB

cd $outdir
fslmaths $standard_img standard_img
fslmaths $standard_synthseg standard_synthseg
fslmaths $standard_roi standard_roi
fslmaths $anatfile anat.nii
fslmaths $epi_base_full epi_mc_avg.nii
fslmaths $epi_base_slab epi_slab_ref.nii

# mri_synthreg
#mri_synthseg --i full.nii --o full_synthseg.nii --parc --threads 8
mri_synthseg --i anat.nii --o anat_synthseg.nii --parc --threads 8

# easyreg
mri_easyreg --ref standard_img.nii  \
            --ref_seg standard_synthseg.nii \
            --flo anat.nii \
            --flo_seg anat_synthseg.nii \
            --bak_field std2anat.nii \
            --threads 8

# transform roi
mri_easywarp --i standard_roi.nii \
             --o roi.nii \
             --field std2anat.nii \
             --threads 8

# threshold probabilistic ROI at 50%
# fslmaths roi.nii -thr 50 roi.nii

# the full mask binarized
fslmaths roi.nii -bin roi_binary.nii

# calculate rim
fslmaths anat_synthseg.nii -thr 41 -uthr 41 -bin wm_right -odt int
fslmaths anat_synthseg.nii -thr 2 -uthr 2 -bin wm_left -odt int
fslmaths anat_synthseg.nii -div 2000 gm -odt int
fslmaths wm_left -add wm_right -add 1 -add gm -add gm rim -odt int
imrm wm_left wm_right gm

# bring rim to original resolution
flirt -in rim.nii -ref anat.nii -usesqform -applyxfm -interp nearestneighbour -o anat_rim.nii

# calculate layers
LN2_LAYERS -rim anat_rim.nii -nr_layers 2 -output full

# combine layers with roi
fslmaths full_layers_equidist.nii -mas roi.nii roi_layers.nii

# split into both layers
fslmaths roi_layers.nii -thr 1 -uthr 1 -bin roi_layer1.nii
fslmaths roi_layers.nii -thr 2 -uthr 2 -bin roi_layer2.nii

# create gm mask
fslmaths roi_layers.nii -bin roi_gm.nii

#Now get the anat to full epi space
flirt -in anat.nii -ref epi_mc_avg.nii -out anat2epifull.nii -omat anat2epifull.mat
#apply the xfrm matrix on the anatomical ROIs to ROIs in FUll EPI space
flirt -in roi.nii -ref epi_mc_avg.nii -o roi_full.nii -init anat2epifull.mat -applyxfm -interp nearestneighbour
flirt -in roi_binary.nii -ref epi_mc_avg.nii -o roi_binary_full.nii -init anat2epifull.mat -applyxfm -interp nearestneighbour 
flirt -in roi_gm.nii -ref epi_mc_avg.nii -o roi_gm_full.nii -init anat2epifull.mat -applyxfm -interp nearestneighbour
flirt -in roi_layer1.nii -ref epi_mc_avg.nii -o roi_layer1_full.nii -init anat2epifull.mat -applyxfm -interp nearestneighbour
flirt -in roi_layer2.nii -ref epi_mc_avg.nii -o roi_layer2_full.nii -init anat2epifull.mat -applyxfm -interp nearestneighbour

#NOW take the ROIS from full epi spcae to slab epi space
# Cut a slab from the high-res full brain ref according to the slab epi ref. Output: a slab of the high-res full brain ref
flirt -in epi_mc_avg.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o epi_ref_full2slab.nii
#now get the xfrm matrix from the high-res full brain ref slab to the slab epi space
flirt -in epi_ref_full2slab.nii -ref epi_slab_ref.nii -omat full2slab.mat -interp nearestneighbour -o epi_ref_full2slab.nii

# Cut slabs from the high-res full brain roi as per the slab epi reference. Output: a slab of the high-res full brain roi
flirt -in roi_full.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o roi_slab.nii
flirt -in roi_binary_full.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o roi_binary_slab.nii
flirt -in roi_gm_full.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o roi_gm_slab.nii
flirt -in roi_layer1_full.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o roi_layer1_slab.nii
flirt -in roi_layer2_full.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o roi_layer2_slab.nii

#Now xfrm the slab of the high-res full brain roi to slab epi space roi by applying the xfrm matrix calculated earlier
flirt -in roi_slab.nii -ref epi_slab_ref.nii -o roi_slab.nii -init full2slab.mat -applyxfm -interp nearestneighbour
flirt -in roi_binary_slab.nii -ref epi_slab_ref.nii -o roi_binary_slab.nii -init full2slab.mat -applyxfm -interp nearestneighbour
flirt -in roi_gm_slab.nii -ref epi_slab_ref.nii -o roi_gm_slab.nii -init full2slab.mat -applyxfm -interp nearestneighbour
flirt -in roi_layer1_slab.nii -ref epi_slab_ref.nii -o roi_layer1_slab.nii -init full2slab.mat -applyxfm -interp nearestneighbour
flirt -in roi_layer2_slab.nii -ref epi_slab_ref.nii -o roi_layer2_slab.nii -init full2slab.mat -applyxfm -interp nearestneighbour


