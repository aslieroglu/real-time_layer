#Serves the dicoms one by one for testing pyneal scanner and pyneal connection
import shutil, os, time
basename = "001_000016_"
src = "/mnt/upload9t/USERS/RLorenz/realTimeExport/20240807.sfassnacht_zyzzyva.24.08.07_10_38_05_DST_1.3.12.2.1107.5.2.0.18951"
dst = "/home/meduser/realTimefMRI/workspace/rttest/scannerdata"
TR = 2 
for i in range(168):
    fname = f"{basename}{(i+1):0>6}.dcm"
    time.sleep(TR)
    print(f"senfing file {fname}\n")
    shutil.copyfile(os.path.join(src,fname), os.path.join(dst,fname))
