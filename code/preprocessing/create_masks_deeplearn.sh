#!/bin/bash
#requires: AFNI, FSL, FREESURFER 7.4,LAYNII 
export FSLOUTPUTTYPE=NIFTI

# pre-generated files in standard space:
standard_img=/data/pt_02900/Neurofeedback/templates/synthseg/MNI152_T1_1mm.nii.gz
# generate standard_synthseg:
# mri_synthseg --i $standard_img --o $standard_synthseg --parc --threads 8
standard_synthseg=/data/pt_02900/Neurofeedback/templates/synthseg/mni_synthseg.nii
standard_roi=/data/pt_02900/Neurofeedback/templates/synthseg/SMA_std.nii

outdir=$1
indir=$2
infile=$3
cd $outdir

# motion correct after removing the first 2 volumes for magnetization stabilization
fslroi ${indir}/${infile}.nii epi_base.nii 2 -1
fslmaths $standard_img standard_img
fslmaths $standard_synthseg standard_synthseg
fslmaths $standard_roi standard_roi
#ensure RAS i.e Neurological orientation
#fslorient -forceneurological epi_base.nii 
#fslorient -forceneurological standard_img
#fslorient -forceneurological standard_synthseg
#fslorient -forceneurological standard_roi

3dvolreg -prefix ${infile}_mc.nii \
         -Fourier \
         epi_base.nii 

# average the motion corrected epi
fslmaths ${infile}_mc.nii -Tmean epi_mc_avg.nii

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


#show center of masks
echo 
echo "**************** Center in mm Coordinates ****************"
echo "roi_binary/roi"
fslstats roi_binary.nii -c
echo "roi_layer1"
fslstats roi_layer1.nii -c
echo "roi_layer2"
fslstats roi_layer2.nii -c
echo "roi_gm"
fslstats roi_gm.nii -c
echo "************************************************************"

#apply the masks and get the average
fslmeants -i epi_base.nii -m roi_binary.nii -o fullbrain_bin_mask.txt
echo "************************************************************"
echo "FULL MASK BASELINE "
awk '{s+=$1}END{print "ave:",s/NR}' fullbrain_bin_mask.txt 
awk '{s+=$1}END{print "ave:",s/NR}' fullbrain_bin_mask.txt > fullbrain_bin_mask_avg.txt
echo "************************************************************"

fslmeants -i epi_base.nii -m roi_layer1.nii -o fullbrain_layer1_mask.txt
echo "************************************************************"
echo " LAYER 1 BASELINE "
awk '{s+=$1}END{print "ave:",s/NR}' fullbrain_layer1_mask.txt 
awk '{s+=$1}END{print "ave:",s/NR}' fullbrain_layer1_mask.txt > fullbrain_layer1_mask_avg.txt
echo "************************************************************"

fslmeants -i epi_base.nii -m roi_layer2.nii -o fullbrain_layer2_mask.txt
echo "************************************************************"
echo " LAYER 2 BASELINE "
awk '{s+=$1}END{print "ave:",s/NR}' fullbrain_layer2_mask.txt 
awk '{s+=$1}END{print "ave:",s/NR}' fullbrain_layer2_mask.txt > fullbrain_layer2_mask_avg.txt
echo "************************************************************"

fslmeants -i epi_base.nii -m roi_gm.nii -o fullbrain_gm_mask.txt
echo "************************************************************"
echo "GM BASELINE "
awk '{s+=$1}END{print "ave:",s/NR}' fullbrain_gm_mask.txt 
awk '{s+=$1}END{print "ave:",s/NR}' fullbrain_gm_mask.txt > fullbrain_gm_mask_avg.txt
echo "************************************************************"



# display
#echo fsleyes --worldLoc $(fslstats roi.nii -c) full.nii  roi_layers.nii --alpha 30 --cmap random
