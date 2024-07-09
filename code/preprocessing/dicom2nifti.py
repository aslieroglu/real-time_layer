from argparse import ArgumentParser
import sys
import os

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("scanner_config",
                        default="",
                        help="Full or relative path of dir containing the scannerConfig.yaml file")
    parser.add_argument("series",
                        default="",
                        help="Series no. of the EPI file")
    parser.add_argument("out_dir",
                        default="",
                        help="Output directory of the NIFTI file")
    parser.add_argument("file_name",
                        default="",
                        help="Name of the putput file. Automatically appended with nii.gz")
    args = parser.parse_args()
    prog_file = os.path.abspath(__file__)
    prog_dir, prog_fn = os.path.split(prog_file)
    code_dir = os.path.dirname(prog_dir) #the dir with the  current program is inside the code directory
    sys.path.append(os.path.join(code_dir,"pyneal_scanner"))
    from utils.general_utils import initializeSession
    from utils.Siemens_utils import Siemens_BuildNifti

    scannerSettings, scannerDirs = initializeSession(args.scanner_config)
    # print all of the current series dirs to the terminal
    print('\n' + '*'*10)
    scannerDirs.print_currentSeries()
    print("\n")
    currentSeries = scannerDirs.getUniqueSeries()
    if not args.series.zfill(6) in currentSeries:
        print('{} is not a valid series choice!'.format(args.series))
        exit(1)

    output_fName = '{}.nii.gz'.format(args.file_name)
    # progress updates
    print('='*10)
    print('Building Nifti...')
    print('\tinput series: {}'.format(args.series))
    print('\toutput name: {}'.format(output_fName))
    # create an instance of the Siemens_NiftiBuilder
    niftiBuilder = Siemens_BuildNifti(scannerDirs.sessionDir, args.series)
    print('Successfully built Nifti image: {}\n'.format(output_fName))
    #save the nifti image
    output_path = os.path.join(args.out_dir, output_fName)
    # make sure the output dir exists
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
    niftiBuilder.write_nifti(output_path)
