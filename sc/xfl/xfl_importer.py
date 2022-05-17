import os

import cv2
import numpy as np

from math import radians, degrees

from xml.etree.ElementTree import *

from sc.utils import AffineTransform
from sc.swf.shape import  calculate_translation, calculate_rotation, calculate_rotation2, calculate_scale

from sc.xfl.xfl import XFL
from sc.xfl.bitmap import Bitmap


KEY_MODE_NORMAL = 9728
KEY_MODE_CLASSIC_TWEEN = 22017
KEY_MODE_SHAPE_TWEEN = 17922
KEY_MODE_MOTION_TWEEN = 8195
KEY_MODE_SHAPE_LAYERS = 8192

text_field_alignment = ["left", "right", "center", "justify"]

text_field_actions = {}
movieclip_ids = []
shape_ids = []


def convert_text_fields(swf):
    for text_field in swf.text_fields:
        text_field_actions[text_field.id] = text_field


def convert_movieclips(swf, xfl):
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

        layer_idx = 0
        layers_list = []
        for bind in movieclip.binds:
            layer_name = f"Layer_{layer_idx}"
            if bind["name"]:
                layer_name = bind["name"]
            
            layer = Element("DOMLayer")
            layer.attrib = {"name": layer_name, "autoNamed": "false", "color": "#000000"}
            layer_frames = SubElement(layer, "frames")

            for frame in movieclip.frames:
                layer_frame = SubElement(layer_frames, "DOMFrame", index=str(movieclip.frames.index(frame)), keyMode=str(KEY_MODE_NORMAL))

                if frame.name:
                    layer_frame.attrib["labelType"] = "name"
                    layer_frame.attrib["name"] = frame.name

                frame_elements = SubElement(layer_frame, "elements")
                for element in frame.elements:
                    if element["bind"] != layer_idx:
                        continue

                    if bind["id"] in shape_ids or bind["id"] in movieclip_ids:
                        frame_element_name = f"Shapes/{bind['id']}" if bind["id"] in shape_ids else str(bind["id"])
                        frame_element = SubElement(frame_elements, "DOMSymbolInstance", libraryItemName=frame_element_name, loop="loop")
                    
                    elif bind["id"] in text_field_actions:
                        text_field = text_field_actions[bind["id"]]

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
                            #"alignment": text_field_alignment[text_field.font_align],
                            "fillColor": "#" + hex(text_field.font_color & 0x00FFFFFF)[2:],
                            "alpha": str(((text_field.font_color & 0xFF000000) >> 24) / 255)
                        }

                        if text_field.text:
                            SubElement(text_run, "characters").text = text_field.text
                    
                    else:
                        continue

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
        
            layer_idx += 1
            layers_list.append(layer)
        
        for layer in layers_list[::-1]:
            layers.append(layer)
        
        if movieclip.nine_slice:
            x, y, width, height = movieclip.nine_slice

            symbol.attrib["scaleGridLeft"] = str(x)
            symbol.attrib["scaleGridTop"] = str(y)
            symbol.attrib["scaleGridRight"] = str(width)
            symbol.attrib["scaleGridBottom"] = str(height)

        with open(f"{xfl.library_dir}{movieclip.id}.xml", 'wb') as file:
            file.write(tostring(symbol))

        SubElement(xfl.symbols, "Include", loadImmediate="true", href=f"{movieclip.id}.xml")


