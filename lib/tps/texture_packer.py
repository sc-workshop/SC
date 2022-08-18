from lxml.etree import *
from os import path
import numpy as np


class Enum:
    def __init__(self, key=None, value=None) -> None:
        self.key = key
        self.value = value


class Map:
    def __init__(self, type: str, keys: list, values: list) -> None:
        self.type = type

        self.keys = keys
        self.values = values


class Rect:
    def __init__(self, left: int, right: int, bottom: int, top: int) -> None:
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top


class PointF:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class QSize:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height


class FileName:
    def __init__(self, filename: str) -> None:
        self.filename = filename


def load_variable(variable):
    tag = variable.tag

    if tag == 'string':
        if not variable.text:
            return ""
        return variable.text

    elif tag == 'int':
        return int(variable.text)

    elif tag == "uint":
        return np.uint(int(variable.text))

    elif tag == 'true':
        return True

    elif tag == 'false':
        return False

    elif tag == 'double':
        return float(variable.text)

    elif tag == 'array':
        return [load_variable(var) for var in variable]

    elif tag == 'enum':
        return Enum(variable.attrib["type"], variable.text)

    elif tag == 'map':
        map_keys = []
        map_values = []

        active_key_index = 0
        active_key = False
        for i, map_key in enumerate(variable):
            if map_key.tag == "key":
                if active_key:
                    map_keys[active_key_index].append(map_key.text)
                else:
                    active_key = True
                    map_keys.append([map_key.text])
                    active_key_index = map_keys.index([map_key.text])
            else:
                active_key = False
                map_values.append(load_variable(map_key))

        return Map(variable.attrib['type'], map_keys, map_values)

    elif tag == 'struct':
        return {variable.attrib["type"]:
                    {struct_var.text: load_variable(variable[i + 1]) for i, struct_var in enumerate(variable) if struct_var.tag == "key"}}

    elif tag == 'rect':
        point = variable.text.split(',')
        return Rect(float(point[0]), float(point[1]), float(point[2]), float(point[3]))

    elif tag == 'point_f':
        point = variable.text.split(',')
        return PointF(float(point[0]), float(point[1]))

    elif tag == 'QSize':
        width = 0
        height = 0
        for i, key in enumerate(variable):
            if key.tag == "key":
                if key.text == "width":
                    width = load_variable(variable[i + 1])
                elif key.text == "height":
                    height = load_variable(variable[i + 1])

        return QSize(width, height)

    elif tag == 'filename':
        return FileName(variable.text)

    else:
        raise TypeError(f"Unknown TexturePacker data type {tag}!")

def write_variable(variable):

    if isinstance(variable, bool):
        element = Element('true' if variable else 'false')

    elif isinstance(variable, str):
        element = Element('string')
        element.text = variable

    elif isinstance(variable, int):
        element = Element('int')
        element.text = str(variable)

    elif isinstance(variable, np.uint):
        element = Element('uint')
        element.text = str(variable)

    elif isinstance(variable, float):
        element = Element('double')
        element.text = str(variable)

    elif isinstance(variable, Enum):
        element = Element('enum', {"type": variable.key})
        element.text = variable.value

    elif isinstance(variable, list):
        element = Element("array")
        for array in variable:
            element.append(write_variable(array))

    elif isinstance(variable, Map):
        element = Element("map", {'type': variable.type})

        for keys, value in zip(variable.keys, variable.values):
            for key in keys:
                map_key = Element('key')
                map_key.text = key
                element.append(map_key)
            element.append(write_variable(value))

    elif isinstance(variable, dict):
        key = list(variable)[0]
        element = Element('struct', {'type': key})
        for value in variable[key]:
            key_element = Element("key")
            key_element.text = value
            element.append(key_element)
            element.append(write_variable(variable[key][value]))

    elif isinstance(variable, Rect):
        element = Element('rect')
        element.text = f"{variable.left},{variable.right},{variable.top},{variable.bottom}"

    elif isinstance(variable, PointF):
        element = Element("point_f")
        element.text = f"{variable.x},{variable.y}"

    elif isinstance(variable, QSize):
        element = Element("QSize")
        width = Element("key")
        width.text = "width"
        height = Element("key")
        height.text = "height"

        element.append(width)
        element.append(write_variable(variable.width))
        element.append(height)
        element.append(write_variable(variable.height))

    elif isinstance(variable, FileName):
        element = Element("filename")
        element.text = variable.filename

    else:
        raise TypeError(f"Unknown data type {type(variable)}")

    return element

