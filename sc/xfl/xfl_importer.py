import os

import cv2
import numpy as np

from math import radians, sin, cos, ceil

from xml.etree.ElementTree import *

from sc.utils import AffineTransform
from sc.swf.shape import  get_center, calculate_rotation2, calculate_scale

from sc.xfl.xfl import XFL
from sc.xfl.bitmap import Bitmap


# for use
KEY_MODE_NORMAL = 9728
KEY_MODE_CLASSIC_TWEEN = 22017
KEY_MODE_SHAPE_TWEEN = 17922
KEY_MODE_MOTION_TWEEN = 8195
KEY_MODE_SHAPE_LAYERS = 8192

text_field_alignment = ["left", "right", "center", "justify"] # for future

text_field_actions = {}
movieclip_ids = []
modifers_ids = []
shape_ids = []


# collect all text fields to one dictionary
def convert_text_fields(swf):
    for text_field in swf.text_fields:
        text_field_actions[text_field.id] = text_field


# proceed movies
def convert_movieclips(swf, xfl):
    for modifer in swf.movieclip_modifiers:
        modifers_ids.append(modifer.id)

    for movieclip in swf.movieclips:
        movieclip_ids.append(movieclip.id)

        movie_name = f"{movieclip.id}"
        if movieclip.id in swf.exports:
            movie_name = swf.exports[movieclip.id]

        symbol = Element("DOMSymbolItem")
        symbol.attrib = {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns": "http://ns.adobe.com/xfl/2008/",
            "name": movie_name
        }

        timeline = SubElement(SubElement(symbol, "timeline"), "DOMTimeline", name=movie_name)
        layers = SubElement(timeline, "layers")

        mask = False #Boolean for modifers(masks)
        mask_child = False

        layer_idx = 0
        layers_list = [] # for layers reversing
        for bind in movieclip.binds:
            layer_name = f"Layer_{layer_idx}"
            if bind["name"]:
                layer_name = bind["name"]

            layer = Element("DOMLayer")
            if bind['id'] in modifers_ids:
                modifer = swf.movieclip_modifiers[modifers_ids.index(bind['id'])].stencil
                if modifer == 2:
                    mask = True
                elif modifer == 3:
                    mask_child = True
                elif modifer == 4:
                    mask_child == False

            else:
                layer_attribs = {"name": layer_name, "autoNamed": "false", "color": "#000000"}
                if mask:
                    layer_attribs["layerType"] = "mask"
                    mask = False
                elif mask_child:
                    layer_attribs["parentLayerIndex"] = str(len(movieclip.binds) - layer_idx - 1) #bind count - layer index - modifer bind

                layer.attrib = layer_attribs
                layer_frames = SubElement(layer, "frames")

                for frame in movieclip.frames:
                    layer_frame = SubElement(layer_frames, "DOMFrame", index=str(movieclip.frames.index(frame)),
                                             keyMode=str(KEY_MODE_NORMAL))

                    if frame.name:
                        layer_frame.attrib["labelType"] = "name"
                        layer_frame.attrib["name"] = frame.name

                    if bind["blend"]:
                        layer_frame.attrib["blendMode"] = bind["blend"]

                    frame_elements = SubElement(layer_frame, "elements")
                    for element in frame.elements:
                        if element["bind"] != layer_idx:
                            continue

                        # adding shape or another movie instance as frame element from main scene
                        if bind["id"] in shape_ids or bind["id"] in movieclip_ids:
                            frame_element_name = f"Shapes/{bind['id']}" if bind["id"] in shape_ids else str(bind["id"])
                            frame_element = SubElement(frame_elements, "DOMSymbolInstance",
                                                       libraryItemName=frame_element_name, loop="loop")

                        # adding text field from dictionary as frame element
                        elif bind["id"] in text_field_actions:
                            text_field = text_field_actions[bind["id"]]

                            # must be Dynamic, but I think SupercellSWF also contains Static and Input (just find correct tag)
                            frame_element = SubElement(frame_elements, "DOMDynamicText", fontRenderingMode="standard")

                            frame_element.attrib["width"] = str(text_field.right_corner - text_field.left_corner)
                            frame_element.attrib["height"] = str(text_field.bottom_corner - text_field.top_corner)

                            if text_field.multiline:
                                frame_element.attrib["lineType"] = "multiline"

                            text_run = SubElement(SubElement(frame_element, "textRuns"), "DOMTextRun")

                            text_attrs = SubElement(SubElement(text_run, "textAttrs"), "DOMTextAttrs")
                            text_attrs.attrib = {
                                "face": text_field.font_name,
                                "size": str(text_field.font_size),
                                "bitmapSize": str(text_field.font_size),
                                "leftMargin": str(text_field.left_corner),
                                "rightMargin": str(text_field.right_corner),
                                # "alignment": text_field_alignment[text_field.font_align], # it is not alignment... (maybe margin)
                                "fillColor": "#" + hex(text_field.font_color & 0x00FFFFFF)[2:],
                                "alpha": str(((text_field.font_color & 0xFF000000) >> 24) / 255)
                            }

                            if text_field.text:
                                SubElement(text_run, "characters").text = text_field.text

                        else:
                            continue

                        # adding matrix to frame element from matrix bank
                        if element["matrix"] != 0xFFFF:
                            matrix_holder = SubElement(SubElement(frame_element, "matrix"), "Matrix")

                            matrix = swf.matrix_banks[movieclip.matrix_bank].matrices[element["matrix"]]

                            matrix_holder.attrib = {
                                "a": str(matrix[0]),
                                "b": str(matrix[1]),
                                "c": str(matrix[2]),
                                "d": str(matrix[3]),
                                "tx": str(matrix[4]),
                                "ty": str(matrix[5])
                            }

                        # adding color transformation to frame element from matrix bank
                        if element["color"] != 0xFFFF:
                            color_holder = SubElement(SubElement(frame_element, "color"), "Color")

                            color = swf.matrix_banks[movieclip.matrix_bank].color_transforms[element["color"]]

                            color_holder.attrib = {
                                "redOffset": str(color[0]),
                                "greenOffset": str(color[1]),
                                "blueOffset": str(color[2]),
                                "alphaOffset": str(color[3]),
                                "redMultiplier": str(color[4]),
                                "greenMultiplier": str(color[5]),
                                "blueMultiplier": str(color[6]),
                                "alphaMultiplier": str(color[7]),
                            }

                layers_list.append(layer)

            layer_idx += 1


        # reversing layers (because Adobe Animate says YES.) #TODO
        for layer in layers_list[::-1]:
            layers.append(layer)
        
        # adding nine slice scaling grid
        if movieclip.nine_slice:
            x, y, width, height = movieclip.nine_slice

            symbol.attrib["scaleGridLeft"] = str(x)
            symbol.attrib["scaleGridTop"] = str(y)
            symbol.attrib["scaleGridRight"] = str(width + x)
            symbol.attrib["scaleGridBottom"] = str(height + y)

        # saving symbol to .xml file
        with open(f"{xfl.library_dir}{movieclip.id}.xml", 'wb') as file:
            file.write(tostring(symbol))

        # including it to the main scene
        SubElement(xfl.symbols, "Include", loadImmediate="true", href=f"{movieclip.id}.xml")


