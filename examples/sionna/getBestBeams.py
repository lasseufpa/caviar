#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 15:07:51 2020

Description: This code was in part copied/adapted from [1].
It reads sumoOutputFiles from the runs of a Raymobtime simulation
to generate the receivers positions that are used as input of the NN
training.
It also reads the HDF5 files generated from the Raymobtime simulation
to calculate the best Tx,Rx beam pairs 

References:
    [1] https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY.git

@author: Ilan Correa <ilan@ufpa.br>
"""

###############################################################################
#### Imports
###############################################################################
import h5py
import numpy as np
import math
import mimo_channels

###############################################################################
#### Configurations
###############################################################################
number_Tx_antennas = 32  # ULA
number_Rx_antennas = 8  # ULA

saveData = True

# TODO: update information in this module to reflect path in your PC, but do not
# commit it
import datasetInfo as d

b = h5py.File(d.hdf5File.replace("*", str(0)), "r")
#### Derived Configurations
analysis_area_x_dim = d.analysis_area[2] - d.analysis_area[0]
analysis_area_y_dim = d.analysis_area[3] - d.analysis_area[1]

b = h5py.File(d.hdf5File.replace("*", str(0)), "r")
allEpisodeData = b.get("allEpisodeData")
numScenes = allEpisodeData.shape[0]
numReceivers = allEpisodeData.shape[1]
numEpisodes = checkNumEpisodes(d.hdf5File)
numRays = allEpisodeData.shape[2]

best_ray_array = -1 * np.ones((numEpisodes, numScenes, numReceivers, 2))
dataset_rays = np.zeros((numEpisodes * numScenes * numReceivers, 2))
dataset_coordinates = np.zeros((numEpisodes * numScenes * numReceivers, 3))

dataset_ptr = 0
totalOfUsers = 0
totalOfValidUsers = 0
totalOfInvalidUsers = 0

# Get users positions corresponding to iEpisode x iScene x iUser x (x, y, angle)
users_info = getUsersInfo(d.sumoOutputFile, numEpisodes, numScenes)
users_matrix = drawSceneMap(users_info, d.analysis_area, d.sumoOutputFile)

for iEpisode in range(numEpisodes):
    currentFile = d.hdf5File.replace("*", str(iEpisode))

    print("Episode # ", iEpisode)

    b = h5py.File(currentFile, "r")
    allEpisodeData = b.get("allEpisodeData")

    for iScene in range(numScenes):
        for iRx in range(numReceivers):
            if not withinAnalysisArea(
                users_info[iEpisode, iScene, iRx, 0],
                users_info[iEpisode, iScene, iRx, 1],
                d.analysis_area,
            ):
                totalOfInvalidUsers += 1
                continue

            totalOfUsers += 1

            insiteData = allEpisodeData[iScene, iRx, :, :]

            for iRay in range(numRays):
                if np.isnan(insiteData[iRay, 0]):
                    break

            if iRay == 0:
                totalOfInvalidUsers += 1
                continue

            totalOfValidUsers += 1

            gain_in_dB = insiteData[0:iRay, 0]
            timeOfArrival = insiteData[0:iRay, 1]
            AoD_el = insiteData[0:iRay, 2]
            AoD_az = insiteData[0:iRay, 3]
            AoA_el = insiteData[0:iRay, 4]
            AoA_az = insiteData[0:iRay, 5]
            isLOSperRay = insiteData[0:iRay, 6]
            pathPhases = insiteData[0:iRay, 7]
            if insiteData.shape[1] == 8:
                RxAngle = users_info[iEpisode, iScene, iRx, 2]
            else:
                RxAngle = insiteData[0:iRay, 8][0]
            RxAngle = RxAngle + 90.0
            if RxAngle > 360.0:
                RxAngle = RxAngle - 360.0
            # Correct ULA with Rx orientation
            AoA_az = -RxAngle + AoA_az  # angle_new = - delta_axis + angle_wi;

            mimoChannel = mimo_channels.getNarrowBandULAMIMOChannel(
                AoD_az, AoA_az, gain_in_dB, number_Tx_antennas, number_Rx_antennas
            )

            # TODO: modify later here to generate pilot to be used as input dataset
            # the pilots shoul be used to predict the beam pair indexes (i,j) or Rx and Tx angles

            ## TODO: Generate as outputs the exact RX and Tx angles

            equivalentChannel = mimo_channels.getDFTOperatedChannel(
                mimoChannel, number_Tx_antennas, number_Rx_antennas
            )
            equivalentChannelMagnitude = np.abs(equivalentChannel)

            best_ray = np.argwhere(
                equivalentChannelMagnitude == np.max(equivalentChannelMagnitude)
            )
            best_ray_array[iEpisode, iScene, iRx, :] = best_ray  # not used?

            # check nan values
            if math.isnan(users_info[iEpisode][iScene][iRx][0]) or math.isnan(
                users_info[iEpisode][iScene][iRx][1]
            ):
                continue
            best_ray = np.argwhere(
                equivalentChannelMagnitude == np.max(equivalentChannelMagnitude)
            )

            # not used, but saved to keep track for each scene
            best_ray_array[iEpisode, iScene, iRx, :] = best_ray

            # Output - best beam pair
            dataset_rays[dataset_ptr, :] = best_ray

            # Inputs
            dataset_coordinates[dataset_ptr, :] = users_info[iEpisode, iScene, iRx, 0:3]

            dataset_ptr += 1

# Get only valid data and save
dataset_coordinates = dataset_coordinates[range(dataset_ptr), :]
dataset_rays = dataset_rays[range(dataset_ptr), :]

print("Position Matrix (numExamples, shapeX, ShapeY)")
print("Best Ray Array(numExamples, i, j)")
print(dataset_rays.shape)
if saveData:
    np.savez(
        d.outputFile
        + "_nTx%d" % number_Tx_antennas
        + "_nRx%d" % number_Rx_antennas
        + "_beams_output.npz",
        output_classification=dataset_rays,
    )
    np.savez(
        d.outputFile
        + "_nTx%d" % number_Tx_antennas
        + "_nRx%d" % number_Rx_antennas
        + "_coordinates_input.npz",
        input_classification=dataset_coordinates,
    )