class TexturePackerProject:
    def __init__(self) -> None:
        self.data: list = []

    def init(self):
        self.data = [{'Settings':
                          {'fileFormatVersion': 5,
                           'texturePackerVersion': '6.0.1',
                           'allowRotation': True,
                           'shapeDebug': False,
                           'dpi': 72,
                           'dataFormat': 'json-array',
                           'textureFileName': FileName(""),
                           'ditherType': Enum("SettingsBase::DitherType", "NearestNeighbour"),
                           'backgroundColor': 0,
                            'shapePadding': 0,
                           'jpgQuality': 80,
                           'pngOptimizationLevel': 1,
                           'textureSubPath': "",
                           'textureFormat': Enum("SettingsBase::TextureFormat", "png"),
                           'borderPadding': 0,
                           'maxTextureSize': QSize(2048, 2048),
                           'fixedTextureSize': QSize(-1, -1),
                           'algorithmSettings':
                               {'AlgorithmSettings':
                                    {'algorithm': Enum("AlgorithmSettings::AlgorithmId", "MaxRects"),
                                     'freeSizeMode': Enum("AlgorithmSettings::AlgorithmFreeSizeMode", "Best"),
                                     'sizeConstraints': Enum("AlgorithmSettings::SizeConstraints", "AnySize"),
                                     'forceSquared': False,
                                     'maxRects':
                                         {'AlgorithmMaxRectsSettings':
                                              {'heuristic': Enum("AlgorithmMaxRectsSettings::Heuristic", "Best")}},
                                     'basic':
                                         {'AlgorithmBasicSettings':
                                              {'sortBy': Enum("AlgorithmBasicSettings::SortBy", "Best"),
                                               'order': Enum("AlgorithmBasicSettings::Order", "Ascending")}},
                                     'polygon':
                                         {'AlgorithmPolygonSettings':
                                              {'alignToGrid': 1}}}},
                           'dataFileNames': Map("GFileNameMap", ["data"], [[{"DataFile": {"name": FileName()}}]]),
                           'multiPack': False,
                           'forceIdenticalLayout': False,
                           'outputFormat': Enum("SettingsBase::OutputFormat", "RGBA8888"),
                           'alphaHandling': Enum("SettingsBase::AlphaHandling", "ClearTransparentPixels"),
                            'trimSpriteNames': False,
                           'prependSmartFolderName': False,
                           'autodetectAnimations': True,
                           'globalSpriteSettings':
                               {'SpriteSettings':
                                    {'scale': 1.0,
                                     'scaleMode': Enum("ScaleMode", "Smooth"),
                                     'extrude': 1,
                                     'trimThreshold': 1,
                                     'trimMargin': 1,
                                     'trimMode': Enum("SpriteSettings::TrimMode", "Trim"),
                                     'tracerTolerance': 200,
                                     'heuristicMask': False,
                                     'defaultPivotPoint': PointF(0.5, 0.5),
                                     'writePivotPoints': False}},
                           'individualSpriteSettings': Map("IndividualSpriteSettingsMap", [], []),
                           'fileList': [],
                           'ignoreFileList': [],
                           'replaceList': [],
                           'ignoredWarnings': [],
                            'exporterProperties': Map("ExporterProperties", [], [])}}]

    def load(self, filepath: str):
        parsed = parse(filepath)
        xml = parsed.getroot()

        for variable in xml:
            self.data.append(load_variable(variable))

    def save(self, filepath: str):
        root = Element("data", {"version": "1.0"})

        for data_set in self.data:
            root.append(write_variable(data_set))

        ElementTree(root).write(filepath, xml_declaration = True, encoding='UTF-8', pretty_print = True)
