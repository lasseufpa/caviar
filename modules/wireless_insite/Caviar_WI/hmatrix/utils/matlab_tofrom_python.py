import numpy as np
import scipy.io as spio
'''
Code to interface Python and Matlab.
'''

def read_matrix_from_file(fileName, numRows, numColumns):
    '''
    Read in Python a real-valued matrix written in Matlab as binary file with doubles (64 bits).
    We deal here with transposing the matrix given that Matlab organizes the numbers
    ordering along columns while Python, C, etc. go along the rows.

    It assumes the file was written in Matlab with function writeFloatMatrixToBinaryFile.m below:

    function writeFloatMatrixToBinaryFile(matrix, fileName)

    fileID = fopen(fileName,'wb');
    if fileID == -1
        error(['Could not open file ' fileName])
    end
    [N,M]=size(matrix);
    fwrite(fileID, N, 'double');
    fwrite(fileID, M, 'double');
    fwrite(fileID, matrix, 'double');
    fclose(fileID);

    :param fileName: file name
    :param numRows: number of rows
    :param numColumns: number of columns
    :return: matrix of dimension numRows x numColumns
    '''
    matrix = np.fromfile(fileName,dtype=np.double)
    #there is a small header: first two values are the matrix dimension
    if matrix[0] != numRows: #check consistency
        print(matrix[0], ' != ', numRows)
        exit(-1)
    if matrix[1] != numColumns: #check consistency
        print(matrix[1], ' != ', numColumns)
        exit(-1)
    matrix = matrix[2:] #skip the header (two first values)
    #recall that it was written along columns in Matlab, so will need to transpose
    #in order to adjust to the way Python reads it in
    matrix = np.reshape(matrix,(numColumns, numRows)) #read with "transposed" shape
    matrix = matrix.T #now effectively transpose elements
    return matrix

def read_matlab_array_from_mat(fileName, arrayName):
    '''
    Read an array saved in Matlab with something like:
    save -v6 'test.mat'
    or
    save(thisFileName,'myArray','-v6')
    Note that this gives support to multidimensional complex-valued arrays.
    :param fileName: file name (test.mat in this example)
    :param arrayName: name of array of interest
    :return: numpy array
    '''
    arrays=spio.loadmat(fileName)
    x=arrays[arrayName]
    #return np.transpose(x) #scipy already transposes. No need to:
    #https://stackoverflow.com/questions/21624653/python-created-hdf5-dataset-transposed-in-matlab
    return x

if __name__ == '__main__':
    if False:
        #some example of complex-valued 3-d array called H_all in a mat file:
        fileName = 'D:/ak/Works/2018-massive-mimo/GampMatlab/trunk/code/examples/ProbitSE/test3.mat'
        arrayName = 'H_all'
        x=read_matlab_array_from_mat(fileName, arrayName)
        print(x[50,60,70])
    else:
        if True:
            #this array is complex and has shape (140, 7, 4, 2, 18, 50)
            fileName = 'D:/gits/lasse/software/mimo-matlab/clusteredChannels/802_16_outdoor/mainFolder/allChannelsEpisode1.mat'
            arrayName = 'allHs'
            x=read_matlab_array_from_mat(fileName, arrayName)
            print(x.shape)
            print(x[50,6,3,1,3,40]) #and compare with allHs(50+1,6+1,3+1,1+1,3+1,40+1) in Matlab
        else:
            #another example saved with
            #save(fileName,'ak_receivedSignal_y', 'ak_transmittedSignal_x', 'ak_channel', 'ak_noise','-v6');
            fileName = 'gamp_simulation.mat'
            arrayName = 'ak_receivedSignal_y'
            x=read_matlab_array_from_mat(fileName, arrayName)
            #Matlab: ak_receivedSignal_y(10,5,20)
            print(x[9,4,19])
