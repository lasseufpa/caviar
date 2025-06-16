'''
Will parse all database and create numpy arrays that represent all channels in the database.
Specificities: some episodes do not have all scenes. And some scenes do not have all receivers.
Assuming Ne episodes, with Ns scenes each, and Nr receivers (given there was only one transmitter),
there are Ne x Ns x Nr channel matrices and each must represent L=25 rays.
With Ne=119, Ns=50, Nr=10, we have 59500 matrices with 25 rays. It is better to save
each episode in one file, with the matrix given by
scene 1:Ns x Tx_index x Rx_index x numberRays and 7 numbers, the following for each ray
         path_gain
         timeOfArrival
         departure_elevation
         departure_azimuth
         arrival_elevation
         arrival_azimuth
         isLOS
to simplify we assume that all episodes have the same number of scenes (e.g. 50) and receivers (e.g. 10).
Episodes, scenes, etc, start counting from 0 (not 1).
'''
import numpy as np
import os
import os
import gc
from sqlalchemy import func
from itertools import islice
from  .utils import save5gmdata_IsolatedSim as fgdbIS

def gen_rays_dataset(run_path,step,cfg):
    
    database_folder = os.path.join(run_path, 'Data')
    
    if not os.path.exists(database_folder):
        os.makedirs(database_folder)
    
    database_path = os.path.join(database_folder, f'run{step}.db')

    numTxRxPairsPerScene = cfg.simulation.n_antenna_per_episode
    numVariablePerRay = 8 #has the ray phase now
    session = fgdbIS.open_database(database_path)
    numRaysPerTxRxPair = session.query(func.min(fgdbIS.Receiver.total_rays)).scalar()

    dataset_folder = os.path.join(database_folder)
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)
    fileNamePrefix = os.path.join(dataset_folder, f'rays_run{step}')
    matlabExtension = '.hdf5'

    numLOS = 0
    numNLOS = 0
    
    outputFileName = fileNamePrefix + matlabExtension

    allEpisodeData = np.zeros((1, numTxRxPairsPerScene, numRaysPerTxRxPair,
                            numVariablePerRay), np.float32)
    allEpisodeData.fill(np.nan)

    for rec in session.query(fgdbIS.Receiver):
        
        ray_i = 0
        isLOSChannel = 0
        for ray in islice(rec.rays, numRaysPerTxRxPair): # Iterate over a minimum number of rays for each receiver

            thisRayInfo = np.zeros(numVariablePerRay)
            thisRayInfo[0] = ray.path_gain
            thisRayInfo[1] = ray.time_of_arrival
            thisRayInfo[2] = ray.departure_elevation
            thisRayInfo[3] = ray.departure_azimuth
            thisRayInfo[4] = ray.arrival_elevation
            thisRayInfo[5] = ray.arrival_azimuth
            if ray.interactions_positions.count(',')>1:
                thisRayInfo[6] = 1
            else:
                thisRayInfo[6] = 0
            
            thisRayInfo[7] = ray.phase_in_degrees
            
            allEpisodeData[0][int(ray.receiver_id)-1][ray_i] = thisRayInfo
            ray_i += 1
            if thisRayInfo[6] == 1:
                isLOSChannel = True #if one ray is LOS, the channel is
        #print('AK:',sc_i, rec_array_idx)
        if isLOSChannel == True:
            numLOS += 1
        else:
            numNLOS += 1
    
    return allEpisodeData
    # print('==> Wrote file ' + outputFileName)
    # f = h5py.File(outputFileName, 'w')
    # f['allEpisodeData'] = allEpisodeData
    # f.close()
    
    # del ray, rec, allEpisodeData
    # gc.collect()

    