def convert_shapes(swf, xfl):
    prepared_shapes = []
    for shape in swf.shapes:
        shape_ids.append(shape.id)

        prepared_shape = {
            "id": shape.id,
            "bitmaps": [],
            "matrices": [],
            "colorFills": []
        }

        for bitmap in shape.bitmaps:
            uv_x = [coord[0] for coord in bitmap.uv_coords]
            uv_y = [coord[1] for coord in bitmap.uv_coords]

            prepared_bitmap = {
                "texture": bitmap.texture_index,
                "uvCoords": bitmap.uv_coords,
                "simX": uv_x.count(uv_x[0]) == len(uv_x),
                "simY": uv_y.count(uv_y[0]) == len(uv_y)
            }

            x, y = calculate_translation(bitmap)
            rotation, mirroring = calculate_rotation2(bitmap)

            rotation_matrix = AffineTransform()
            rotation_matrix.rotate(rotation)
            rotation_matrix = rotation_matrix.get_matrix()

            sx, sy, w, h = calculate_scale([[rotation_matrix[0] * point[0] + -(rotation_matrix[1]) * point[1], -(rotation_matrix[2]) * point[0] + rotation_matrix[3] * point[1]] for point in bitmap.uv_coords], bitmap.xy_coords)

            at = AffineTransform()

            # sx *= -1 if mirroring else 1

            at.scale(sx, sy)
            at.translate(x - (w / 2), y - (h / 2))
            at.rotate(radians(-rotation))

            if mirroring:
                at.scale(-1, 1)
                at.tx *= -1

            prepared_shape["matrices"].append(at.get_matrix())

            is_color_fill = bitmap.uv_coords.count(bitmap.uv_coords[0]) == len(bitmap.uv_coords)
            prepared_shape["colorFills"].append(is_color_fill)

            if is_color_fill:
                prepared_bitmap["twips"] = bitmap.xy_coords

            if prepared_bitmap not in prepared_shape["bitmaps"]:
                prepared_shape["bitmaps"].append(prepared_bitmap)
            else:
                prepared_shape["bitmaps"].append(prepared_shape["bitmaps"].index(prepared_bitmap))
            
        prepared_shapes.append(prepared_shape)
    
    for shape in prepared_shapes:
        for bitmap in shape["bitmaps"]:
            if not isinstance(bitmap, int) and not shape["colorFills"][shape["bitmaps"].index(bitmap)]:
                texture = swf.textures[bitmap["texture"]]
                points = np.array(bitmap["uvCoords"], dtype=np.int32)
                mask = np.zeros(texture.image.shape[:2], dtype=np.uint8)

                cv2.drawContours(mask, [points], -1, (255, 255, 255), -1)
                res = cv2.bitwise_and(texture.image, texture.image, mask=mask)
                rect = cv2.boundingRect(points)

                cropped = res[rect[1]: rect[1] + rect[3], rect[0]: rect[0] + rect[2]]

                binary = Bitmap()
                binary_name = f"M {shape['id']} {shape['bitmaps'].index(bitmap)}.dat"
                with open(f"{xfl.binary_dir}{binary_name}", 'wb') as file:
                    file.write(binary.save(cropped))
                
                SubElement(xfl.media, "DOMBitmapItem", name=f"Resources/{shape['id']} {shape['bitmaps'].index(bitmap)}", allowSmoothing="true", compressionType="lossless", useImportedJPEGData="false", quality="100", bitmapDataHRef=binary_name)

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

        for bitmap in shape["bitmaps"]:
            if isinstance(bitmap, int):
                index = bitmap
            else:
                index = shape["bitmaps"].index(bitmap)
            
            if not shape["colorFills"][shape["bitmaps"].index(bitmap)]:
                item_name = f"Resources/{shape['id']} {index}"
                instance = SubElement(frame_elements, "DOMBitmapInstance", libraryItemName=item_name)

                matrix_holder = SubElement(SubElement(instance, "matrix"), "Matrix")

                matrix = shape["matrices"][shape["bitmaps"].index(bitmap)]

                matrix_holder.attrib = {
                    "a": str(matrix[0]),
                    "b": str(matrix[1]),
                    "c": str(matrix[2]),
                    "d": str(matrix[3]),
                    "tx": str(matrix[4]),
                    "ty": str(matrix[5])
                }
            else:
                texture = swf.textures[bitmap["texture"]]

                fill_item = SubElement(frame_elements, "DOMShape")

                fill = SubElement(SubElement(fill_item, "fills"), "FillStyle", index="1")
                
                color = texture.image[round(bitmap["simX"]), round(bitmap["simY"])]
                final_color = hex(color[0])[2:] + hex(color[1])[2:] + hex(color[2])[2:]
                SubElement(fill, "SolidColor", color="#" + final_color, alpha=str(color[3] / 255))

                edges = SubElement(SubElement(fill_item, "edges"), "Edge", fillStyle1="1")

                final_edges = ""
                for x in range(len(bitmap["twips"])):
                    curr = bitmap["twips"][x]
                    nxt = bitmap["twips"][(x + 1) % len(bitmap["twips"])]

                    final_edges += f"!{curr[0] * 20} {curr[1] * 20}|{nxt[0] * 20} {nxt[1] * 20}"
                
                edges.attrib["edges"] = final_edges

        
        with open(f"{xfl.shapes_dir}{shape['id']}.xml", 'wb') as file:
            file.write(tostring(symbol))
        
        SubElement(xfl.symbols, "Include", loadImmediate="true", itemIcon="1", href=f"Shapes/{shape['id']}.xml")


def init_dom(xfl):
    xfl.folders = SubElement(xfl.dom, "folders")
    xfl.media = SubElement(xfl.dom, "media")
    xfl.symbols = SubElement(xfl.dom, "symbols")
    xfl.timelines = SubElement(xfl.dom, "timelines")

    SubElement(xfl.folders, "DOMFolderItem", name="Resources", isExpanded="ture")
    SubElement(xfl.folders, "DOMFolderItem", name="Shapes", isExpanded="ture")

    os.mkdir(xfl.project_dir)
    os.mkdir(xfl.library_dir)
    os.mkdir(xfl.resources_dir)
    os.mkdir(xfl.shapes_dir)
    os.mkdir(xfl.binary_dir)


def generate_texturepacker_project(swf):
    pass


def convert_sc_to_xfl(swf):
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

    xfl.project_dir = os.path.splitext(swf.filename)[0]

    init_dom(xfl)

    convert_text_fields(swf)
    convert_shapes(swf, xfl)
    convert_movieclips(swf, xfl)

    # saving project
    with open(f"{xfl.project_dir}/DOMDocument.xml", 'wb') as dom:
        dom.write(tostring(xfl.dom))
    
    with open(f"{xfl.project_dir}/{os.path.basename(xfl.project_dir)}.xfl", 'w') as xfl:
        xfl.write("PROXY-CS5")
