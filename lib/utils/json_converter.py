import os

import json

import cv2

from struct import unpack

from lib.sc.swf import *


def convert_sc_to_json(filepath):
    swf = SupercellSWF()
    swf.load(filepath)

    library = {"hasExternalTextureFile": swf.has_external_texture, "hasHighResTexture": swf.has_highres_texture,
               "hasLowResTexture": swf.has_lowres_texture, "highResTextureFilePostfix": swf.highres_asset_postfix,
               "lowResTextureFilePostfix": swf.lowres_asset_postfix, "compression": swf.compression, "textures": [],
               "movieclipModifiers": [], "shapes": [], "textFields": [], "movieclips": []}

    for texture in swf.textures:
        inlib = {"pixelType": texture.pixel_type, "pixelFormat": texture.pixel_format,
                 "pixelInternalFormat": texture.pixel_internal_format, "magFilter": texture.mag_filter,
                 "minFilter": texture.min_filter, "linear": texture.linear, "downscaling": texture.downscaling,
                 "width": texture.width, "height": texture.height}  # in library texture

        print(texture.image.shape[2])

        cv2.imwrite(f"{os.path.splitext(swf.filename)[0]}_{swf.textures.index(texture)}.png", texture.image)
        inlib["uri"] = os.path.splitext(swf.filename)[0] + f"_{swf.textures.index(texture)}.png"

        library["textures"].append(inlib)

    for movieclip_modifier in swf.movieclip_modifiers:
        inlib = {"id": movieclip_modifier.id, "stencil": movieclip_modifier.type}  # in library movieclip modifier

        library["movieclipModifiers"].append(inlib)

    for shape in swf.shapes:
        inlib = {"id": shape.id, "bitmaps": []}  # in library shape

        for bitmap in shape.bitmaps:
            inlib_bitmap = {"texture": bitmap.texture_index}  # in library shape draw bitmap command

            if bitmap.max_rects:
                inlib_bitmap["rect"] = bitmap.max_rects

            inlib_bitmap["vertices"] = [twip for twip in bitmap.xy_coords]
            inlib_bitmap["texcoords"] = [[round(uv[0]), round(uv[1])] for uv in bitmap.uv_coords]

            inlib["bitmaps"].append(inlib_bitmap)

        library["shapes"].append(inlib)

    # font_alignment = ["left", "right", "center", "justify"]
    for text_field in swf.text_fields:
        inlib = {"id": text_field.id, "fontName": text_field.font_name,
                 "fontColor": hex(text_field.font_color & 0xFFFFFFFF), "fontSize": text_field.font_size,
                 "fontMargin": text_field.font_align,
                 "bounds": [text_field.left_corner, text_field.top_corner,
                            text_field.right_corner, text_field.bottom_corner],
                 "bold": text_field.bold, "italic": text_field.italic,
                 "multiline": text_field.multiline,
                 "uppercase": text_field.uppercase}  # in library text field

        # inlib["fontAlign"] = font_alignment[text_field.font_align]

        if text_field.flag1 is not None:
            inlib["flag1"] = text_field.flag1

        if text_field.flag2 is not None:
            inlib["flag2"] = text_field.flag2

        if text_field.flag3 is not None:
            inlib["flag3"] = text_field.flag3

        if text_field.text:
            inlib["text"] = text_field.text

        if text_field.outline_color is not None:
            inlib["outlineColor"] = hex(text_field.outline_color & 0xFFFFFFFF)

        if text_field.c1 is not None:
            inlib["c1"] = text_field.c1

        if text_field.c2 is not None:
            inlib["c2"] = text_field.c2

        library["textFields"].append(inlib)

    for movieclip in swf.movieclips:
        inlib = {}  # in library movieclip

        if movieclip.id in swf.exports:
            inlib["exportName"] = swf.exports[movieclip.id]

        inlib["id"] = movieclip.id
        inlib["fps"] = movieclip.frame_rate
        inlib["binds"] = []

        for bind in movieclip.binds:
            inlib_bind = {"id": bind["id"]}  # in library bind layer

            if bind["blend"]:
                inlib_bind["blend"] = bind["blend"]

            if bind["name"]:
                inlib_bind["name"] = bind["name"]

            inlib_bind["frames"] = []
            for frame in movieclip.frames:
                inlib_frame = {}  # in library movieclip frame

                inlib_frame["index"] = movieclip.frames.index(frame)

                if frame.name:
                    inlib_frame["name"] = frame.name

                for element in frame.elements:
                    if element["bind"] != movieclip.binds.index(bind):
                        continue

                    if element["matrix"] != 0xFFFF:
                        inlib_frame["matrix"] = swf.matrix_banks[movieclip.matrix_bank].matrices[element["matrix"]]

                    if element["color"] != 0xFFFF:
                        inlib_frame["color"] = swf.matrix_banks[movieclip.matrix_bank].color_transforms[
                            element["color"]]

                    inlib_bind["frames"].append(inlib_frame)

            inlib["binds"].append(inlib_bind)

        if movieclip.nine_slice:
            inlib["nineSlice"] = movieclip.nine_slice

        library["movieclips"].append(inlib)

    json.dump(library, open(os.path.splitext(swf.filename)[0] + ".json", 'w'), indent=2)


