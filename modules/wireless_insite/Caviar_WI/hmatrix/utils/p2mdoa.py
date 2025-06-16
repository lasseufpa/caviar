import re
import os
import collections

import numpy as np


class ParsingError(Exception):
    pass


class P2mFileParser:
    """Parser for p2m files. It currently support doa, paths and cir. Notice the regular expression in the code."""

    # project.type.tx_y.rz.p2m
    _filename_match_re = (r'^(?P<project>.*)' +
                          r'\.' +
                          r'(?P<type>((doa)|(paths)|(cir)))' +
                          r'\.' +
                          r't(?P<transmitter>\d+)'+
                          r'_' +
                          r'(?P<transmitter_set>\d+)' +
                          r'\.' +
                          r'r(?P<receiver_set>\d+)' +
                          r'\.' +
                          r'p2m$')

    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self._parse()

    def get_data_dict(self):
        return self.data

    def _parse_meta(self):
        match = re.match(P2mFileParser._filename_match_re,
                         os.path.basename(self.filename))

        self.project = match.group('project')
        self.transmitter_set = int(match.group('transmitter_set'))
        self.transmitter = int(match.group('transmitter'))
        self.receiver_set = int(match.group('receiver_set'))

    def _parse(self):
        with open(self.filename) as self.file:
            self._parse_meta()
            self._parse_header()
            self.data = collections.OrderedDict()
            for rec in range(self.n_receivers):
                self._parse_receiver()

    def _parse_header(self):
        """read the first line of the file, indicating the number of receivers"""
        line = self._get_next_line()
        self.n_receivers = int(line.strip())
    
    def get_num_receivers(self):
        """Get number of receivers"""
        if self.n_receivers is None:
            self._parse_header()  # Se n_receivers não for definido, chama o método de parsing
        return self.n_receivers

    def _parse_receiver(self):
        raise NotImplementedError()

    def _get_next_line(self):
        """Get the next uncommedted line of the file

        Call this only if a new line is expected
        """
        if self.file is None:
            raise ParsingError('File is closed')
        while True:
            next_line = self.file.readline()
            if next_line == '':
                raise ParsingError('Unexpected end of file')
            if re.search(r'^\s*#', next_line, re.DOTALL):
                continue
            else:
                return next_line

class P2MDoA(P2mFileParser):
    """Parse a p2m direction of arrival file
    > P2MDoA('iter0.doa.t001_05.r006.p2m').get_data_ndarray()
    """
    # project.type.tx_y.rz.p2m
    _filename_match_re = (r'^(?P<project>.*)' +
                          r'\.' + 
                          r'doa' + 
                          r'\.' + 
                          r't(?P<transmitter>\d+)'+
                          r'_' +
                          r'(?P<transmitter_set>\d+)' +
                          r'\.' + 
                          r'r(?P<receiver_set>\d+)' + 
                          r'\.' +
                          r'p2m$')
    
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self._parse()
        
    def get_data_ndarray(self):
        ''' return the DoA as a ndarray
        
        The array is shaped (reiceiver, path, direction) the order is the one they appear in the file
        
        If a receiver has less paths than another its path is populated with zeros
        '''
        data_ndarray = np.zeros((self.n_receivers, self.biggest_n_paths(), 3))
        for rec_idx, path_dict in enumerate(self.data.values()):
            for path_idx, direction in enumerate(path_dict.values()):
                data_ndarray[rec_idx][path_idx][:] = direction
        return data_ndarray
    
    def biggest_n_paths(self):
        ''' find the reciever with the biggest number of received paths'''
        biggest = -np.inf
        for receiver, receiver_v in self.data.items():
            n_paths = len(receiver_v)
            if n_paths > biggest:
                biggest = n_paths
        return biggest

    def _parse_receiver(self):
        line = self._get_next_line()
        receiver, n_paths = [int(i) for i in line.split()]
        self.data[receiver] = collections.OrderedDict()
        for i in range(n_paths):
            line = self._get_next_line()
            sp_line = line.split()
            path = int(sp_line[0])
            direction = np.array([float(j) for j in sp_line[1:]])
            self.data[receiver][path] = direction

if __name__=='__main__':
    doa = P2MDoA('example/iter0.doa.t001_05.r006.p2m')
    print('project: ', doa.project)
    print('transmitter set: ', doa.transmitter_set)
    print('transmitter: ', doa.transmitter)
    print('receiver set: ', doa.receiver_set)
    print(doa.get_data_ndarray())
    data_ndarray = doa.get_data_ndarray()
    print(data_ndarray[0][0][0:3])