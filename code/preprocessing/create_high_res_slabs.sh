#!/bin/bash
#requires: FSL,AFNI
#High-res full brain roi masks -> high res slab roi masks
#Step1: Create the slab epi space reference
#Step2: Find transfrom from the full brain epi space to the slab epi space
#Step3: Cut slabs from the full-brain roi according to the slab epi ref
#Step4: Apply the xfrm from Step2 to take the full brain roi slabs to the slab epi space
export FSLOUTPUTTYPE=NIFTI
outdir=$1
indir=$2
infile=$3
cd $outdir
# remove the first 2 volumes of input EPI for magnetization stabilization
fslroi ${indir}/${infile}.nii epi_base_slab.nii 2 -1
#ensure orientation is RAS i.e. Neurological
#fslorient -forceneurological epi_base_slab.nii
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

#apply the masks and get the average
fslmeants -i epi_base_slab.nii -m roi_binary_slab.nii -o slab_bin_mask.txt
echo "************************************************************"
echo "FULL MASK BASELINE "
awk '{s+=$1}END{print "ave:",s/NR}' slab_bin_mask.txt 
awk '{s+=$1}END{print "ave:",s/NR}' slab_bin_mask.txt > slab_bin_mask_avg.txt
echo "************************************************************"

fslmeants -i epi_base_slab.nii -m roi_layer1_slab.nii -o slab_layer1_mask.txt
echo "************************************************************"
echo " LAYER 1 BASELINE "
awk '{s+=$1}END{print "ave:",s/NR}' slab_layer1_mask.txt 
awk '{s+=$1}END{print "ave:",s/NR}' slab_layer1_mask.txt > slab_layer1_mask_avg.txt
echo "************************************************************"

fslmeants -i epi_base_slab.nii -m roi_layer2_slab.nii -o slab_layer2_mask.txt
echo "************************************************************"
echo " LAYER 2 BASELINE "
awk '{s+=$1}END{print "ave:",s/NR}' slab_layer2_mask.txt 
awk '{s+=$1}END{print "ave:",s/NR}' slab_layer2_mask.txt > slab_layer2_mask_avg.txt
echo "************************************************************"

fslmeants -i epi_base_slab.nii -m roi_gm_slab.nii -o slab_gm_mask.txt
echo "************************************************************"
echo "GM BASELINE "
awk '{s+=$1}END{print "ave:",s/NR}' slab_gm_mask.txt 
awk '{s+=$1}END{print "ave:",s/NR}' slab_gm_mask.txt > slab_gm_mask_avg.txt
echo "************************************************************"