# creating graphics
def convert_shapes(swf, xfl):
    # we must do some FUCKING MAGIC to convert SupercellSWF's shapes to Adobe Animate graphic symbols :)
    # preparing our shapes (graphic symbols that contains bitmap instances)
    prepared_shapes = []
    for shape in swf.shapes:
        shape_ids.append(shape.id)

        prepared_shape = {
            "id": shape.id,
            "bitmaps": [], # bitmap instances
            "colorFills": [], # "color fill commands"
            "matrices": []
        }

        for bitmap in shape.bitmaps:
            # X and Y uv coords for calculating "color fill"
            uv_x = [coord[0] for coord in bitmap.uv_coords]
            uv_y = [coord[1] for coord in bitmap.xy_coords]

            prepared_bitmap = {
                "texture": bitmap.texture_index,
                "uvCoords": bitmap.uv_coords,
                "simX": uv_x.count(uv_x[0]) == len(uv_x),
                # finding similiar X coordinates for calculating "color fill"
                "simY": uv_y.count(uv_y[0]) == len(uv_y)  # and also Y coordinates for it
            }

            # checking for dublicate (instancing)
            if prepared_bitmap not in prepared_shape["bitmaps"]:
                prepared_shape["bitmaps"].append(prepared_bitmap)
            else:
                prepared_shape["bitmaps"].append(prepared_shape["bitmaps"].index(prepared_bitmap))


        prepared_shapes.append(prepared_shape)
    
    # saving prepared bitmaps to Adobe Animate image binary format
    for shape_index in range(len(prepared_shapes)):
        shape = prepared_shapes[shape_index]

        instanced = False
        for bitmap_index in range(len(shape["bitmaps"])):
            bitmap = shape["bitmaps"][bitmap_index]

            # creating main affine matrix
            at = AffineTransform()

            # at this point little message for Adobe Animate...
            # WHY DO AFFINE TRANSFORMATION MATRICES WORK DIFFERENTLY IN BITMAP INSTANCES AND OTHER INSTANCES?
            # WHY NORMAL 90 DEGREES ROTATED MATRIX AND 90 DEGREES ROTATED MATRIX IN ADOBE IS DIFFERENT MF????
            # HOT TO F CREATE MATRIX LIKE IN ADOBE ANIMATE???
            # HELP. ~ from 31 and SV

            uv_coords = swf.shapes[shape_index].bitmaps[bitmap_index].uv_coords
            xy_coords = swf.shapes[shape_index].bitmaps[bitmap_index].xy_coords

            # building sprite bounding box
            image_box = cv2.boundingRect(np.array(uv_coords))
            a, b, c, d = image_box

            # checking for "color fill"
            is_color_fill = c + d < 3
            shape["colorFills"].append(is_color_fill)

            if not is_color_fill:
                if not isinstance(bitmap, int):
                    if c - 1 > 1 and not prepared_bitmap['simX']:
                        c -= 1
                    if d - 1 > 1 and not prepared_bitmap['simY']:
                        d -= 1

                    # ------------------------------------Bitmap matrix-------------------------------------------------#
                    # getting rotation angle (in degrees) of bitmap vertices (xy_coords) and mirror option
                    rotation, mirroring = calculate_rotation2(uv_coords, xy_coords)
                    rad_rot = radians(-rotation)

                    sx, sy, w, h = calculate_scale(
                        [[round(x * cos(rad_rot) + -y * sin(rad_rot)),
                          round(x * sin(rad_rot) + y * cos(rad_rot))]
                         for x, y in uv_coords], xy_coords)

                    left = min(coord[0] for coord in xy_coords)
                    top = min(coord[1] for coord in xy_coords)
                    at.translate(top, left)
                    at.scale(sx, sy)  # apply scale
                    # -----------------------------------------Bitmap image----------------------------------------------#
                    texture = swf.textures[bitmap["texture"]].image

                    points = np.array(uv_coords, dtype=np.int32)
                    mask = np.zeros(texture.shape[:2], dtype=np.uint8)
                    cv2.drawContours(mask, [points], -1, (255, 255, 255), -1, cv2.LINE_AA)
                    res = cv2.bitwise_and(texture, texture, mask=mask)
                    cropped = res[b: b + d, a: a + c]

                    if cropped.shape[0] < 1 or cropped.shape[1] < 1:
                        cropped = res[b - 1: b + d, a - 1: a + c]

                    if rotation:
                        uv_h, uv_w = cropped.shape[:2]
                        uv_center = (uv_w / 2, uv_h / 2)
                        rot = cv2.getRotationMatrix2D(uv_center, -rotation, 1)

                        s = sin(rad_rot)
                        c = cos(rad_rot)
                        b_w = int((uv_h * abs(s)) + (uv_w * abs(c)))
                        b_h = int((uv_h * abs(c)) + (uv_w * abs(s)))

                        rot[0, 2] += ((b_w / 2) - uv_center[0])
                        rot[1, 2] += ((b_h / 2) - uv_center[1])
                        cropped = cv2.warpAffine(cropped, rot, (b_w, b_h))
                    if mirroring:
                        cropped = cv2.flip(cropped, 1)

                    binary_name = f"M {shape['id']} {shape['bitmaps'].index(bitmap)}.dat"
                    png_name = f"{shape['id']} {shape['bitmaps'].index(bitmap)}.png"

                    cv2.imwrite(f"{xfl.resources_dir}{png_name}", cropped)
                    binary = Bitmap()
                    with open(f"{xfl.binary_dir}{binary_name}", 'wb') as file:
                        file.write(binary.save(cropped))

                    # including this media file to main scene library
                    SubElement(xfl.media, "DOMBitmapItem",
                               name=f"Resources/{shape['id']} {shape['bitmaps'].index(bitmap)}",
                               allowSmoothing="true", compressionType="lossless", useImportedJPEGData="false",
                               quality="100", sourceExternalFilepath=f"./LIBRARY/Resources/{png_name}",
                               bitmapDataHRef=binary_name)
                else:
                    pivot_coords = swf.shapes[shape_index].bitmaps[bitmap].xy_coords

                    shape["colorFills"].append(shape["colorFills"][bitmap])

                    #Calculate rotation for bitmap image
                    rotation, mirroring = calculate_rotation2(pivot_coords, xy_coords)
                    rad_rot = radians(-rotation)

                    #Calculate rotation for uv
                    uv_rotation, uv_mirroring = calculate_rotation2(uv_coords, xy_coords)
                    uv_rad_rot = radians(uv_rotation)

                    sx, sy, w, h = calculate_scale(
                        [[ceil(x * cos(uv_rad_rot) + y * sin(uv_rad_rot)),
                          ceil(x * sin(uv_rad_rot) + y * cos(uv_rad_rot))]
                         for x, y in uv_coords], xy_coords)

                    at.rotate(rad_rot)  # apply rotation
                    sprite_box = [[0, 0], [w, 0], [w, h], [0, h]]  # building sprite bounding box

                    # mirroring bounding box
                    if mirroring:
                        at.scale(-1, 1)
                        sprite_box = [[-x, y]
                                      for x, y in sprite_box]

                    # rotating bounding box
                    sprite_box = [[ceil(x * cos(rad_rot) + y * sin(rad_rot)),
                                   ceil(x * sin(rad_rot) + y * cos(rad_rot))]
                                  for x, y in sprite_box]

                    for point_index in range(4):
                        x, y = sprite_box[point_index]

                        if x < 0:
                            sprite_box = [[x_b - x, y_b] for x_b, y_b in sprite_box]
                            at.ty -= x
                        if y < 0:
                            sprite_box = [[x_b, y_b - y] for x_b, y_b in sprite_box]
                            at.tx -= y

                    left = min(coord[0] for coord in xy_coords)
                    top = min(coord[1] for coord in xy_coords)

                    at.tx = top + sprite_box[0][1]
                    at.ty = left + sprite_box[0][0]

                    at.scale(sx, sy)  # apply scale
                    #print(f"Bitmap index: {bitmap_index}, Rotation: {rotation}, Translate: {left, top}, Mirror: {mirroring}, Box: {sprite_box}")

            # adding matrix
            prepared_shapes[shape_index]["matrices"].append(at.get_matrix())

        # creating graphic symbol
        symbol = Element("DOMSymbolItem")
        symbol.attrib = {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns": "http://ns.adobe.com/xfl/2008/",
            "symbolType": "graphic",
            "name": f"Shapes/{shape['id']}"
        }

        timeline = SubElement(SubElement(symbol, "timeline"), "DOMTimeline", name=str(shape["id"]))
        layer = SubElement(SubElement(timeline, "layers"), "DOMLayer", name=str(shape["id"]), backgroundColor="#000000", current="true", isSelected="true")
        frame = SubElement(SubElement(layer, "frames"), "DOMFrame", index="0", keyMode=str(KEY_MODE_NORMAL))
        frame_elements = SubElement(frame, "elements")

        for bitmap_index in range(len(shape["bitmaps"])):
            bitmap = shape["bitmaps"][bitmap_index]

            if isinstance(bitmap, int):
                index = bitmap
            else:
                index = shape["bitmaps"].index(bitmap)
            
            # creating bitmap instance
            if not shape["colorFills"][bitmap_index]:
                item_name = f"Resources/{shape['id']} {index}"
                instance = SubElement(frame_elements, "DOMBitmapInstance", libraryItemName=item_name)

                matrix_holder = SubElement(SubElement(instance, "matrix"), "Matrix")

                matrix = shape["matrices"][bitmap_index]
                
                if matrix[0] != 1.0:
                    matrix_holder.attrib["a"] = str(matrix[0])
                
                if matrix[1]:
                    matrix_holder.attrib["b"] = str(matrix[1])
                
                if matrix[2]:
                    matrix_holder.attrib["c"] = str(matrix[2])
                
                if matrix[3] != 1.0:
                    matrix_holder.attrib["d"] = str(matrix[3])

                if matrix[5]:
                    matrix_holder.attrib["tx"] = str(matrix[5])

                if matrix[4]:
                    matrix_holder.attrib["ty"] = str(matrix[4])

            # creating "color fill"
            else:
                if isinstance(bitmap, int):
                    texture = swf.textures[shape["bitmaps"][bitmap]["texture"]]
                    color_coords = shape["bitmaps"][bitmap]["uvCoords"][0]
                else:
                    texture = swf.textures[bitmap["texture"]]
                    color_coords = bitmap["uvCoords"][0]

                fill_item = SubElement(frame_elements, "DOMShape")

                fill = SubElement(SubElement(fill_item, "fills"), "FillStyle", index="1")

                # fill color
                x, y = color_coords
                color = texture.image[round(y), round(x)]
                
                final_color = hex(color[2])[2:] + hex(color[1])[2:] + hex(color[0])[2:]
                SubElement(fill, "SolidColor", color="#" + final_color, alpha=str(color[3] / 255))

                edges = SubElement(SubElement(fill_item, "edges"), "Edge", fillStyle1="1")
                xy_coords = swf.shapes[shape_index].bitmaps[bitmap_index].xy_coords
                # filling polygon coordinates
                final_edges = ""
                for x in range(len(xy_coords)):
                    curr = xy_coords[x]
                    nxt = xy_coords[(x + 1) % len(xy_coords)]

                    final_edges += f"!{curr[0] * 20} {curr[1] * 20}|{nxt[0] * 20} {nxt[1] * 20}" # converting pixels to twips (again.) (1 twip = 1/20 pixel)
                
                edges.attrib["edges"] = final_edges

        
        with open(f"{xfl.shapes_dir}{shape['id']}.xml", 'wb') as file:
            file.write(tostring(symbol))
        
        SubElement(xfl.symbols, "Include", loadImmediate="true", itemIcon="1", href=f"Shapes/{shape['id']}.xml")


