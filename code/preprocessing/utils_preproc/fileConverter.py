import glob
import os
import shutil
import subprocess

defaults = {
    "src":"/data/pt_02900/realtime_export/20240224.27993.cb.27993.cb",
    "dest":"/data/pt_02900/rttest/scannerdata"
}
class dcm2niiRun(object):
    def __init__(self,
                src=None,
                dest=None):
        self.src_dir = src
        self.dest_dir = dest
    
    def convert(self,run=None,outname=None):
        resp = None
        if (run is not None) and (self.src_dir is not None) and (self.dest_dir is not None):
            run_id = f"{run:0>6}"
            #list of files with the specified Siemens run-id
            files = glob.glob(os.path.join(self.src_dir, f"*_{run_id}_*.dcm"))
            tmpdir = os.path.join(self.dest_dir,"_tmp") #tmp storage
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir) #remove tmp storage is it exists
            os.makedirs(tmpdir) #create temp storage
            #copy all the files
            for f in files:
                shutil.copy2(f, tmpdir)
            
            if outname is None:
                outname = run_id
            #run dcm2niix
            #-b n option for no sidecar
            command = ["dcm2niix",   
                        "-b","n",
                        "-o", self.dest_dir,
                        "-f", outname,
                        tmpdir]
            try:
                subprocess.run(command, check=True, timeout=60)
                resp = os.path.join(self.dest_dir,outname + ".nii")
            except FileNotFoundError as exc:
                print(
                    f"Command {command} failed because the process "
                    f"could not be found.\n{exc}"
                    )
            except subprocess.CalledProcessError as exc:
                print(
                    f"Command {command} failed because the process "
                    f"did not return a successful return code.\n{exc}"
                    )
            except subprocess.TimeoutExpired as exc:
                print(f"Command {command} timed out.\n {exc}")
            #delete the temp folder before exit
            shutil.rmtree(tmpdir)
        return resp
        

