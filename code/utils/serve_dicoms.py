#Serves the dicoms one by one for testing pyneal scanner and pyneal connection
import shutil, os, time
basename = "001_000013_"
src = "/home/meduser/realTimefMRI/workspace/rttest/dicoms"
dst = "/home/meduser/realTimefMRI/workspace/rttest/scannerdata"
TR = 2 
for i in range(11):
    fname = f"{basename}{(i+1):0>6}.dcm"
    time.sleep(TR)
    print(f"senfing file {fname}\n")
    shutil.copyfile(os.path.join(src,fname), os.path.join(dst,fname))
