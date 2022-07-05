import copy

import cv2
import numpy as np

from lib.utils import AffineTransform
# Affine matrix class for calculate bitmap transforms

from lib.sc.swf.shape import calculate_rotation, calculate_scale

from math import radians, sin, cos, ceil

from lib.xfl import *
from lib.xfl.dom.folder_item import DOMFolderItem
# Folder class for.. folders. just for better interaction with different types of symbols

from lib.xfl.dom.symbol_item import DOMSymbolItem
# Symboll item for shape and movieclip in DomDocument

from lib.xfl.dom.symbol_instance import DOMSymbolInstance
# Symboll instance class for using in movieclip or shape frames

from lib.xfl.dom.layer import DOMLayer
# Layer class. Used in all symboll types

from lib.xfl.dom.bitmap_item import DOMBitmapItem
# Bitmap item class for using in DomDocument

from lib.xfl.dom.bitmap_instance import DOMBitmapInstance

from lib.xfl.dom.layer import DOMFrame

from lib.xfl.dom.dynamic_text import DOMDynamicText
# Text instance. Contain text position and some other things

from lib.xfl.dom.text_run import DOMTextRun, DOMTextAttrs
# Subclass of DOMStaticText. Contain text and its settings

from lib.xfl.dom.shape import DOMShape
# Shape class for ColorFill

from lib.xfl.fill.fill_style import FillStyle
from lib.xfl.fill.solid_color import SolidColor
# Subclass for DomShape (color)

from lib.xfl.edge.edge import Edge
# Subclass for DomShape (shape)

from lib.xfl.geom.matrix import Matrix
# Transform matrix class

from lib.xfl.geom.color import Color

# Color transfrom class


# for use
KEY_MODE_NORMAL = 9728
KEY_MODE_CLASSIC_TWEEN = 22017
KEY_MODE_SHAPE_TWEEN = 17922
KEY_MODE_MOTION_TWEEN = 8195
KEY_MODE_SHAPE_LAYERS = 8192


