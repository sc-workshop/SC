from xml.etree.ElementTree import *
from os import path
import numpy as np


class enum:
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def save(self):
        res = Element("enum", {"type": str(self.key)})
        res.text = str(self.value)
        return res


class map:
    def __init__(self, type=None, keys=[], values=[]):
        self.type = type
        self.keys = keys
        self.values = values

    def save(self):
        res = Element("map", {"type": self.type})

        return res


class point_f:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def save(self):
        res = Element("point_f")
        res.text = f"{self.x},{self.y}"
        return res


class filename:
    def __init__(self):
        self.filepath = None

    def save(self):
        res = Element("filename")
        if self.filepath is not None:
            res.text = path.relpath(self.filepath)

        return res


class rect:
    def __init__(self):
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0

    def save(self):
        res = Element("rect")
        res.text = f"{self.left},{self.right},{self.top},{self.bottom}"
        return res


class packer_project:
    def __init__(self):
        self.file_version = 5

        self.packer_version = "6.0.0"

        self.allow_rotation = True

        self.shape_debug = False

        self.data_format = "sc_export"

        self.texture_file_name = filename()

        self.shape_padding = np.uint(0)

        self.png_optimization = np.uint(0)

        self.texture_format = enum("SettingsBase::TextureFormat", "png")

        self.border_padding = np.uint(0)

        self.max_texture_size = [4096, 4096]  # QSize

        self.fixed_texture_size = [-1, -1]  # QSize

        self.algorithm_settings = {"AlgorithmSettings": {"algorithm": enum("AlgorithmSettings::AlgorithmId", "Polygon"),
                                                         "freeSizeMode": enum(
                                                             "AlgorithmSettings::AlgorithmFreeSizeMode", "Best"),
                                                         "sizeConstraints": enum("AlgorithmSettings::SizeConstraints",
                                                                                 "AnySize"),
                                                         "forceSquared": False,
                                                         "maxRects":
                                                             {"AlgorithmMaxRectsSettings":
                                                                 {"heuristic": enum(
                                                                     "AlgorithmMaxRectsSettings::Heuristic",
                                                                     "AreaFit")}}},
                                   "basic":
                                       {"AlgorithmBasicSettings":
                                            {"sortBy": enum("AlgorithmBasicSettings::SortBy", "Best"),
                                             "order": enum("AlgorithmBasicSettings::Order", "Ascending")}},
                                   "polygon": {
                                       "AlgorithmPolygonSettings": {
                                           "alignToGrid": np.uint(1)
                                       }
                                   }}  # Struct

        self.data_file_names = map("GFileNameMap", [["sc_atlas_data"]], [{"DataFile": {"name": filename()}}])  # Map

        self.multipack = True

        self.output_format = enum("SettingsBase::OutputFormat", "RGBA8888")  # Enum

        self.alpha_handling = enum("SettingsBase::AlphaHandling", "ClearTransparentPixels")  # Enum

        self.sprite_settings = {"SpriteSettings": {"scale": 1.0,
                                                   "scaleMode": enum("ScaleMode", "Smooth"),
                                                   "extrude": np.uint(2),
                                                   "trimThreshold": np.uint(1),
                                                   "trimMargin": np.uint(1),
                                                   "trimMode": enum("SpriteSettings::TrimMode", "Polygon"),
                                                   "tracerTolerance": 300,
                                                   "heuristicMask": False,
                                                   "defaultPivotPoint": point_f(0.5, 0.5),
                                                   "writePivotPoints": False}}  # Struct

        self.file_list = []  # Array
        self.individual_sprite_settings = map("IndividualSpriteSettingsMap")

    def read(self, filepath):
        def parse_variable(var):
            if var.tag == "int":
                return np.int(int(var.text))

            if var.tag == "uint":
                return np.uint(int(var.text))

            if var.tag == "double":
                return float(var.text)

            if var.tag == "string":
                if var.text is None:
                    return None
                return var.text

            if var.tag == "filename":
                var_res = filename()
                if var.text is not None:
                    var_res.filepath = var.text
                return var_res

            if var.tag == "true":
                return True

            if var.tag == "false":
                return False

            if var.tag == "enum":
                var_res = enum()
                var_res.key = var.attrib['type']
                var_res.value = var.text
                return var_res

            if var.tag == "QSize":
                width = 0
                height = 0
                for i, key in enumerate(var):
                    if key.tag == "key":
                        if key.text == "width":
                            width = parse_variable(var[i + 1])
                        if key.text == "height":
                            height = parse_variable(var[i + 1])
                return [width, height]

            if var.tag == "struct":
                return {
                    var.attrib["type"]: {struct_var.text: parse_variable(var[i + 1]) for i, struct_var in enumerate(var)
                                         if struct_var.tag == "key"}}

            if var.tag == "map":
                map_keys = []
                map_values = []

                active_key_index = 0
                active_key = False
                for i, map_key in enumerate(var):
                    if map_key.tag == "key":
                        if active_key:
                            map_keys[active_key_index].append(map_key.text)
                        else:
                            active_key = True
                            map_keys.append([map_key.text])
                            active_key_index = map_keys.index([map_key.text])
                    else:
                        active_key = False
                        map_values.append(parse_variable(map_key))

                return map(var.attrib['type'], map_keys, map_values)

            if var.tag == "point_f":
                points = [float(num) for num in var.text.split(",")]
                var_points = point_f()
                var_points.x = points[0]
                var_points.y = points[0]
                return var_points

            if var.tag == "rect":
                rect_points = [int(num) for num in var.text.split(",")]
                var_rect = rect()
                var_rect.left = rect_points[0]
                var_rect.right = rect_points[1]
                var_rect.top = rect_points[2]
                var_rect.bottom = rect_points[3]
                return var_rect

            if var.tag == "array":
                return [parse_variable(array) for array in var]

        parsed = parse(filepath)
        xml = parsed.getroot()

        for settings in xml:
            if settings.attrib['type'] == "Settings":
                for i, key in enumerate(settings):
                    if key.tag == "key":
                        txt = key.text
                        if txt == "fileFormatVersion":
                            self.file_version = parse_variable(settings[i + 1])
                            if self.file_version != 5:
                                raise Exception()
                        if txt == "texturePackerVersion":
                            self.packer_version == parse_variable(settings[i + 1])
                        if txt == "allowRotation":
                            self.allow_rotation == parse_variable(settings[i + 1])
                        if txt == "shapeDebug":
                            self.shape_debug == parse_variable(settings[i + 1])
                        if txt == "dataFormat":
                            self.data_format == parse_variable(settings[i + 1])
                        if txt == "textureFileName":
                            self.texture_file_name = parse_variable(settings[i + 1])
                        if txt == "shapePadding":
                            self.shape_padding = parse_variable(settings[i + 1])
                        if txt == "pngOptimizationLevel":
                            self.png_optimization = parse_variable(settings[i + 1])
                        if txt == "textureFormat":
                            self.texture_format = parse_variable(settings[i + 1])
                        if txt == "borderPadding":
                            self.border_padding = parse_variable(settings[i + 1])
                        if txt == "maxTextureSize":
                            self.max_texture_size = parse_variable(settings[i + 1])
                        if txt == "fixedTextureSize":
                            self.fixed_texture_size = parse_variable(settings[i + 1])
                        if txt == "algorithmSettings":
                            self.algorithm_settings = parse_variable(settings[i + 1])
                        if txt == "dataFileNames":
                            self.data_file_names = parse_variable(settings[i + 1])
                        if txt == "multiPack":
                            self.multipack = parse_variable(settings[i + 1])
                        if txt == "outputFormat":
                            self.output_format = parse_variable(settings[i + 1])
                        if txt == "alphaHandling":
                            self.alpha_handling = parse_variable(settings[i + 1])
                        if txt == "globalSpriteSettings":
                            self.sprite_settings = parse_variable(settings[i + 1])
                        if txt == "individualSpriteSettings":
                            self.individual_sprite_settings = parse_variable(settings[i + 1])
                        if txt == "fileList":
                            self.file_list = parse_variable(settings[i + 1])

    def save(self, filepath):
        def write_variable(xml, key, value):
            if key is not None:
                var = Element("key")
                var.text = key
                xml.append(var)

            if isinstance(value, bool):
                value_res = Element(str(value).lower())

            elif isinstance(value, int):
                value_res = Element('int')
                value_res.text = str(value)

            elif isinstance(value, np.uint):
                value_res = Element('uint')
                value_res.text = str(value)

            elif isinstance(value, str):
                value_res = Element('string')
                value_res.text = str(value)

            elif isinstance(value, float):
                value_res = Element("double")
                value_res.text = str(value)

            elif type(value) in [filename, rect, point_f, enum]:
                value_res = value.save()

            elif isinstance(value, list) and len(value) == 2:
                value_res = Element("QSize")

                write_variable(value_res, "width", value[0])
                write_variable(value_res, "height", value[1])

            elif isinstance(value, list):
                value_res = Element("array")
                for value_array in value:
                    write_variable(value_res, None, value_array)

            elif isinstance(value, dict):
                root_key = list(value)[0]
                value_res = Element("struct", {'type': root_key})
                var_struct = value[root_key]
                for struct_key in var_struct:
                    write_variable(value_res, struct_key, var_struct[struct_key])

            elif isinstance(value, map):
                value_res = Element("map", {'type': value.type})

                for i, key_list in enumerate(value.keys):
                    for key in key_list:
                        map_key = Element("key")
                        map_key.text = key
                        value_res.append(map_key)
                    write_variable(value_res, None, value.values[i])

            xml.append(value_res)

        xml = Element("data", {"version": "1.0"})

        settings = Element("struct", {"type": "Settings"})
        xml.append(settings)

        write_variable(settings, "fileFormatVersion", self.file_version)
        write_variable(settings, "texturePackerVersion", self.packer_version)
        write_variable(settings, "allowRotation", self.allow_rotation)
        write_variable(settings, "shapeDebug", self.shape_debug)
        write_variable(settings, "dataFormat", self.data_format)
        write_variable(settings, "textureFileName", self.texture_file_name)
        write_variable(settings, "shapePadding", self.shape_padding)
        write_variable(settings, "pngOptimizationLevel", self.png_optimization)
        write_variable(settings, "textureFormat", self.texture_format)
        write_variable(settings, "maxTextureSize", self.max_texture_size)
        write_variable(settings, "fixedTextureSize", self.fixed_texture_size)
        write_variable(settings, "algorithmSettings", self.algorithm_settings)
        write_variable(settings, "dataFileNames", self.data_file_names)
        write_variable(settings, "multiPack", self.multipack)
        write_variable(settings, "outputFormat", self.output_format)
        write_variable(settings, "alphaHandling", self.alpha_handling)
        write_variable(settings, "globalSpriteSettings", self.sprite_settings)
        write_variable(settings, "individualSpriteSettings", self.individual_sprite_settings)
        write_variable(settings, "fileList", self.file_list)

        with open(filepath, "wb") as f:
            f.write(b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
            f.write(tostring(xml))
