import re

from .errors import FormatError
from .utils import match_or_error, look_next_line

MAX_LEN_NAME = 71


class BaseObject():
    def __init__(self, name='', material=0):
        self.material = material
        self.name = name
        self.dimensions = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if len(name) > MAX_LEN_NAME:
            raise FormatError(
                'Max len for name is {}'.format(MAX_LEN_NAME))
        else:
            self._name = name


class BaseContainerObject(BaseObject):

    def __init__(self, child_type, **kargs):
        BaseObject.__init__(self, **kargs)
        # list of child entities
        self._child_list = []
        # type of child entities
        self._child_type = child_type
        # define the first line of the entity (assumes the header has only one line)
        self._begin_re = None
        # define the end of the entity header used only if _begin_re is None
        self._end_header_re = None
        # define when start parsing the entity tail
        self._begin_tail_re = None
        # define the end of entity, it None the entity ends in the end of the file
        # (if _begin_tail_re is not defined it is required, the _tail must be implemented)
        self._end_re = None
        # default header and tail strings
        self._header_str = None
        self._tail_str = None

    @property
    def _header(self):
        return self._header_str

    @property
    def _tail(self):
        return self._tail_str

    @property
    def _content(self):
        content_str = ''
        for child in self._child_list:
            content_str += child.serialize()
        return content_str

    def append(self, children):
        """Append an element to the container

        :param children: instance or iterator of instances of _child_type
        :return:
        """
        # only allow insertion of typed elements
        if self._child_type is None:
            raise NotImplementedError()
        if not isinstance(children, list):
            children = [children]

        def _check_and_add_child(child):
            if (not isinstance(child, self._child_type)):
                raise FormatError(
                    'Object is not a "{}" "{}"'.format(
                        self._child_type, child))
            self._child_list.append(child)
        for child in children:
            _check_and_add_child(child)

    def clear(self):
        self._child_list = []

    def translate(self, v):
        for child in self._child_list:
            child.translate(v)

    def serialize(self):
        mstr = ''
        mstr += self._header
        mstr += self._content
        mstr += self._tail
        return mstr

    def write(self, filename):
        with open(filename, 'w', newline='\r\n') as dst_file:
            dst_file.write(self.serialize())

    def _parse_head(self, infile):
        """Parse the start of the entity

        if _begin_re is defined read only the first line which must match _begin_re
        if _begin_re is not defined read until _end_header_re is found

        :param infile: opened input file
        :return:
        """
        self._header_str = ''
        # if _begin_re is defined it must match the first line and the processing ends
        #print(self._begin_re)
        if self._begin_re is not None:
            match_or_error(self._begin_re, infile)
        # if _begin_re is not defined read until _end_header_re
        elif self._end_header_re is not None:
            while True:
                line = look_next_line(infile)
                if line == '':
                    raise FormatError(
                        'Could not find "{}"'.format(self._end_header_re)
                    )
                if re.match(self._end_header_re, line):
                    break
                self._header_str += line
                # consumes the line
                infile.readline()

        else:
            raise NotImplementedError()

    def _parse_tail(self, infile):
        """Parse the end of the entity

        read the file until _end_re is found and save in _tail_str
        if _end_re is None the file is read until its end

        :param infile: opened input file
        :return:
        """
        self._tail_str = ''
        while True:
            line = infile.readline()
            self._tail_str += line
            if line == '':
                # if in end of file is reached and _end_re was not found
                if self._end_re is not None:
                    raise FormatError(
                        'Could not find "{}"'.format(self._end_re)
                    )
                # if _end_re is None the procesing ends
                else:
                    break
            # if _end_re is defined, search for it
            if self._end_re is not None:
                if re.match(self._end_re, line):
                    break

    def _parse_content(self, infile,mimo_id = -1):
        if mimo_id == -1:
            child = self._child_type.from_file(infile)
        else:
            child = self._child_type.from_file(infile, mimo_id)
        self.append(child)

    def __getitem__(self, key):
        for child in self._child_list:
            if child.name == key:
                return child
        raise KeyError()

    def __iter__(self):
        return iter(self._child_list)

    def keys(self):
        keys = []
        for child in self._child_list:
            keys.append(child.name)
        return keys

    def from_file(self, infile, MIMO = False):
        """Parse entity

        Parse the head and then find childs defined by:
            * if _begin_tail is defined calls _parse_tail when _begin_tail is matched
            * if _begin_tail is None _end_re must be defined and children are parsed until it is found

        :param infile: opened input file
        :return: entity instance
        """
        # consumes the entity header
    
        self._parse_head(infile)
        MIMO = MIMO
        mimo_id = -1
        while True:
            line = look_next_line(infile)
            # are we searching for the beginning of the tail
            if self._begin_tail_re is not None:
                if re.match(self._begin_tail_re, line):
                    self._parse_tail(infile)
                    break
            # if not we have to search for the end of the entity
            elif self._end_re is not None:
                if re.match(self._end_re, line):
                    infile.readline()
                    break
            # if it is not the start of the tail nor the end of the entity,
            # it is a child entity
            if MIMO:
                mimo_id += 1
                self._parse_content(infile, mimo_id=mimo_id)
            else:
                self._parse_content(infile)