def init_dom(xfl):
    xfl.folders = SubElement(xfl.dom, "folders") # folders in scene library
    xfl.media = SubElement(xfl.dom, "media") # all scene media (bitmaps in our case)
    xfl.symbols = SubElement(xfl.dom, "symbols") # all included symbols in scene
    xfl.timelines = SubElement(xfl.dom, "timelines") # and timelines (also unused by default)

    SubElement(xfl.folders, "DOMFolderItem", name="Resources", isExpanded="ture") # unused (for sprites debug)
    SubElement(xfl.folders, "DOMFolderItem", name="Shapes", isExpanded="ture") # folder for our graphic symbols

    os.mkdir(xfl.project_dir)
    os.mkdir(xfl.library_dir)
    os.mkdir(xfl.resources_dir)
    os.mkdir(xfl.shapes_dir)
    os.mkdir(xfl.binary_dir)


def generate_texturepacker_project(swf):
    pass


# main convert function
def convert_sc_to_xfl(swf):
    # creating document instance
    xfl = XFL()

    xfl.dom = Element("DOMDocument")
    xfl.dom.attrib = {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns": "http://ns.adobe.com/xfl/2008/",
        "backgroundColor": "#000000",
        "width": "1280",
        "height": "720",
        "frameRate": "30",
        "currentTimeline": "1",
        "creatorInfo": "SupercellSWF (for Python) by SCW Make",
        "xflVersion": "22.02"
    }

    # project director
    xfl.project_dir = os.path.splitext(swf.filename)[0]

    try:
        from shutil import rmtree
        rmtree(xfl.project_dir)
    except:
        pass

    # initialize basic project things (like folders inside scene library etc.)
    init_dom(xfl)

    # creating things
    convert_text_fields(swf)
    convert_shapes(swf, xfl)
    convert_movieclips(swf, xfl)

    # saving project
    with open(f"{xfl.project_dir}/DOMDocument.xml", 'wb') as dom:
        dom.write(tostring(xfl.dom))
    
    # and this very important thing.
    with open(f"{xfl.project_dir}/{os.path.basename(xfl.project_dir)}.xfl", 'w') as xfl:
        xfl.write("PROXY-CS5")

    # now you need pack all files in project directory to .zip and change extension to .fla
    # done!
