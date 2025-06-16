import numpy as np

from .errors import FormatError
from .utils import match_or_error

class BaseVerticeList:
    def __init__(self):
        self._vertice_array = None
        self.vertice_float_precision = 10

    @property
    def vertice_float_precision(self):
        return self._vertice_float_precision

    @property
    def float_format_string(self):
        return '{{:.{0}f}}'.format(self.vertice_float_precision)

    @vertice_float_precision.setter
    def vertice_float_precision(self, value):
        self._vertice_float_precision = value
        self._vertice_format_string = ' '.join([self.float_format_string for i in range(3)]) + '\n'

    @property
    def n_vertices(self):
        if self._vertice_array is None:
            return 0
        return len(self._vertice_array)

    def translate(self, v):
        self._vertice_array += v

    def clear(self):
        self._vertice_array = None

    @property
    def vertice_array(self):
        return self._vertice_array

    def add_vertice(self, v):
        if len(v) != 3:
            raise FormatError('Vertices must have 3 coordenates (x, y, z)')
        if self._vertice_array is None:
            self._vertice_array = np.array(v, ndmin=2, dtype=np.longdouble)
        else:
            self._vertice_array = np.concatenate(
                (self._vertice_array, np.array(v, ndmin=2)))

    def rotate(self, angle):
        """Rotate counterclockwise by a given angle around a given origin.

        The angle should be given in degrees.
        """
        angle = np.radians(angle)

        c = np.cos(angle)
        s = np.sin(angle)
        rot_mat = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

        for i, v in enumerate(self._vertice_array):
            self._vertice_array[i, :] = np.matmul(rot_mat, v)


class VerticeList(BaseVerticeList):

    _begin_re = r'\s*nVertices\s+(?P<nv>\d+)\s*$'

    def __init__(self):
        BaseVerticeList.__init__(self)

    def invert_direction(self):
        self._vertice_array = np.flip(self._vertice_array, 0)

    def serialize(self):
        mstr = ''
        mstr += 'nVertices {}\n'.format(self.n_vertices)
        for v in self._vertice_array:
            mstr += self._vertice_format_string.format(*v)
        return mstr

    def from_file(infile, inst=None):
        if inst is None:
            inst = VerticeList()
        vertices_match = match_or_error(VerticeList._begin_re, infile)
        n_vertices = int(vertices_match.group('nv'))

        for v in range(n_vertices):
            line = infile.readline()
            inst.add_vertice([float(i) for i in line.split()])

        return inst
