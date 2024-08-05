#Serves the dicoms one by one for testing pyneal scanner and pyneal connection
import shutil, os
basename = "001_000013_00000"
src = "/home/meduser/realTimefMRI/workspace/rttest/dicoms"
dst = "/home/meduser/realTimefMRI/workspace/rttest/scannerdata"
TR = 2 
for i in range(10):
    fname = f"{basename}{i}.dcm"
    time.sleep(TR)
    print(f"senfing file {fname}\n")
    shutil.copyfile(os.path.join(src,fname), os.path.join(dst,fname))
