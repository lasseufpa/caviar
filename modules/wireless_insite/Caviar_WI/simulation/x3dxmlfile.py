from xml.etree import ElementTree

from .errors import FormatError

class X3dXmlFile3_3:

    def __init__(self, file_name):
        self._file_name = file_name
        string = open(file_name, 'r').read().replace('::','__')
        with open(file_name, "w") as text_file:
            text_file.write(string)
        self._load_et(file_name)

    def _load_et(self, file_name):
        self._et = ElementTree.parse(file_name)

    def add_vertice_list(self, vertice_list, xpath, clear=True):
        point_list = self._et.findall(xpath)
        if len(point_list) != 1:
            raise FormatError(
                'xpath is not selecting only one element. xpath: "{}" selected: "{}"'.format(xpath, point_list))
        point_list = point_list[0]
        if clear:
            point_list.clear()

        def add_vertice(vertice):
            def add_point(point, name, value):
                name_element = ElementTree.SubElement(point, name)
                double = ElementTree.SubElement(name_element, 'remcom__rxapi__Double')
                double.set('Value', vertice_list.float_format_string.format(value))

            projected_point = ElementTree.SubElement(point_list, 'ProjectedPoint')
            point = ElementTree.SubElement(projected_point, 'remcom__rxapi__CartesianPoint')

            for name, value in zip(('X', 'Y', 'Z'), vertice):
                add_point(point, name, value)

        for vertice in vertice_list.vertice_array:
            add_vertice(vertice)


    def write(self, file_name):
        self._et.write(file_name, short_empty_elements=False)
        string = open(file_name, 'r').read().replace('__','::')
        with open(file_name, "w") as text_file:
            text_file.write(string)
        

class X3dXmlFile:

    def __init__(self, file_name):
        self._file_name = file_name
        self._load_et(file_name)

    def _load_et(self, file_name):
        self._et = ElementTree.parse(file_name)

    def add_vertice_list(self, vertice_list, xpath, clear=True):
        point_list = self._et.findall(xpath)
        if len(point_list) != 1:
            raise FormatError(
                'xpath is not selecting only one element. xpath: "{}" selected: "{}"'.format(xpath, point_list))
        point_list = point_list[0]
        if clear:
            point_list.clear()

        def add_vertice(vertice):
            def add_point(point, name, value):
                name_element = ElementTree.SubElement(point, name)
                double = ElementTree.SubElement(name_element, 'Double')
                double.set('Value', vertice_list.float_format_string.format(value))

            projected_point = ElementTree.SubElement(point_list, 'ProjectedPoint')
            point = ElementTree.SubElement(projected_point, 'CartesianPoint')

            for name, value in zip(('X', 'Y', 'Z'), vertice):
                add_point(point, name, value)

        for vertice in vertice_list.vertice_array:
            add_vertice(vertice)

    def write(self, file_name):
        self._et.write(file_name, short_empty_elements=False)
