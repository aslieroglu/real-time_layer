#!/usr/bin/bash
# ----------------------------------------------------------------------
# Script: Collects Dicoms and ships to NIFTY
# Date  : Feb, 2024
# Requires: DCM2NIIX,FSLEYES
# Usage: Run once per run
#########################################################################
# Help                                                                         #
################################################################################
Help()
{
   # Display Help
   echo
   echo "Syntax: manageDicoms [-h|i|o|n|x]"
   echo "options:"
   echo "h     Print this Help and exit."
   echo "i     Folder with Dicom files."
   echo "o     Folder for depositing NIFTY file."
   echo "n     File name for NIFTY file."
   echo "x     Stops result file from opening in fsleyes"
   echo
}
# Main Program                                                                         #
################################################################################
#Defaults
show_result="Y"
out_dir=/data/hu_biswas/pt2900/pilot/24.02.24/sub-01/func
dicom_dir=/data/hu_biswas/pt2900/realtime_export/base
fname=epi_baseline
echo "use -h option for help"
echo
#process command line options
while getopts ":i:o:n:hx" flag
do
    case "${flag}" in
        o) out_dir=${OPTARG};;
        i) dicom_dir=${OPTARG};;
        n) fname=${OPTARG};;
        h) 
        Help
        exit 0;;
        x) show_result="N";;      
        ?) 
        echo "Error:Invalid option"
        exit;;
    esac
done
#alert user before continuing
echo "VERIFY THE OPTIONS BELOW:"
echo
echo "Dicom source folder: $dicom_dir"
echo "NIFTY destination folder: $out_dir"
echo "NIFTY file name: $fname"
if [[ $show_result == "Y" ]]; then
    echo "Open NIFTY file in fsleyes: Yes";
else
    echo "Open NIFTY file in fsleyes: No"
fi
echo
echo "To CONTINUE enter y or Y, any other key to Exit"
read resp;
if [[ $resp == "y" ]]||[[ $resp == "Y" ]]; then
    echo "proceeding ..."
else
    exit 0
fi
#make the output dir 
mkdir -p ${out_dir}
#cd ${dicom_dir}
#echo "looking for Dicoms in dir $PWD"
#convert to nifty and save in destination folder
dcm2niix -o ${out_dir} \
        -f ${fname}    \
        ${dicom_dir}
#Dimon -infile_pattern '*.dcm'         \
#      -gert_create_dataset            \
#      -gert_write_as_nifti            \
#      -gert_outdir ${out_dir}          \
#      -gert_to3d_prefix ${fname}

if [[ $show_result == "Y" ]]; then
    if [[ -f ${out_dir}/${fname}.nii ]]; then
        fsleyes -ad ${out_dir}/${fname}.nii &
    else
        echo "********Outfut file not generated********"
    fi
fi
time ; 
exit 0
