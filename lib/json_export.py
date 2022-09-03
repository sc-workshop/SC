import affine6p
import ujson
from PIL import Image
from tempfile import TemporaryDirectory
from lib.console import Console
import numpy as np
import os
from lib.sc import *
from lib.sc.texture import PACKER_FILTER_TABLE, PACKER_PIXEL_TYPES, MODES_TABLE, PIXEL_TYPES, PIXEL_FORMATS
from lib.tps.texture_packer import TexturePackerProject, Enum

channels_table = {
    1: "L",
    2: "LA",
    3: "RGB",
    4: "RGBA"
}

modifier_table = {
    "Mask": 38,
    "Masked": 39,
    "Unmasked": 40
}

def convert_texture(texture):
    sc_texture = SWFTexture()
    if texture["texture_format"] in ["png", "png8"]:
        sc_texture.width, sc_texture.height = texture["size"]
        sc_texture.mag_filter, sc_texture.min_filter = [PACKER_FILTER_TABLE[filter] for filter in texture["filter"]]
        sc_texture.pixel_type = PIXEL_TYPES[PACKER_PIXEL_TYPES.index(texture["pixel_type"])]
        texture_mode = MODES_TABLE[PIXEL_FORMATS[PACKER_PIXEL_TYPES.index(texture["pixel_type"])]]
        sc_texture.pixel_format = texture_mode
        sc_texture.image = Image.open(texture["uri"]).convert(texture_mode)
        return sc_texture

    else:
        print(f"Wrong spritesheet format! Has {texture['texture_format']} but should be png or png8")
        raise TypeError()

def convert_shape(atlas, shape, temp_path):
    sc_shape = Shape()
    for i, bitmap in enumerate(shape['Bitmaps']):
        sc_bitmap = ShapeDrawBitmapCommand()
        if "Uri" in bitmap:
            atlas_sprite = atlas[bitmap["Uri"].replace("\\", "/")]
            sc_bitmap.uv_coords = atlas_sprite['vertices_uv']

            matrix = affine6p.Transform(bitmap["Matrix"])

            sc_bitmap.xy_coords = matrix.transform(atlas_sprite["vertices"])

        elif "Color" in bitmap:
            atlas_sprite = atlas[f"{temp_path}/{shape['Name']}_{i}.png"]
            sc_bitmap.uv_coords = atlas_sprite['vertices_uv']
            sc_bitmap.xy_coords = bitmap["Shape"]

        sc_bitmap.max_rects = atlas_sprite["maxRects"]
        sc_bitmap.texture_index = atlas_sprite["texture"]

        sc_shape.bitmaps.append(sc_bitmap)

    return sc_shape

def convert_field(field):
    sc_field = TextField()

    sc_field.font_name = field["Font name"]
    sc_field.font_color = field["Font color"]
    sc_field.outline_color = field["Outline color"]
    sc_field.font_size = field["Font size"]
    sc_field.font_align = field["Font align"]

    sc_field.bold = field["Bold"]
    sc_field.italic = field["Italic"]
    sc_field.multiline = field["Multiline"]
    sc_field.outline = field["Outline"]

    sc_field.left_corner = field["Left corner"]
    sc_field.top_corner = field["Top corner"]
    sc_field.right_corner = field["Right corner"]
    sc_field.bottom_corner = field["Bottom corner"]

    sc_field.text = field["Text"]

    sc_field.flag1 = field["Flag1"]
    sc_field.flag2 = field["Flag2"]
    sc_field.flag3 = field["Flag3"]

    sc_field.c1 = field["C1"]
    sc_field.c2 = field["C2"]

    return sc_field