def sc_to_xfl(swf):
    projectdir = os.path.splitext(swf.filename)[0]
    if os.path.exists(projectdir):
        rmtree(projectdir)

    os.makedirs(projectdir, exist_ok=True)

    # Xfl initialization
    sc_xfl = DOMDocument()
    sc_xfl.filepath = projectdir

    # some pretty functions
    def add_shape(shape, name):
        shape_symboll = DOMSymbolItem(name, "graphic")
        shape_symboll.timeline.name = name.split("/")[-1]

        prepared_shape = {
            "bitmaps": [],  # bitmap instances
            "colorFills": [],  # "color fill commands"
            "matrices": []
        }

        # Searching duplicate bitmaps and colorfills
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

        bitmap_layer = DOMLayer("Bitmaps")
        bitmap_frame = DOMFrame(index=0)
        bitmap_layer.frames.append(bitmap_frame)

        shape_symboll.timeline.layers.append(bitmap_layer)

        for bitmap_index, bitmap in enumerate(prepared_shape['bitmaps']):
            # creating main affine matrix
            at = AffineTransform()

            uv_coords = shape.bitmaps[bitmap_index].uv_coords
            xy_coords = shape.bitmaps[bitmap_index].xy_coords

            # building sprite bounding box
            image_box = cv2.boundingRect(np.array(uv_coords))
            a, b, c, d = image_box

            # checking for "color fill"
            is_color_fill = c + d <= 2
            prepared_shape["colorFills"].append(is_color_fill)

            if not is_color_fill:
                bitmap_name = f"Resources/{name.split('/')[-1]} {bitmap_index}"
                image_name = f"{name.split('/')[-1]} {bitmap_index}.png"

                if not isinstance(bitmap, int):
                    if c - 1 > 1 and not prepared_bitmap['simX']:
                        c -= 1
                    if d - 1 > 1 and not prepared_bitmap['simY']:
                        d -= 1

                    # ------------------------------------Bitmap matrix------------------------------------------------#
                    # getting rotation angle (in degrees) of bitmap vertices (xy_coords) and mirror option
                    rotation, mirroring = calculate_rotation(uv_coords, xy_coords)
                    rad_rot = radians(-rotation)

                    sx, sy, w, h = calculate_scale(
                        [[round(x * cos(rad_rot) + -y * sin(rad_rot)),
                          round(x * sin(rad_rot) + y * cos(rad_rot))]
                         for x, y in uv_coords], xy_coords)

                    left = min(coord[0] for coord in xy_coords)
                    top = min(coord[1] for coord in xy_coords)
                    at.translate(top, left)
                    at.scale(sx, sy)  # apply scale
                    # -----------------------------------------Bitmap image--------------------------------------------#
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

                    dom_bitmap = DOMBitmapItem(bitmap_name, f"M {name.split('/')[-1]} {bitmap_index}.dat")
                    dom_bitmap.use_imported_jpeg_data = False
                    dom_bitmap.compression_type = "lossless"
                    dom_bitmap.image = cropped
                    dom_bitmap.allow_smoothing = True if not swf.textures[bitmap["texture"]].linear else False
                    dom_bitmap.source_external_filepath = f"Resources/{image_name}"
                    cv2.imwrite(f"{image_path}{image_name}", cropped)

                    sc_xfl.media.update({dom_bitmap.name: dom_bitmap})
                else:
                    bitmap_name = f"Resources/{name.split('/')[-1]} {bitmap}"
                    pivot_coords = shape.bitmaps[bitmap].xy_coords

                    prepared_shape["colorFills"].append(prepared_shape["colorFills"][bitmap])

                    # Calculate rotation for bitmap image
                    rotation, mirroring = calculate_rotation(pivot_coords, xy_coords)
                    rad_rot = radians(-rotation)

                    # Calculate rotation for uv
                    uv_rotation, uv_mirroring = calculate_rotation(uv_coords, xy_coords)
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

                a, b, c, d, tx, ty = at.get_matrix()
                bitmap_matrix = Matrix(a, b, c, d, ty, tx)

                bitmap_instance = DOMBitmapInstance()
                bitmap_instance.library_item_name = bitmap_name
                bitmap_instance.matrix = bitmap_matrix

                bitmap_frame.elements.append(bitmap_instance)
            else:
                if isinstance(bitmap, int):
                    texture = swf.textures[prepared_shape["bitmaps"][bitmap]["texture"]].image
                    color_coords = prepared_shape["bitmaps"][bitmap]["uvCoords"][0]
                else:
                    texture = swf.textures[bitmap["texture"]].image
                    color_coords = bitmap["uvCoords"][0]

                x, y = color_coords
                color = texture[y, x]

                final_color = "#" + hex(color[2])[2:] + hex(color[1])[2:] + hex(color[0])[2:]

                final_edges = ""
                for x, curr in enumerate(xy_coords):
                    nxt = xy_coords[(x + 1) % len(xy_coords)]
                    final_edges += f"!{curr[0] * 20} {curr[1] * 20}|{nxt[0] * 20} {nxt[1] * 20}"
                    # converting pixels to twips (again.) (1 twip = 1/20 pixel)

                # Colorfill color
                colorfill_color = FillStyle(1)
                colorfill_color.data = SolidColor(final_color, color[3] / 255)

                # Colorfill shape
                colorfill_edge = Edge()
                colorfill_edge.edges = final_edges
                colorfill_edge.fill_style1 = 1

                colorfill = DOMShape()
                colorfill.fills.append(colorfill_color)
                colorfill.edges.append(colorfill_edge)
                bitmap_frame.elements.append(colorfill)

        sc_xfl.symbols.update({name: shape_symboll})

    # Folders initialization
    Resources = DOMFolderItem("Resources")

    image_path = f"{sc_xfl.librarypath}/Resources/"
    os.makedirs(image_path, exist_ok=True)

    Shapes = DOMFolderItem("Shapes")

    Exports = DOMFolderItem("Exports")

    sc_xfl.folders.append(Resources)
    sc_xfl.folders.append(Shapes)
    sc_xfl.folders.append(Exports)

    # Some storages for using in frames
    text_field_storage = {text_field.id: text_field for text_field in swf.text_fields}
    shapes_storage = {shape.id: shape for shape in swf.shapes}
    modifers_storage = {modifer.id: modifer for modifer in swf.movieclip_modifiers}

    for movieclip in swf.movieclips:
        movie_symbol = DOMSymbolItem()
        movie_symbol.timeline.name = movieclip.id

        movie_name = movieclip.id
        movie_save_name = movieclip.id
        if movieclip.id in swf.exports:
            movie_symbol.timeline.name = swf.exports[movieclip.id]
            movie_name = f"Exports/{swf.exports[movieclip.id]}"
            movie_save_name = f"Exports/{movieclip.id}"

        prepared_bind_layers = {}
        bind_layers = []
        movie_bind_instances = []  # bind instances for using in frames
        for i, bind in enumerate(movieclip.binds):
            if bind['id'] not in modifers_storage:
                # Layers
                bind_layer = DOMLayer(f"Layer_{i}")
                for f_i in range(len(movieclip.frames)):
                    empty_frame = DOMFrame(f_i)
                    bind_layer.frames.append(empty_frame)

                bind_layers.append(bind_layer)

                # Symbolls
                if movieclip.nine_slice and bind['id'] in swf.shapes_ids:  # TODO add slice
                    instance = DOMBitmapInstance()  # for first time

                elif bind['id'] in swf.shapes_ids or bind['id'] in swf.movieclips_ids:
                    instance = DOMSymbolInstance()

                    if bind["id"] in swf.shapes_ids:
                        instance.library_item_name = f"Shapes/{bind['id']}"
                        if instance.library_item_name not in sc_xfl.symbols:
                            add_shape(shapes_storage[bind['id']], instance.library_item_name)

                    elif bind["id"] in swf.movieclips_ids and bind['id'] in swf.exports:
                        instance.library_item_name = f"Exports/{swf.exports[bind['id']]}"

                    elif bind["id"] in swf.movieclips_ids:
                        instance.library_item_name = bind['id']

                elif bind['id'] in swf.text_fields_ids:
                    bind_text = text_field_storage[bind['id']]

                    instance = DOMDynamicText()
                    instance.width = bind_text.right_corner - bind_text.left_corner
                    instance.height = bind_text.bottom_corner - bind_text.top_corner

                    if bind_text.multiline:
                        instance.line_type = "multiline"

                    instance_text = DOMTextRun()
                    instance_text.characters = bind_text.text

                    instance_text_atr = DOMTextAttrs()
                    instance_text_atr.face = bind_text.font_name
                    instance_text_atr.size = bind_text.font_size
                    instance_text_atr.bitmap_size = bind_text.font_size
                    instance_text_atr.left_margin = bind_text.left_corner
                    instance_text_atr.right_margin = bind_text.right_corner
                    instance_text_atr.fill_color = "#" + hex(bind_text.font_color & 0x00FFFFFF)[2:]
                    instance_text_atr.alpha = ((bind_text.font_color & 0xFF000000) >> 24) / 255

                    instance_text.text_attrs.append(instance_text_atr)
                    instance.text_runs.append(instance_text)

                instance.name = bind['name']
                movie_bind_instances.append(instance)
            else:
                bind_layers.append(None)
                movie_bind_instances.append(None)
        # TODO framerate

        parent_layers = []
        added_bind_layer = {}
        for i, frame in enumerate(movieclip.frames):
            mask = False
            mask_child = False
            mask_idx = 0
            for element in frame.elements:
                if movieclip.binds[element['bind']]['id'] in modifers_storage:
                    modifer_value = modifers_storage[movieclip.binds[element['bind']]['id']].stencil
                    if modifer_value == 2:
                        mask = True
                    elif modifer_value == 3:
                        mask_child = True
                    elif modifer_value == 4:
                        mask_child = False
                        mask_idx = 0
                else:
                    if element['bind'] not in prepared_bind_layers:
                        layer_is_prepared = [(el['bind'] in prepared_bind_layers) for el in frame.elements]
                        if True in layer_is_prepared and layer_is_prepared.index(True) > element['bind']:
                            layer_list = [{key: prepared_bind_layers[key]} for key in prepared_bind_layers]
                            layer_list.insert([key for key in prepared_bind_layers].index(frame.elements[layer_is_prepared.index(True)]['bind']), {element['bind']: bind_layers[element['bind']]})
                            prepared_bind_layers = {key: layer[key] for layer in layer_list for key in layer}

                        else:
                            prepared_bind_layers.update({element['bind']: bind_layers[element['bind']]})

                    bind_layer = bind_layers[element['bind']]

                    bind_frame = bind_layer.frames[i]
                    bind_frame.name = frame.name
                    bind_frame.key_mode = KEY_MODE_NORMAL
                    bind_frame.blend_mode = movieclip.binds[element['bind']]['blend']

                    instance = copy.deepcopy(movie_bind_instances[element['bind']])

                    if element["matrix"] != 0xFFFF:
                        a, b, c, d, tx, ty = swf.matrix_banks[movieclip.matrix_bank].matrices[element["matrix"]]
                        instance.matrix = Matrix(a, b, c, d, tx, ty)

                    if element["color"] != 0xFFFF:
                        r_add, g_add, b_add, a_add, r_multi, g_multi, b_multi, a_multi = \
                            swf.matrix_banks[movieclip.matrix_bank].color_transforms[element["color"]]
                        bind_color = Color()
                        bind_color.red_offset = r_add
                        bind_color.green_offset = g_add
                        bind_color.blue_offset = b_add
                        bind_color.alpha_offset = a_add
                        bind_color.red_multiplier = r_multi
                        bind_color.green_multiplier = g_multi
                        bind_color.blue_multiplier = b_multi
                        bind_color.alpha_multiplier = a_multi
                        instance.color = bind_color

                    bind_frame.elements.append(instance)

                    if mask:
                        bind_layer.layer_type = "mask"
                        bind_layer.is_locked = True
                        mask_idx = element['bind']
                        mask = False
                    if mask_child:
                        parent_layers.append({mask_idx: bind_layer})
                        bind_layer.parent_layer_index = mask_idx
                        bind_layer.is_locked = True

                    bind_layers[element['bind']] = bind_layer

        for layer_key in prepared_bind_layers:
            bind_layer = prepared_bind_layers[layer_key]

            if bind_layer.parent_layer_index is None:
                added_bind_layer.update({layer_key: bind_layer})
                movie_symbol.timeline.layers.append(bind_layer)

        for parent_layer in parent_layers:
            for layer_idx in parent_layer:
                parent_idx = list(added_bind_layer).index(layer_idx)
                parent_layer[layer_idx].parent_layer_index = parent_idx
                movie_symbol.timeline.layers.insert(parent_idx + 1, parent_layer[layer_idx])

                add_index = list(added_bind_layer)
                add_index.insert(parent_idx + 1, bind_layers.index(parent_layer[layer_idx]))
                add_layer = [added_bind_layer[key] for key in added_bind_layer]
                add_layer.insert(parent_idx + 1, parent_layer[layer_idx])

                added_bind_layer = {add_index[i]: add_layer[i] for i in range(len(add_index))}

        movie_symbol.name = movie_name
        sc_xfl.symbols.update({movie_save_name: movie_symbol})

    # XFL.save(projectdir, sc_xfl)
    sc_xfl.save(projectdir)  # save as xfl
