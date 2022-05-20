import os

import cv2
import numpy as np

from math import radians, cos, sin

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
shape_ids = []


# collect all text fields to one dictionary
def convert_text_fields(swf):
    for text_field in swf.text_fields:
        text_field_actions[text_field.id] = text_field


# proceed movies
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
        layers_list = [] # for layers reversing
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

                    # adding shape or another movie instance as frame element from main scene
                    if bind["id"] in shape_ids or bind["id"] in movieclip_ids:
                        frame_element_name = f"Shapes/{bind['id']}" if bind["id"] in shape_ids else str(bind["id"])
                        frame_element = SubElement(frame_elements, "DOMSymbolInstance", libraryItemName=frame_element_name, loop="loop")
                    
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
                            "redOffset": str(color[0] * 255),
                            "greenOffset": str(color[1] * 255),
                            "blueOffset": str(color[2] * 255),
                            "alphaOffset": str(color[3] * 255),
                            "redMultiplier": str(color[4]),
                            "greenMultiplier": str(color[5]),
                            "blueMultiplier": str(color[6]),
                            "alphaMultiplier": str(color[7]),
                        }
        
            layer_idx += 1
            layers_list.append(layer)

        # reversing layers (because Adobe Animate says YES.)
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
            "matrices": [], # instance matrices
            "colorFills": [] # "color fill commands"
        }

        for bitmap in shape.bitmaps[::-1]:
            # X and Y uv coords for calculating "color fill"
            uv_x = [coord[0] for coord in bitmap.uv_coords]
            uv_y = [coord[1] for coord in bitmap.uv_coords]

            prepared_bitmap = {
                "texture": bitmap.texture_index,
                "uvCoords": bitmap.uv_coords,
                "simX": uv_x.count(uv_x[0]) == len(uv_x), # finding similiar X coordinates for calculating "color fill"
                "simY": uv_y.count(uv_y[0]) == len(uv_y) # and also Y coordinates for it
            }

            # building sprite bounding box
            a, b, c, d = cv2.boundingRect(np.array(bitmap.uv_coords, dtype=np.int32))
            if c - a - 1 and not prepared_bitmap['simX']:
                c -= 1
            if d - b - 1 and not prepared_bitmap['simY']:
                d -= 1
            
            prepared_bitmap["rect"] = a, b, c, d

            # getting rotation angle (in degrees) of bitmap vertices (xy_coords) and mirror option
            rotation, mirroring = calculate_rotation2(bitmap)
            radians_rotation = radians(rotation)

            # at this point little message for Adobe Animate...
            # WHY DO AFFINE TRANSFORMATION MATRICES WORK DIFFERENTLY IN BITMAP INSTANCES AND OTHER INSTANCES?
            # WHY NORMAL 90 DEGREES ROTATED MATRIX AND 90 DEGREES ROTATED MATRIX IN ADOBE IS DIFFERENT MF????
            # HOT TO F CREATE MATRIX LIKE IN ADOBE ANIMATE???
            # HELP. ~ from 31 and SV

            # creating rotation matrix
            rotation_matrix = AffineTransform()
            rotation_matrix.rotate(radians_rotation) # apply rotation
            rotation_matrix = rotation_matrix.get_matrix() # get it as list

            # getting scaling (X & Y) and size (Width & Height) of bitmap vertices (xy_coords)
            sx, sy, w, h, uv_w, uv_h = calculate_scale([[ -rotation_matrix[2] * point[0] + rotation_matrix[3] * point[1], rotation_matrix[0] * point[0] + -rotation_matrix[1] * point[1]] for point in bitmap.uv_coords], bitmap.xy_coords)

            # creating main affine matrix
            at = AffineTransform()
            at.scale(sx, sy) # apply scale
            at.rotate(radians_rotation) # apply rotation

            # apply rotation to image bounding box
            image_box = [[0, 0], [0, h], [w, h], [w, 0]]
            for point_index in range(4):
                point = image_box[point_index]

                x, y = point
                xx = round(x * cos(radians_rotation) + -y * sin(radians_rotation))
                yy = round(x * sin(radians_rotation) + y * cos(radians_rotation))

                image_box[point_index] = [xx, yy]

            # returning image point to center
            for point_index in range(4):
                point = image_box[point_index]
                if point[0] < 0:
                    image_box = [[box_point[0] - point[0], box_point[1]] for box_point in image_box]
                    at.tx += -point[0]

                if point[1] < 0:
                    image_box = [[box_point[0], box_point[1] - point[1]] for box_point in image_box]
                    at.ty += -point[1]

            if rotation == 180:
                tx = at.tx
                ty = at.ty

                at.tx = ty
                at.ty = tx

            #at.translate(y_center - v_center,x_center - u_center) # shit

            #if shape.id == 1: print(image_box)
            #if shape.id == 6: print(at.get_matrix(), image_box)
            if shape.id == 443: print(at.get_matrix(), image_box, rotation)

            # return it if u want it
            #at.tx -= x_center + (w/2)
            #at.ty -= y_center + (h/2)

            # applying translation
            #u_center, v_center = get_center(image_box) # reserve
            x_center, y_center = get_center(bitmap.xy_coords)

            at.tx -= h / 2
            at.ty -= w / 2

            at.tx += x_center
            at.ty += y_center

            # applying mirror option
            '''if not mirroring:
                at.scale(-1, 1)
                at.tx *= -1'''

            # adding matrix
            prepared_shape["matrices"].append(at.get_matrix())

            # checking for "color fill"
            is_color_fill = bitmap.uv_coords.count(bitmap.uv_coords[0]) == len(bitmap.uv_coords)
            prepared_shape["colorFills"].append(is_color_fill)

            if is_color_fill:
                prepared_bitmap["twips"] = bitmap.xy_coords # adding vertices for "color fill"

            # checking for dublicate (instancing)
            if prepared_bitmap not in prepared_shape["bitmaps"]:
                prepared_shape["bitmaps"].append(prepared_bitmap)
            else:
                prepared_shape["bitmaps"].append(prepared_shape["bitmaps"].index(prepared_bitmap))
            
        prepared_shapes.append(prepared_shape)
    
    # saving prepared bitmaps to Adobe Animate image binary format
    for shape in prepared_shapes:
        for bitmap in shape["bitmaps"]:
            # checking if it not dublicate
            if not isinstance(bitmap, int) and not shape["colorFills"][shape["bitmaps"].index(bitmap)]:
                # creating binary mask and cropping sprite
                texture = swf.textures[bitmap["texture"]]
                points = np.array(bitmap["uvCoords"], dtype=np.int32)
                mask = np.zeros(texture.image.shape[:2], dtype=np.uint8)

                cv2.drawContours(mask, [points], -1, (255, 255, 255), -1)
                res = cv2.bitwise_and(texture.image, texture.image, mask=mask)
                a, b, c, d = bitmap['rect']
                cropped = res[b: b + d, a: a + c]

                binary = Bitmap()
                binary_name = f"M {shape['id']} {shape['bitmaps'].index(bitmap)}.dat"
                with open(f"{xfl.binary_dir}{binary_name}", 'wb') as file:
                    file.write(binary.save(cropped))
                
                # for debug
                #cv2.imwrite(f"{xfl.resources_dir}{shape['id']} {shape['bitmaps'].index(bitmap)}.png", cropped)
                
                # including this media file to main scene library
                SubElement(xfl.media, "DOMBitmapItem", name=f"Resources/{shape['id']} {shape['bitmaps'].index(bitmap)}", allowSmoothing="true", compressionType="lossless", useImportedJPEGData="false", quality="100", bitmapDataHRef=binary_name)

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

        for bitmap in shape["bitmaps"]:
            if isinstance(bitmap, int):
                index = bitmap
            else:
                index = shape["bitmaps"].index(bitmap)
            
            # creating bitmap instance
            if not shape["colorFills"][shape["bitmaps"].index(bitmap)]:
                item_name = f"Resources/{shape['id']} {index}"
                instance = SubElement(frame_elements, "DOMBitmapInstance", libraryItemName=item_name)

                matrix_holder = SubElement(SubElement(instance, "matrix"), "Matrix")

                matrix = shape["matrices"][shape["bitmaps"].index(bitmap)]
                matrix_values = {}

                if matrix[0] != 1:
                    matrix_values["a"] = '%g'%(matrix[0])
                if matrix[1]:
                    matrix_values["b"] = '%g'%(matrix[1])
                if matrix[2]:
                    matrix_values["c"] = '%g'%(matrix[2])
                if matrix[3] != 1:
                    matrix_values["d"] = '%g'%(matrix[3])
                if matrix[4]:
                    matrix_values["ty"] = round(matrix[4])
                if matrix[5]:
                    matrix_values["tx"] = round(matrix[5])

                matrix_holder.attrib = {value:str(matrix_values[value]) for value in matrix_values}
            
            # creating "color fill"
            else:
                texture = swf.textures[bitmap["texture"]]

                fill_item = SubElement(frame_elements, "DOMShape")

                fill = SubElement(SubElement(fill_item, "fills"), "FillStyle", index="1")

                # fill color
                color = texture.image[round(bitmap["simX"]), round(bitmap["simY"])]
                final_color = hex(color[2])[2:] + hex(color[1])[2:] + hex(color[0])[2:]
                SubElement(fill, "SolidColor", color="#" + final_color, alpha=str(color[3] / 255))

                edges = SubElement(SubElement(fill_item, "edges"), "Edge", fillStyle1="1")

                # filling polygon coordinates
                final_edges = ""
                for x in range(len(bitmap["twips"])):
                    curr = bitmap["twips"][x]
                    nxt = bitmap["twips"][(x + 1) % len(bitmap["twips"])]

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
