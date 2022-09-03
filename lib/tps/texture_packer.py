from lxml.etree import *
import os
import numpy as np
from lib.console import Console
import ujson


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
        self.data: dict = {}

    def init(self):
        self.data = {'Settings':
                          {'fileFormatVersion': 5,
                           'texturePackerVersion': '6.0.1',
                           'allowRotation': True,
                           'shapeDebug': False,
                           'dpi': np.uint(72),
                           'dataFormat': 'sc_atlas',
                           'textureFileName': FileName(""),
                           'ditherType': Enum("SettingsBase::DitherType", "NearestNeighbour"),
                           'backgroundColor': np.uint(0),
                            'shapePadding': np.uint(0),
                           'jpgQuality': np.uint(80),
                           'pngOptimizationLevel': np.uint(1),
                           'textureSubPath': "",
                           'textureFormat': Enum("SettingsBase::TextureFormat", "png"),
                           'borderPadding': np.uint(0),
                           'maxTextureSize': QSize(2048, 2048),
                           'fixedTextureSize': QSize(-1, -1),
                           'algorithmSettings':
                               {'AlgorithmSettings':
                                    {'algorithm': Enum("AlgorithmSettings::AlgorithmId", "Polygon"),
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
                                              {'alignToGrid': np.uint(1)}}}},
                           'dataFileNames': Map("GFileNameMap", [["json"]], [{"DataFile": {"name": FileName("")}}]),
                           'multiPack': True,
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
                                     'extrude': np.uint(1),
                                     'trimThreshold': np.uint(1),
                                     'trimMargin': np.uint(10),
                                     'trimMode': Enum("SpriteSettings::TrimMode", "Trim"),
                                     'tracerTolerance': 700,
                                     'heuristicMask': False,
                                     'defaultPivotPoint': PointF(0.5, 0.5),
                                     'writePivotPoints': False}},
                           'individualSpriteSettings': Map("IndividualSpriteSettingsMap", [], []),
                           'fileList': [],
                           'ignoreFileList': [],
                           'replaceList': [],
                           'ignoredWarnings': [],
                            'exporterProperties': Map("ExporterProperties", [["sc_atlas::downscaling", "sc_atlas::linear"],
                                                                             ["sc_atlas::max_filter", "sc_atlas::min_filter"]],
                                                      [{"ExporterProperty": {"value": "true"}}, {"ExporterProperty": {"value": "LINEAR"}}])}}

    def load(self, filepath: str):
        parsed = parse(filepath)
        xml = parsed.getroot()

        for variable in xml:
            data_set = load_variable(variable)
            data_key = list(data_set)[0]
            self.data[data_key] = data_set[data_key]

    def save(self, filepath: str):
        root = Element("data", {"version": "1.0"})

        for data_key in self.data:
            root.append(write_variable({data_key: self.data[data_key]}))

        ElementTree(root).write(filepath, xml_declaration = True, encoding='UTF-8', pretty_print = True)

    def create_atlas(self, filenames: list, output_path: str, project_name: str):
        os.chdir(output_path)
        project_file = f"{output_path}/{project_name}.tps"
        settings = self.data['Settings']

        settings['fileList'] = []
        for file in filenames:
            settings['fileList'].append(FileName(file))

        self.save(project_file)
        Console.info(f"Please open {project_file} in Texture Packer, publish sprite sheet with your settings, save project and press any button in console...\nFor details, you can look at our github")
        while True:
            input()
            temp = TexturePackerProject()
            temp.load(project_file)
            data_names = temp.data["Settings"]["dataFileNames"]
            for i, keys in enumerate(data_names.keys):
                if "json" in keys:
                    data_files = data_names.values[i]
                    if "DataFile" in data_files:
                        path = data_files["DataFile"]["name"].filename
                        if path:
                            abs_path = os.path.abspath(path)
                            if os.path.exists(abs_path):
                                Console.info("Sheet successfully found.")
                                return ujson.load(open(abs_path, "r"))

                Console.error("Something is wrong with project. Try again.")






