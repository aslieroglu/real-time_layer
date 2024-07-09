#!/bin/bash
#requires: AFNI, FSL, FREESURFER 7.4,LAYNII 
#The same preprocessing applied during the NFB experiment
#Repeated here for 2 purposes:
# 1. RoI masks from T1w anat 
# 2. RoI masks with dcm2niix converted dicoms

export FSLOUTPUTTYPE=NIFTI

# pre-generated files in standard space:
standard_img=/data/pt_02900/Neurofeedback/templates/synthseg/MNI152_T1_1mm.nii.gz
# generate standard_synthseg:
# mri_synthseg --i $standard_img --o $standard_synthseg --parc --threads 8
standard_synthseg=/data/pt_02900/Neurofeedback/templates/synthseg/mni_synthseg.nii
standard_roi=/data/pt_02900/Neurofeedback/templates/synthseg/SMA_std.nii


outdir=/data/pt_02900/analysis-highres/data/27993.cb/proc/highres
indir=/data/pt_02900/analysis-highres/results/tsnr_analysis
infile="27993.cb_high_res_full"
slabfile="27993.cb_high_res_slab" #to be set  na if slab scans not done for e.g. low res NFB
cd $outdir

# motion correct after removing the first 2 volumes for magnetization stabilization
fslroi ${indir}/${infile}.nii epi_base.nii 2 -1
fslmaths $standard_img standard_img
fslmaths $standard_synthseg standard_synthseg
fslmaths $standard_roi standard_roi

3dvolreg -prefix epi_base_mc.nii \
         -Fourier \
         epi_base.nii 

# average the motion corrected epi
fslmaths epi_base_mc.nii -Tmean epi_mc_avg.nii

# mri_synthreg
#mri_synthseg --i full.nii --o full_synthseg.nii --parc --threads 8
mri_synthseg --i epi_mc_avg.nii --o epi_mc_avg_synthseg.nii --parc --threads 8

# easyreg
mri_easyreg --ref standard_img.nii  \
            --ref_seg standard_synthseg.nii \
            --flo epi_mc_avg.nii \
            --flo_seg epi_mc_avg_synthseg.nii \
            --bak_field std2epi_mc_avg.nii \
            --threads 8

# transform roi
mri_easywarp --i standard_roi.nii \
             --o roi.nii \
             --field std2epi_mc_avg.nii \
             --threads 8

# threshold probabilistic ROI at 50%
# fslmaths roi.nii -thr 50 roi.nii

# the full mask binarized
fslmaths roi.nii -bin roi_binary.nii

# calculate rim
fslmaths epi_mc_avg_synthseg.nii -thr 41 -uthr 41 -bin wm_right -odt int
fslmaths epi_mc_avg_synthseg.nii -thr 2 -uthr 2 -bin wm_left -odt int
fslmaths epi_mc_avg_synthseg.nii -div 2000 gm -odt int
fslmaths wm_left -add wm_right -add 1 -add gm -add gm rim -odt int
imrm wm_left wm_right gm

# bring rim to original resolution
flirt -in rim.nii -ref epi_mc_avg.nii -usesqform -applyxfm -interp nearestneighbour -o epi_mc_avg_rim.nii

# calculate layers
LN2_LAYERS -rim epi_mc_avg_rim.nii -nr_layers 2 -output full

# combine layers with roi
fslmaths full_layers_equidist.nii -mas roi.nii roi_layers.nii

# split into both layers
fslmaths roi_layers.nii -thr 1 -uthr 1 -bin roi_layer1.nii
fslmaths roi_layers.nii -thr 2 -uthr 2 -bin roi_layer2.nii

# create gm mask
fslmaths roi_layers.nii -bin roi_gm.nii

#Now create the slab adjusted masks if slabfile is provided
#High-res full brain roi masks -> high res slab roi masks
#Step1: Create the slab epi space reference
#Step2: Find transfrom from the full brain epi space to the slab epi space
#Step3: Cut slabs from the full-brain roi according to the slab epi ref
#Step4: Apply the xfrm from Step2 to take the full brain roi slabs to the slab epi space

if [ $slabfile == "na" ]
    then
    exit 0
fi

# remove the first 2 volumes of input EPI for magnetization stabilization
fslroi ${indir}/${slabfile}.nii epi_base_slab.nii 2 -1

#MC the slab EPI
3dvolreg -prefix epi_slab_mc.nii \
        -Fourier \
        epi_base_slab.nii 
# average the MC corrected slab epi and use that as reference
fslmaths epi_slab_mc.nii -Tmean epi_slab_ref.nii

# Cut a slab from the high-res full brain ref according to the slab epi ref. Output: a slab of the high-res full brain ref
flirt -in epi_mc_avg.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o epi_ref_full2slab.nii
#now get the xfrm matrix from the high-res full brain ref slab to the slab epi space
flirt -in epi_ref_full2slab.nii -ref epi_slab_ref.nii -omat full2slab.mat -interp nearestneighbour -o epi_ref_full2slab.nii

# Cut slabs from the high-res full brain roi as per the slab epi reference. Output: a slab of the high-res full brain roi
flirt -in roi.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o roi_slab.nii
flirt -in roi_binary.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o roi_binary_slab.nii
flirt -in roi_gm.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o roi_gm_slab.nii
flirt -in roi_layer1.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o roi_layer1_slab.nii
flirt -in roi_layer2.nii -ref epi_slab_ref.nii -usesqform -applyxfm -interp nearestneighbour -o roi_layer2_slab.nii

#Now xfrm the slab of the high-res full brain roi to slab epi space roi by applying the xfrm matrix calculated earlier
flirt -in roi_slab.nii -ref epi_slab_ref.nii -o roi_slab.nii -init full2slab.mat -applyxfm -interp nearestneighbour
flirt -in roi_binary_slab.nii -ref epi_slab_ref.nii -o roi_binary_slab.nii -init full2slab.mat -applyxfm -interp nearestneighbour
flirt -in roi_gm_slab.nii -ref epi_slab_ref.nii -o roi_gm_slab.nii -init full2slab.mat -applyxfm -interp nearestneighbour
flirt -in roi_layer1_slab.nii -ref epi_slab_ref.nii -o roi_layer1_slab.nii -init full2slab.mat -applyxfm -interp nearestneighbour
flirt -in roi_layer2_slab.nii -ref epi_slab_ref.nii -o roi_layer2_slab.nii -init full2slab.mat -applyxfm -interp nearestneighbour

