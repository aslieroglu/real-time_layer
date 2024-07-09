# Test Data

For testing purposes, this directory includes abbreviated sample acquisitions (3 timepts) for each of the 3 scanner environments Pyneal is built to support. Each directory contains a `dummyMask.nii.gz` file built using `mkDummyMask.py` tool, and matches the dimensions of the functional data for that environment. 

## GE_env
```
GE_env/ 
├──  dummyMask.nii.gz 
└── p1  
    └── e123  
	    └── s1925 
			├── i2862280.MRDC.1
   		  	├── i2862281.MRDC.2
   		  	├── ...
``` 

**s1925** - EPI sequence

* TE: 28ms
* TR: 1000ms
* Flip Angle: 90
* Slices/Vol: 18
* Slice dims: 64 x 64 x 18
* Voxel dims: 3 x 3 x 3.8mm
* Total Vols: 3


## Philips_env
```
Philips_env/
├──  dummyMask.nii.gz 
└── 0001
    ├── Dump-0000.par
    ├── Dump-0000.rec
    ├── Dump-0001.par
    ├── Dump-0001.rec
    ├──...
```

**0001** - EPI sequence

* TR: 1000ms
* Flip Angle: 79
* Slices/Vol: 15
* Slice dims: 80 x 80 x 15
* Voxel dims: 3 x 3 x 4mm
* Total Vols: 3


## Siemens_env
```
Siemens_env/
├──  dummyMask.nii.gz   
└── funcData 
    ├── 001_000013_000001.dcm  
    ├── 001_000013_000002.dcm  
    └── 001_000013_000003.dcm  

```

**000013** - EPI sequence

* TE: 28ms
* TR: 1000ms
* Flip Angle: 90
* Slices/Vol: 18
* Slice dims: 64 x 64 x 18
* Voxel dims: 3 x 3 x 3.8mm
* Total Vols: 3


## Test Volume
```
└── testSeries.nii.gz
└── testSeries_mask.nii.gz 

```

`testVol` and `testVol_mask` are designed to assist in testing functions on the **Pyneal** side. That is, they mimic the output that **Pyneal_Scanner** would be sending to **Pyneal** during an actual scan. 

* `testSeries.nii.gz` - [64, 64, 30, 3] series
* `testSeries_mask.nii.gz` - [64, 64, 30] volume
	* this mask was made by transforming an MNI space mask of the L motor cortex (juelich probability, thresholded at 50%) to the functional space of testSeries.nii.gz. The mask contains weighted voxels, which allows us to test both weighted and binarized versions of this mask based on the how the pyneal settings dictionary is specified (i.e. the `maskIsWeighted` field). 
