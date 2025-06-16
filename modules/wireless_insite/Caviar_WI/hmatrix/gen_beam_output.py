import numpy as np
import pandas as pd
import os

from .utils import (getNarrowBandUPAMIMOChannel, getCodebookOperatedChannel, rotate_vectors, import_mimo_channel,  dft_codebook_upa)

def count_hmatrix(dir):
    c = 0
    for _, _, file in os.walk(dir):
        for file in file:
            if file.startswith("hmatrix"):
                c += 1
    return c

def process_ep(path, step, c, hdf5=None):

    import_precoding = c.data_handler.antenna_arr.import_precoding
    import_hmatrix = c.data_handler.antenna_arr.import_hmatrix
    import_combining = c.data_handler.antenna_arr.import_combining
    expansion = c.data_handler.antenna_arr.expansion
    rotation = c.data_handler.antenna_arr.rotation

    normalizedAntDistance = c.data_handler.antenna_arr.normalized_antenna_distance #0.5#8
    numOfInvalidChannels = 0

    # dataHdf5_folder = os.path.join(path,'Data',f'rays_run{step}.hdf5')
    
    if  import_hmatrix:
        hmatrix_folder =  os.path.join(path,'study','HMatrixCategory')
        numReceivers = count_hmatrix(hmatrix_folder) #Cada recptor possui um ID diferente no WI
    else:
        ray_data = hdf5
        numScenes = ray_data.shape[0]
        numReceivers = ray_data.shape[1]

    hmatrix = np.nan * np.ones((numScenes, numReceivers), np.matrix)
    hmatrix = np.array(hmatrix, dtype=object)
    
    channelOutputs = np.nan * np.ones((numScenes, numReceivers, 
                                       expansion['Rx_x']*expansion['Rx_y'], 
                                       expansion['Tx_x']*expansion['Tx_y']), float)     #number_Rx_antennas,number_Tx_antennas), float)
    
    beamIndexOutputs = np.nan * np.ones((numScenes, numReceivers), dtype=object)
        
    # if false use dft codebook else use path given to .npy
    # eg import_precoding = '/home/gabrielferreiravieira/Documents/Demo/UPA-microtik-WI-Exported/codebook50-horizontal/phi_50.npy'
    if import_precoding == False:
        precoding = dft_codebook_upa(expansion['Tx_x'],expansion['Tx_y'])
    else:
        precoding = np.load(import_precoding)
    
    # if false use dft codebook else use path given to .npy
    if import_combining == False:
        combining = dft_codebook_upa(expansion['Rx_x'],expansion['Rx_y'])
    else:
        combining = np.load(import_combining)
        
    # if import channel, hmatrix.csv from WI. Mean that's a channel from 1 Tx to 1 Rx
    # eg import_hmatrix = 'hmatrix.txSet001.txPt001.rxSet002.inst001.csv'
    if import_hmatrix:
        for s in range(numScenes):
            
            hmatrix_folder =  os.path.join(path,'study','HMatrixCategory')
            
            if not os.path.exists(hmatrix_folder):
                raise FileNotFoundError(f'Not Found dir: {hmatrix_folder}')
               
            for r in range(numReceivers):
                hmatrix_file = os.path.join(hmatrix_folder, f'hmatrix.txSet001.txPt001.rxSet00{r+2}.inst001.csv')
                if not os.path.isfile(hmatrix_file):
                    print(f'File {hmatrix_file} not found')
                    continue
                try:
                    mimoChannel = import_mimo_channel(hmatrix_file)
                    equivalentChannel = getCodebookOperatedChannel(mimoChannel, precoding, combining)
                    
                    hmatrix[s,r] = np.array(mimoChannel)
                    equivalentChannelMagnitude = np.abs(equivalentChannel)
                    rx_idx, tx_idx = np.unravel_index(np.argmax(equivalentChannelMagnitude, axis=None), equivalentChannelMagnitude.shape)
                    beamIndexOutputs[s, r] = (rx_idx, tx_idx)
                    channelOutputs[s,r]=np.abs(equivalentChannel)
                except Exception as e:
                    continue
        
        return hmatrix, beamIndexOutputs, channelOutputs
            
    for s in range(numScenes):  # 10
        for r in range(numReceivers):  # 2
            insiteData = ray_data[s, r, :, :]
            numNaNsInThisChannel = sum(np.isnan(insiteData.flatten()))
            if numNaNsInThisChannel == np.prod(insiteData.shape):
                numOfInvalidChannels += 1
                continue  # next Tx / Rx pair
            if numNaNsInThisChannel > 0:
                numMaxRays = insiteData.shape[0]
                for itemp in range(numMaxRays):
                    if sum(np.isnan(insiteData[itemp].flatten())) > 0:
                        insiteData = insiteData[:itemp-1,:] #replace by smaller array without NaN
                        break
            gain_in_dB = insiteData[:, 0]
            AoD_el = insiteData[:, 2]
            AoD_az = insiteData[:, 3]
            AoA_el = insiteData[:, 4]
            AoA_az = insiteData[:, 5]
            pathPhases = insiteData[:, 7] #or None
            
            AoD_az, AoD_el = rotate_vectors(AoD_az, AoD_el, rotation['Tx_alpha'], rotation['Tx_beta'], rotation['Tx_gamma'])
            AoA_az, AoA_el = rotate_vectors(AoA_az, AoA_el, rotation['Rx_alpha'], rotation['Rx_beta'], rotation['Rx_gamma'])
            
            mimoChannel = getNarrowBandUPAMIMOChannel(AoD_el,AoD_az,AoA_el,AoA_az,
                                                        gain_in_dB,pathPhases,expansion['Tx_x'],
                                                        expansion['Tx_y'],expansion['Rx_x'],
                                                        expansion['Rx_y'],normalizedAntDistance)
            equivalentChannel = getCodebookOperatedChannel(mimoChannel, precoding, combining)

            equivalentChannelMagnitude = np.abs(equivalentChannel)
            hmatrix[s,r] = mimoChannel
            rx_idx, tx_idx = np.unravel_index(np.argmax(equivalentChannelMagnitude, axis=None), equivalentChannelMagnitude.shape)
            beamIndexOutputs[s, r] = (rx_idx, tx_idx)
            channelOutputs[s,r]=np.abs(equivalentChannel)
        
    return hmatrix[0][0], beamIndexOutputs[0][0], channelOutputs[0][0]