def convert_json_to_sc(filepath):
    library = json.load(open(filepath, 'r'))

    swf = SupercellSWF()

    if "hasExternalTextureFile" in library:
        swf.has_external_texture = library["hasExternalTextureFile"]

    if "hasHighResTexture" in library:
        swf.has_highres_texture = library["hasHighResTexture"]

    if "hasLowResTexture" in library:
        swf.has_lowres_texture = library["hasLowResTexture"]

    if "highResTextureFilePostfix" in library:
        swf.highres_asset_postfix = library["highResTextureFilePostfix"]

    if "lowResTextureFilePostfix" in library:
        swf.lowres_asset_postfix = library["lowResTextureFilePostfix"]

    if "compression" in library:
        swf.compression = library["compression"]

    if "textures" in library:
        for texture in library["textures"]:
            tag = SWFTexture()

            if "linear" in texture:
                tag.linear = texture["linear"]

            if "downscaling" in texture:
                tag.downscaling = texture["downscaling"]

            if "magFilter" in texture:
                tag.mag_filter = texture["magFilter"]

            if "minFilter" in texture:
                tag.min_filter = texture["minFilter"]

            if "pixelType" in texture:
                tag.pixel_type = texture["pixelType"]

            if "pixelFormat" in texture:
                tag.pixel_format = texture["pixelFormat"]

            if "pixelInternalFormat" in texture:
                tag.pixel_internal_format = texture["pixelInternalFormat"]

            if "uri" not in texture:
                continue

            tag.image = cv2.imread(texture["uri"], cv2.IMREAD_UNCHANGED)

            swf.textures.append(tag)

        if "shapes" in library:
            for shape in library["shapes"]:
                tag = Shape()

                if "id" not in shape:
                    continue

                if "bitmaps" not in shape:
                    continue

                for bitmap in shape["bitmaps"]:
                    inner_tag = ShapeDrawBitmapCommand()

                    if "texture" not in bitmap:
                        continue

                    if "vertices" not in bitmap:
                        continue

                    if "texcoords" not in bitmap:
                        continue

                    if not bitmap["vertices"]:
                        continue

                    if not bitmap["texcoords"]:
                        continue

                    inner_tag.texture_index = bitmap["texture"] % len(swf.textures)

                    if "rect" in bitmap:
                        inner_tag.max_rects = bitmap["rect"]

                    while len(bitmap["vertices"]) < 4:
                        bitmap["vertices"].append(bitmap["vertices"][-1])

                    while len(bitmap["texcoords"]) < len(bitmap["vertices"]):
                        bitmap["texcoords"].append(bitmap["texcoords"][-1])

                    if len(bitmap["vertices"]) != len(bitmap["texcoords"]):
                        continue

                    inner_tag.xy_coords = bitmap["vertices"]
                    inner_tag.uv_coords = bitmap["texcoords"]

                    tag.bitmaps.append(inner_tag)

                if not tag.bitmaps:
                    continue

                tag.id = shape["id"]
                swf.shapes.append(tag)

    if "movieclipModifiers" in library:
        for modifier in library["movieclipModifiers"]:
            tag = MovieClipModifier()

            if "id" not in modifier:
                continue

            if "stencil" in modifier:
                tag.type = modifier["stencil"]

            tag.id = modifier["id"]
            swf.movieclip_modifiers.append(tag)

    if "textFields" in library:
        for text_field in library["textFields"]:
            tag = TextField()

            if "id" not in text_field:
                continue

            if "fontName" not in text_field:
                continue

            tag.font_name = text_field["fontName"]

            if "fontColor" in text_field:
                tag.font_color = unpack('i', bytes.fromhex(text_field["fontColor"][2:]))[0]

            if "fontSize" in text_field:
                tag.font_size = text_field["fontSize"]

            if "fontMargin" in text_field:
                tag.font_align = text_field["fontMargin"]

            if "bold" in text_field:
                tag.bold = text_field["bold"]

            if "italic" in text_field:
                tag.italic = text_field["italic"]

            if "multiline" in text_field:
                tag.multiline = text_field["multiline"]

            if "uppercase" in text_field:
                tag.uppercase = text_field["uppercase"]

            if "text" in text_field:
                tag.text = text_field["text"]

            if "bounds" in text_field:
                if len(text_field["bounds"]) >= 4:
                    tag.left_corner = text_field["bounds"][0]
                    tag.top_corner = text_field["bounds"][1]
                    tag.right_corner = text_field["bounds"][2]
                    tag.bottom_corner = text_field["bounds"][3]

            if "outlineColor" in text_field:
                tag.outline_color = unpack('i', bytes.fromhex(text_field["outlineColor"][2:]))[0]

            if "flag1" in text_field:
                tag.flag1 = text_field["flag1"]

            if "flag2" in text_field:
                tag.flag2 = text_field["flag2"]

            if "flag3" in text_field:
                tag.flag3 = text_field["flag3"]

            if "c1" in text_field:
                tag.c1 = text_field["c1"]

            if "c2" in text_field:
                tag.c2 = text_field["c2"]

            tag.id = text_field["id"]
            swf.text_fields.append(tag)

    if "movieclips" in library:
        def check_index(index, data):
            return (0 <= index < len(data)) or (-len(data) <= index < 0)

        def check_matrix_bank():
            matrices = 65534 - len(swf.matrix_banks[-1].matrices)
            colors = 65534 - len(swf.matrix_banks[-1].color_transforms)
            return matrices > 0, colors > 0

        swf.matrix_banks.append(MatrixBank())

        for movieclip in library["movieclips"]:
            tag = MovieClip()

            if "id" not in movieclip:
                continue

            if "binds" not in movieclip:
                continue

            if not movieclip["binds"]:
                continue

            if "exportName" in movieclip:
                swf.exports[movieclip["id"]] = movieclip["exportName"]

            if "fps" in movieclip:
                tag.frame_rate = movieclip["fps"]

            bind_index = 0
            for bind in movieclip["binds"]:
                if "id" not in bind:
                    continue

                if "frames" not in bind:
                    continue

                if not bind["frames"]:
                    continue

                tag_bind = {"id": bind["id"], "blend": None, "name": None}

                if "blend" in bind:
                    tag_bind["blend"] = bind["blend"]

                if "name" in bind:
                    tag_bind["name"] = bind["name"]

                for frame in bind["frames"]:
                    if "index" not in frame:
                        continue

                    while True:
                        if not check_index(frame["index"], tag.frames):
                            tag.frames.append(MovieClipFrame())
                        else:
                            break

                    if "name" in frame:
                        tag.frames[frame["index"]].name = frame["name"]

                    element = {"bind": bind_index, "matrix": 0xFFFF, "color": 0xFFFF}

                    matrices, colors = check_matrix_bank()

                    if not matrices or not colors:
                        swf.matrix_banks.append(MatrixBank())

                    if "matrix" in frame:
                        element["matrix"] = swf.matrix_banks[-1].get_matrix(frame["matrix"])

                    if "color" in frame:
                        if frame["color"] not in swf.matrix_banks[-1].color_transforms:
                            swf.matrix_banks[-1].color_transforms.append(frame["color"])

                        element["color"] = swf.matrix_banks[-1].color_transforms.index(frame["color"])

                    tag.frames[frame["index"]].elements.append(element)

                bind_index += 1
                tag.binds.append(tag_bind)

            if not tag.binds:
                continue

            tag.id = movieclip["id"]
            swf.movieclips.append(tag)

    swf.save(os.path.splitext(filepath)[0] + ".sc")
