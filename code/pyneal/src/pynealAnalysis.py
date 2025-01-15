""" Analysis Module for Pyneal Real-time Scan

These tools will set up and apply the specified analysis steps to incoming
volume data during a real-time scan

"""
import os
import sys
import logging
import importlib

import numpy as np
import nibabel as nib


class Analyzer:
    """ Analysis Class


    This is the main Analysis module that gets instantiated by Pyneal, and will
    handle executing the specific analyses throughout the scan. The specific
    analysis functions that get used will be based on the analyses specified
    in the settings dictionary that gets passed in.

    """
    def __init__(self, settings):
        """ Initialize the class

        Parameters
        ----------
        settings : dict
            dictionary that contains all of the pyneal settings for the current
            session. This dictionary is loaded/configured by the GUI once
            Pyneal is first launched

        """
        # set up logger
        self.logger = logging.getLogger('PynealLog')
        # create reference to settings dict
        self.settings = settings
        self.mask = None
        self.weightMask = False
        #for handling layers
        self.layerMasks = dict(Superior=None,Middle=None,Deep=None)
        self.layerWeights = dict(Superior=None,Middle=None,Deep=None)
        #self.layerBaseline = dict(Superior=None,Middle=None,Deep=None)

        ### Format the mask. If the settings specify that the the mask should
        # be weighted, create separate vars for the weights and mask. Convert
        # mask to boolean array
        if settings['analysisChoice'] == 'Layers':
            for l in ["Superior","Middle","Deep"]:
                if settings[f"layerMask{l}"] is None:
                    continue
                #self.layerBaseline[l] = settings[f"baselineLayer{l}"]
                mask_img = nib.load(settings[f"layerMask{l}"])
                if settings['maskIsWeighted'] is True:
                    self.weightMask = True
                    self.layerWeights[l] = mask_img.get_fdata().copy()
                    self.layerMasks[l] = mask_img.get_fdata() > 0
                else:
                    self.weightMask = False
                    self.layerMasks[l] = mask_img.get_fdata() > 0
        
        ### Set the appropriate analysis function based on the settings
        if settings['analysisChoice'] == 'Average':
            self.analysisFunc = self.averageFromMask
        elif settings['analysisChoice'] == 'Median':
            self.analysisFunc = self.medianFromMask
        elif settings['analysisChoice'] == 'Layers':
            self.analysisFunc = self.layerAnalysis
        else:
            # must be a custom analysis script
            # get the path to the custom analysis file and import it
            customAnalysisDir, customAnalysisName = os.path.split(settings['analysisChoice'])
            sys.path.append(customAnalysisDir)
            customAnalysisModule = importlib.import_module(customAnalysisName.split('.')[0])

            # create instance of customAnalysis class, pass in mask reference
            customAnalysis = customAnalysisModule.CustomAnalysis(settings['maskFile'],
                                                                 settings['maskIsWeighted'],
                                                                 settings['numTimepts'])

            # define the analysis func for the custom analysis (should be 'compute'
            # method of the customAnaylsis template)
            self.analysisFunc = customAnalysis.compute

    def runAnalysis(self, vol, volIdx, proc_flag):
        """ Analyze the supplied volume

        This is a generic function that Pyneal can call in order to execute the
        unique analysis routines setup for this session. The specific analysis
        routines are contained in the `analysisFunc` function, and will be
        set up by the `__init__` method of this class.

        Every analysisFunc will have access to the volume data and the `volIdx`
        (0-based index). Not every `analysisFunc` will use the `volIdx` for
        anything (e.g. averageFromMask),but is included anyway so that any
        custom analysis scripts that need it have access to it

        Parameters
        ----------
        vol : numpy-array
            3D array of voxel data for the current volume
        volIdx : int
            0-based index indicating where, in time (4th dimension), the volume
            belongs

        Returns
        -------
        output : dict
            dictionary containing key:value pair(s) for analysis results
            specific to the current volume

        """
        self.logger.debug('started volIdx {}'.format(volIdx))
        if proc_flag == "mc":
            output = self.analysisFunc(vol, volIdx)
            self.logger.info('analyzed volIdx {}'.format(volIdx))
        elif proc_flag == "refmask":
            mask_data = vol
            if self.settings['maskIsWeighted'] is True:
                self.weightMask = True
                self.weights = mask_data.copy()
                self.mask = mask_data > 0
            else:
                self.weightMask = False
                self.mask = mask_data > 0
            self.logger.info('Mask set in Analysis module volIdx {}'.format(volIdx))
            output= {'average': np.nan}
        else:
            self.logger.info('Skipped Analysis volIdx {}'.format(volIdx))
            output= {'average': np.nan}

        return output

    def averageFromMask(self, vol, volIdx):
        """ Compute the average voxel activation within the mask.
        Note: np.average has weights option, np.mean doesn't

        Parameters
        ----------
        vol : numpy-array
            3D array of voxel data for the current volume
        volIdx : int
            0-based index indicating where, in time (4th dimension), the volume
            belongs

        Returns
        -------
        dict
            {'weightedAverage': ####} or {'average': ####}

        """
        if self.weightMask:
            result = np.average(vol[self.mask], weights=self.weights[self.mask])
            return {'weightedAverage': np.round(result, decimals=2)}
        else:
            result = np.mean(vol[self.mask])
            return {'average': np.round(result, decimals=2)}

    def medianFromMask(self, vol, volIdx):
        """ Compute the median voxel activation within the mask

        Parameters
        ----------
        vol : numpy-array
            3D array of voxel data for the current volume
        volIdx : int
            0-based index indicating where, in time (4th dimension), the volume
            belongs

        Returns
        -------
        dict
            {'weightedMedian': ####} or {'median': ####}

        See Also
        --------
        Weighted median algorithm from: https://pypi.python.org/pypi/weightedstats/0.2

        """
        if self.weightMask:
            data = vol[self.mask]
            sorted_data, sorted_weights = map(np.array, zip(*sorted(zip(data, self.weights[self.mask]))))
            midpoint = 0.5 * sum(sorted_weights)
            if any(self.weights[self.mask] > midpoint):
                return (data[self.weights == np.max(self.weights)])[0]
            cumulative_weight = np.cumsum(sorted_weights)
            below_midpoint_index = np.where(cumulative_weight <= midpoint)[0][-1]
            if cumulative_weight[below_midpoint_index] == midpoint:
                return np.mean(sorted_data[below_midpoint_index:below_midpoint_index + 2])
            result = sorted_data[below_midpoint_index + 1]
            return {'weightedMedian': np.round(result, decimals=2)}
        else:
            # take the median of the voxels in the mask
            result = np.median(vol[self.mask])
            return {'median': np.round(result, decimals=2)}
        
    def layerAnalysis(self, vol, volIdx):
        """ Compute the average voxel activation within the layers mask.
        Note: np.average has weights option, np.mean doesn't

        Parameters
        ----------
        vol : numpy-array
            3D array of voxel data for the current volume
        volIdx : int
            0-based index indicating where, in time (4th dimension), the volume
            belongs

        Returns
        -------
        dict
            {'weightedAverage': ####} or {'average': ####}

        """
        result = dict(Superior=None,Middle=None,Deep=None)
        for l in ["Superior","Deep"]:
            if self.weightMask:
                result[l] = np.average(vol[self.layerMasks[l]], weights=self.layerWeights[self.layerMasks[l]])
            else:
                result[l] = np.mean(vol[self.layerMasks[l]])
        res = result["Superior"]/result["Deep"]
        return {'layers':{key:np.round(val, decimals=2) if val is not None else val for key,val in result.items()}}