def gen_beam_output_file(run_path,step,cfg,hdf5=None):

    output_beam_folder = os.path.join(run_path,'Data')
    
    if not os.path.exists(output_beam_folder):
        os.makedirs(output_beam_folder)
    output_beam_list = []
    output_channel_list = []
    output_hmatrix_list = []            
    
    if not cfg.data_handler.antenna_arr.import_hmatrix:
        hmatrix,beamIndex, channel = process_ep(run_path,step, cfg, hdf5) #'100rays_180-360_60Ghz_e{ep}.hdf5'), c)
        output_hmatrix_list.append(hmatrix)
        output_beam_list.append(beamIndex)
        output_channel_list.append(channel)
    else:
        hmatrix,beamIndex, channel = process_ep(None, cfg)
        
        output_hmatrix_list.append(hmatrix)
        output_beam_list.append(beamIndex)
        output_channel_list.append(channel)
                
    # Convert lists to numpy arrays
    try:

        output_hmatrix_matrix = np.squeeze(np.array(output_hmatrix_list))
        output_beam_matrix = np.squeeze(np.array(output_beam_list))
        output_channel_matrix = np.squeeze(np.array(output_channel_list))
        
        
        # Save the output
        hmatrixOutputFileName = os.path.join(output_beam_folder, 'hmatrix.npz')
        beamOutputFileName = os.path.join(output_beam_folder, 'beam_output.npz')
        channelOutputFileName = os.path.join(output_beam_folder, 'channel_output.npz')
        np.savez(hmatrixOutputFileName, hmatrix_array=output_hmatrix_matrix)
        np.savez(channelOutputFileName, channel_array=output_channel_matrix)
        np.savez(beamOutputFileName, beam_index_array=output_beam_matrix)
    except ValueError as e:
        print(f" Error stacking hmatrix_list: {e}")