def convert_movieclip(swf, movieclip):
    sc_movieclip = MovieClip()

    if "Framerate" in movieclip:
        sc_movieclip.frame_rate = movieclip["Framerate"]

    if "Exports" in movieclip:
        if movieclip["Name"] not in swf.exports:
            swf.exports[movieclip["Name"]] = []

        for export in movieclip["Exports"]:
            swf.exports[movieclip["Name"]].append(export)

    if "9slice" in movieclip:
        sc_movieclip.nine_slice = movieclip["9slice"]

    sc_movieclip.binds = movieclip["Binds"]

    movieclip_matrix_count = 0
    movieclip_colors_count = 0
    temp_matrix_storage = []
    temp_color_storage = []
    for frame in movieclip["Frames"]:
        for element in frame["Elements"]:
            if "Matrix" in element:
                if element["Matrix"] not in temp_matrix_storage:
                    temp_matrix_storage.append(element["Matrix"])
                    movieclip_matrix_count += 1

            if "Color" in element:
                if element["Color"] not in temp_color_storage:
                    temp_color_storage.append(element["Color"])
                    movieclip_colors_count += 1

    available_banks = [bank.available_for_matrix(movieclip_matrix_count)
                       and bank.available_for_colors(movieclip_colors_count)
                       for bank in swf.matrix_banks]
    if True not in available_banks:
        new_bank = MatrixBank()
        swf.matrix_banks.append(new_bank)
        sc_movieclip.matrix_bank = swf.matrix_banks.index(new_bank)
    else:
        sc_movieclip.matrix_bank = available_banks.index(True)

    del temp_color_storage
    del temp_matrix_storage

    for frame in movieclip["Frames"]:
        sc_frame = MovieClipFrame()
        sc_frame.name = frame["Name"]

        for element in frame["Elements"]:
            sc_frame.elements.append({"bind": element["BindIndex"],
                                      "matrix": 0xFFFF if "Matrix" not in element
                                      else swf.matrix_banks[sc_movieclip.matrix_bank].get_matrix(element["Matrix"]),
                                      "color": 0xFFFF if "Color" not in element
                                      else swf.matrix_banks[sc_movieclip.matrix_bank].get_color_transform(element["Color"])})
        sc_movieclip.frames.append(sc_frame)

    return sc_movieclip


def json_to_sc(filepath):
    json = ujson.load(open(filepath, "r"))
    swf = SupercellSWF()
    swf.has_external_texture = json["Has external texture"]
    swf.use_lowres_texture = json["Has lowres texture"]
    swf.use_uncommon_texture = json["Uses uncommon texture"]
    swf.matrix_banks.append(MatrixBank())

    temp_dirr = TemporaryDirectory()
    temp_path = temp_dirr.name.replace('\\', '/')
    prepared_sprites = {"RGBA8888": [], "ALPHA": [], "ALPHA_INTENSITY": []}

    for shape in json['Shapes']:
        for i, bitmap in enumerate(shape["Bitmaps"]):
            sprite_type = "RGBA8888"
            if "Pixel type" in bitmap:
                if bitmap["Pixel type"] == "GL_LUMINANCE_ALPHA":
                    sprite_type = "ALPHA_INTENSITY"
                elif bitmap["Pixel type"] == "GL_LUMINANCE":
                    sprite_type = "ALPHA"

            if "Uri" in bitmap:
                if bitmap["Uri"] not in prepared_sprites[sprite_type]:
                    prepared_sprites[sprite_type].append(bitmap["Uri"])
            elif "Color" in bitmap:
                fill_path = f"{temp_path}/{shape['Name']}_{i}.png"
                fill = Image.new(channels_table[len(bitmap["Color"])], (1, 1), tuple(bitmap["Color"]))
                fill.save(fill_path)
                prepared_sprites[sprite_type].append(fill_path)

    atlas = {"textures": [],
             "shapes": {}}

    project_dir = os.path.dirname(os.path.abspath(filepath))
    for pixel_format, filelist in prepared_sprites.items():
        if filelist:
            atlas_project = TexturePackerProject()
            atlas_project.init()
            atlas_project.data["Settings"]["outputFormat"] = Enum("SettingsBase::OutputFormat", pixel_format)
            temp_atlas = atlas_project.create_atlas(filelist, project_dir, os.path.basename(os.path.splitext(filepath)[0]))
            for shape_key in temp_atlas['shapes']:
                shape = temp_atlas['shapes'][shape_key]
                shape['texture'] += len(atlas['textures'])
                atlas['shapes'][shape_key] = temp_atlas['shapes'][shape_key]

            atlas["textures"] += temp_atlas["textures"]

    for texture in atlas["textures"]:
        swf.textures.append(convert_texture(texture))

    for shape in json['Shapes']:
        swf.resources[shape["Name"]] = convert_shape(atlas["shapes"], shape, temp_path)

    for modifier in json["Modifiers"]:
        sc_modifier = MovieClipModifier()
        sc_modifier.modifier = Modifier(modifier_table[modifier["Modifier"]])
        swf.resources[modifier["Id"]] = sc_modifier


    for field in json["Textfields"]:
        swf.resources[field["Name"]] = convert_field(field)

    for movieclip in json["Movieclips"]:
        swf.resources[movieclip["Name"]] = convert_movieclip(swf, movieclip)

    save_path = os.path.splitext(os.path.basename(filepath))[0] + ".sc"
    swf.save(save_path)
