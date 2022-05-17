import os

import json

import cv2

from sc.swf.swf import SupercellSWF



def convert_sc_to_json(filepath):
    swf = SupercellSWF()
    has_external_texture, has_highres_texture, has_lowres_texture = swf.load(filepath)

    library = {}

    library["hasExternalTextureFile"] = has_external_texture
    library["hasHighResTexture"] = has_highres_texture
    library["hasLowResTexture"] = has_lowres_texture

    library["highResTextureFilePostfix"] = swf.highres_asset_postfix
    library["lowResTextureFilePostfix"] = swf.lowres_asset_postfix

    library["textures"] = []
    library["movieclipModifiers"] = []
    library["shapes"] = []
    library["textFields"] = []
    library["movieclips"] = []

    for texture in swf.textures:
        inlib = {} # in library texture

        inlib["pixelType"] = texture.pixel_type
        inlib["pixelFormat"] = texture.pixel_format
        inlib["pixelInternalFormat"] = texture.pixel_internal_format

        inlib["magFilter"] = texture.mag_filter
        inlib["minFilter"] = texture.min_filter

        inlib["linear"] = texture.linear
        inlib["downscaling"] = texture.downscaling

        inlib["width"] = texture.width
        inlib["height"] = texture.height

        cv2.imwrite(f"{os.path.splitext(swf.filename)[0]}_{swf.textures.index(texture)}.png", texture.image)
        inlib["uri"] = os.path.splitext(swf.filename)[0] + f"_{swf.textures.index(texture)}.png"

        library["textures"].append(inlib)
    
    for movieclip_modifier in swf.movieclip_modifiers:
        inlib = {} # in library movieclip modifier

        inlib["id"] = movieclip_modifier.id
        inlib["stencil"] = movieclip_modifier.stencil

        library["movieclipModifiers"].append(inlib)
    
    for shape in swf.shapes:
        inlib = {} # in library shape

        inlib["id"] = shape.id
        inlib["bitmaps"] = []

        for bitmap in shape.bitmaps:
            inlib_bitmap = {} # in library shape draw bitmap command

            inlib_bitmap["texture"] = bitmap.texture_index
            inlib_bitmap["vertices"] = [twip for twip in bitmap.xy_coords]
            inlib_bitmap["texcoords"] = [[round(uv[0]), round(uv[1])] for uv in bitmap.uv_coords]

            inlib["bitmaps"].append(inlib_bitmap)
        
        library["shapes"].append(inlib)
    
    font_alignment = ["left", "right", "center", "justify"]
    for text_field in swf.text_fields:
        inlib = {} # in library text field

        inlib["id"] = text_field.id

        inlib["fontName"] = text_field.font_name
        inlib["fontColor"] = hex(text_field.font_color & 0xFFFFFFFF)

        inlib["fontSize"] = text_field.font_size
        inlib["fontAlign"] = font_alignment[text_field.font_align]

        inlib["bounds"] = [
            text_field.left_corner, text_field.top_corner,
            text_field.right_corner, text_field.bottom_corner
        ]

        inlib["bold"] = text_field.bold
        inlib["italic"] = text_field.italic
        inlib["multiline"] = text_field.multiline
        inlib["uppercase"] = text_field.uppercase
        inlib["flag1"] = text_field.flag1
        inlib["flag2"] = text_field.flag2
        inlib["flag3"] = text_field.flag3

        if text_field.text:
            inlib["text"] = text_field.text
        
        inlib["outlineColor"] = hex(text_field.outline_color & 0xFFFFFFFF)
        inlib["c1"] = text_field.c1
        inlib["c2"] = text_field.c2

        library["textFields"].append(inlib)
    
    for movieclip in swf.movieclips:
        inlib = {} # in library movieclip

        if movieclip.id in swf.exports:
            inlib["exportName"] = swf.exports[movieclip.id]

        inlib["id"] = movieclip.id
        inlib["fps"] = movieclip.frame_rate
        inlib["binds"] = []

        for bind in movieclip.binds:
            inlib_bind = {} # in library bind layer

            inlib_bind["id"] = bind["id"]

            inlib_bind["blend"] = bind["blend"]

            if bind["name"]:
                inlib_bind["name"] = bind["name"]
            
            inlib_bind["frames"] = []
            for frame in movieclip.frames:
                inlib_frame = {} # in library movieclip frame

                if frame.name:
                    inlib_frame["name"] = frame.name
                
                for element in frame.elements:
                    if element["bind"] != movieclip.binds.index(bind):
                        continue

                    if element["matrix"] != 0xFFFF:
                        inlib_frame["matrix"] = swf.matrix_banks[movieclip.matrix_bank].matrices[element["matrix"]]

                    if element["color"] != 0xFFFF:
                        inlib_frame["color"] = swf.matrix_banks[movieclip.matrix_bank].color_transforms[element["color"]]
                    
                    inlib_bind["frames"].append(inlib_frame)
            
            inlib["binds"].append(inlib_bind)

        if movieclip.nine_slice:
            inlib["nineSlice"] = movieclip.nine_slice
        
        library["movieclips"].append(inlib)

    json.dump(library, open(os.path.splitext(swf.filename)[0] + ".json", 'w'), indent=2)
