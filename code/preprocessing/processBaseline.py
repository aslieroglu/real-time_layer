from argparse import ArgumentParser
import os
import subprocess
import sys
import yaml

from utils_preproc.fileConverter import dcm2niiRun


if __name__ == "__main__":
    print("Use option -h for help")
    parser = ArgumentParser()
    #parser.add_argument("-src","--source",
    #                    help="Folder with epi dicom")
    parser.add_argument("config",
                        default="",
                        help="Full or relative path of Config file")
    parser.add_argument("series",
                        default="",
                        help="Series no. of the EPI file")


    args = parser.parse_args()
    series = args.series
    config_file = args.config
    config_file_dir, config_file_name = os.path.split(config_file)
    epi_name = "epi_base"
    #dicom_converter = "dicom2nifti.py"
    dicom_converter = 'own'
    # Read the config file, fail if any error with config file
    with open(config_file, 'r') as f:
        configs = yaml.safe_load(f)

    dicom_dir = configs['dicomPath']
    if not os.path.isdir(dicom_dir):
        print(f"Dicom location isnt a valid folder: {dicom_dir}")
        exit(1)
    else:
        print(f"EPI dicoms in {dicom_dir}")
    
    if not os.path.isdir(configs['outputPath']):
        print(f"Creating the output folder {configs['outputPath']}")
        os.makedirs(configs['outputPath'])
    else:
        print(f"Outputs in {configs['outputPath']}")
    
    epi_dir = os.path.join(configs['outputPath'],"func")
    if not os.path.isdir(epi_dir):
        print(f"Creating EPI folder {epi_dir}")
        os.makedirs(epi_dir)
    else:
        print(f"EPI NIFTI in {epi_dir}")
    
    if os.path.isfile(os.path.join(epi_dir,f"{epi_name}.nii.gz")):
        os.remove(os.path.join(epi_dir,f"{epi_name}.nii.gz"))
        print("Cleaned old epi_base file") 

    proc_dir = os.path.join(configs['outputPath'],"proc")
    if not os.path.isdir(proc_dir):
        print(f"Creating processed outputs folder {proc_dir}")
        os.makedirs(proc_dir)
    else:
        print(f"Processed outputs in {proc_dir}")

    if dicom_converter == "dicom2nifti.py":
        python_exec = sys.executable
        command = [python_exec, dicom_converter, config_file_dir, series, epi_dir, epi_name]
        subprocess.run(command, check=True)
    else:    
        converter = dcm2niiRun(src=dicom_dir,
                                dest=epi_dir)
        epi = converter.convert(series,epi_name)
    
    
    script = "./create_masks_deeplearn.sh"
    command = [script, proc_dir, epi_dir, epi_name]
    print("Submitted: " + " ".join(command))
    subprocess.run(command, check=True)

    os.chdir(configs['outputPath'])
    command = ["fsleyes"]
    subprocess.Popen(command,start_new_session=True,
                    stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    print("Finished and launched fsleyes.")
