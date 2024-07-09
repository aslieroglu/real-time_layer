from argparse import ArgumentParser
from nipype.interfaces import spm
from nipype.interfaces import matlab
from nipype.interfaces import cat12
from nipype.interfaces.freesurfer import ApplyVolTransform, ApplyMask
import nipype.pipeline.engine as pe
import nibabel as nib
import numpy as np
import os
import shutil
import subprocess

from utils_preproc.fileConverter import dcm2niiRun

spm_path = '/afs/cbs.mpg.de/software/scripts/spm'
matlab.MatlabCommand.set_default_paths(spm_path)
tpm_template = "/data/pt_02900/Neurofeedback/templates/TPM.nii"

    
def load_niimg(niimg):
    if type(niimg) is str:
        return nib.load(niimg)
    else:
        return niimg

def normalize(niimg_in,out_file=None):
    niimg_in = load_niimg(niimg_in)
    data = niimg_in.get_fdata()
    data_norm = (data-np.min(data))/(np.max(data)-np.min(data))
    niimg_out = nib.Nifti1Image(data_norm,niimg_in.affine,niimg_in.header)
    if out_file:
        nib.save(niimg_out,out_file)
    return niimg_out

def multiply(niimg_in1, niimg_in2, out_file=None):
    niimg_in1 = load_niimg(niimg_in1)
    niimg_in2 = load_niimg(niimg_in2)
    data1 = niimg_in1.get_fdata()
    data2 = niimg_in2.get_fdata()
    data_mult = data1 * data2
    niimg_out = nib.Nifti1Image(data_mult,niimg_in1.affine,niimg_in1.header)
    if out_file:
        nib.save(niimg_out,out_file)
    return niimg_out


def mprageize(inv2_file, uni_file, out_file=None):
    """ 
    Based on Sri Kashyap (https://github.com/srikash/presurfer/blob/main/func/presurf_MPRAGEise.m)
    """
    
    # bias correct INV2
    seg = spm.NewSegment()
    seg.inputs.channel_files = inv2_file
    seg.inputs.channel_info = (0.001, 30, (False, True))
    tissue1 = ((tpm_template, 1), 2, (False,False), (False, False))
    tissue2 = ((tpm_template, 2), 2, (False,False), (False, False))
    tissue3 = ((tpm_template, 3), 2, (False,False), (False, False))
    tissue4 = ((tpm_template, 4), 3, (False,False), (False, False))
    tissue5 = ((tpm_template, 5), 4, (False,False), (False, False))
    tissue6 = ((tpm_template, 6), 2, (False,False), (False, False))
    seg.inputs.tissues = [tissue1, tissue2, tissue3, tissue4, tissue5, tissue6]    
    seg.inputs.affine_regularization = 'mni'
    seg.inputs.sampling_distance = 3
    seg.inputs.warping_regularization = [0, 0.001, 0.5, 0.05, 0.2]
    seg.inputs.write_deformation_fields = [False, False]
    seg_results = seg.run(cwd=os.path.dirname(os.path.abspath(inv2_file)))
    
    # normalize bias corrected INV2
    norm_inv2_niimg = normalize(seg_results.outputs.bias_corrected_images)
                              
    # multiply normalized bias corrected INV2 with UNI
    uni_mprageized_niimg = multiply(norm_inv2_niimg,uni_file)

    if out_file:
        nib.save(uni_mprageized_niimg,out_file)
    return uni_mprageized_niimg

    
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-src","--source",
                        help="Folder with INV and UNI dicom folders")
    parser.add_argument("-out","--outdir",
                        help="Output folder")
    parser.add_argument("-inv2",
                        help="Series no. for INV2 file")
    parser.add_argument("-uni",
                        help="Series no. for UNI file")
    
    args = parser.parse_args()
    dicom_dir = args.source
    inv2 = args.inv2
    uni = args.uni
    out_dir = args.outdir

    print("Use option -h for help")
    print("\nVERIFY THE DETAILS BELOW")
    print(f"Dicom (INV2 and UNI) folders in : {dicom_dir}")
    print(f"NIFTY INV2, UNI and T1w files in: {out_dir}")
    print(f"INV2 and UNI series are         : {inv2},{uni}")
    resp = input("\nTo continue enter y, anything else to Exit :")
    if resp != "y":
        print("User exited")
        exit(0)
    if not os.path.isdir(out_dir):
        print("Creating output directory ...\n")
        os.makedirs(out_dir)
    
    converter = dcm2niiRun(src=dicom_dir,
                            dest=out_dir)
    inv2_file = converter.convert(inv2,"INV2")
    uni_file = converter.convert(uni,"UNI")

    #create the T1w file
    T1w = os.path.join(out_dir,"T1w.nii")
    res = mprageize(inv2_file,uni_file,T1w)
    
    command = ["fsleyes","-ad",inv2_file,uni_file,T1w]
    subprocess.Popen(command,start_new_session=True,
                    stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    print("Finished and launched fsleyes.")



