import copy

import cv2
import numpy as np

from math import degrees

from lib.sc.swf import *

from lib.sc.swf.shape import calculate_size
from lib.xfl import *
from lib.xfl.dom.bitmap_instance import DOMBitmapInstance
from lib.xfl.dom.bitmap_item import DOMBitmapItem
from lib.xfl.dom.dynamic_text import DOMDynamicText
from lib.xfl.dom.folder_item import DOMFolderItem
from lib.xfl.dom.layer import DOMFrame
from lib.xfl.dom.layer import DOMLayer
from lib.xfl.dom.shape import DOMShape
from lib.xfl.dom.symbol_instance import DOMSymbolInstance
from lib.xfl.dom.symbol_item import DOMSymbolItem
from lib.xfl.dom.text_run import DOMTextRun, DOMTextAttrs
from lib.xfl.edge.edge import Edge
from lib.xfl.fill.fill_style import FillStyle
from lib.xfl.fill.solid_color import SolidColor
from lib.xfl.fill.bitmap_fill import BitmapFill
from lib.xfl.geom.color import Color
from lib.xfl.geom.matrix import Matrix
from lib.xfl.dom.group import DOMGroup

# for use
KEY_MODE_NORMAL = 9728
KEY_MODE_CLASSIC_TWEEN = 22017
KEY_MODE_SHAPE_TWEEN = 17922
KEY_MODE_MOTION_TWEEN = 8195
KEY_MODE_SHAPE_LAYERS = 8192


def sc_to_xfl(filepath):
    swf = SupercellSWF()
    swf.load(filepath)
    print()

    projectdir = os.path.splitext(swf.filename)[0]
    if os.path.exists(projectdir):
        rmtree(projectdir)

    os.makedirs(projectdir, exist_ok=True)

    # Xfl initialization
    sc_xfl = DOMDocument()
    sc_xfl.filepath = projectdir

    # Folders initialization
    Resources = DOMFolderItem("Resources")

    image_path = f"{sc_xfl.librarypath}/Resources/"
    os.makedirs(image_path, exist_ok=True)

    Shapes = DOMFolderItem("Shapes")

    Exports = DOMFolderItem("Exports")

    sc_xfl.folders.append(Resources)
    sc_xfl.folders.append(Shapes)
    sc_xfl.folders.append(Exports)

    shapes_uvs = []
    shapes_colorfill = {}

    for shape in swf.shapes:
        shapes_colorfill[shape.id] = []
        for bitmap in shape.bitmaps:
            uv = bitmap.uv_coords
            xy = bitmap.xy_coords

            if uv not in shapes_uvs:
                shapes_uvs.append(uv)
            if sum(calculate_size(uv)) <= 2:
                tex = swf.textures[bitmap.texture_index].image
                x, y = uv[-1]
                px = tex[y, x]

                color = "#000000"
                alpha = 0
                if tex.shape[2] == 4:
                    color = "#{:02x}{:02x}{:02x}".format(px[2], px[1], px[0])
                    alpha = px[3] / 255
                elif tex.shape[2] == 3:
                    color = "#{:02x}{:02x}{:02x}".format(px[2], px[1], px[0])
                elif tex.shape[1] == 1:
                    "#{:02x}{:02x}{:02x}".format(px[0], px[0], px[0])

                final_edges = ""
                for x, curr in enumerate(xy):
                    nxt = xy[(x + 1) % len(xy)]
                    final_edges += f"!{curr[0] * 20} {curr[1] * 20}|{nxt[0] * 20} {nxt[1] * 20}"
                    # converting pixels to twips (again.) (1 twip = 1/20 pixel)

                # Colorfill color
                colorfill_color = FillStyle(1)
                colorfill_color.data = SolidColor(color, alpha)

                # Colorfill shape
                colorfill_edge = Edge()
                colorfill_edge.edges = final_edges
                colorfill_edge.fill_style1 = 1

                colorfill = DOMShape()
                colorfill.fills.append(colorfill_color)
                colorfill.edges.append(colorfill_edge)
                shapes_colorfill[shape.id].append(colorfill)
                continue

            shapes_colorfill[shape.id].append(None)

    shapes_box = [None for _ in range(len(shapes_uvs))]

    for movieclip in swf.movieclips:
        movie_symbol = DOMSymbolItem()
        movie_symbol.timeline.name = movieclip.id

        bind_layers = []
        movie_bind_instances = []  # bind instances for using in frames
        for i, bind in enumerate(movieclip.binds):
            if bind['id'] not in swf.modifers_ids:
                # Layers
                bind_layer = DOMLayer(f"Layer_{i}")

                bind_layers.append(bind_layer)

                if bind['id'] in swf.shapes_ids and movieclip.nine_slice:
                    movie_symbol.scale_grid_left = movieclip.nine_slice[0]
                    movie_symbol.scale_grid_top = movieclip.nine_slice[1]

                    movie_symbol.scale_grid_right = movieclip.nine_slice[2] + movieclip.nine_slice[0]
                    movie_symbol.scale_grid_bottom = movieclip.nine_slice[3] + movieclip.nine_slice[1]

                    shape = swf.shapes[swf.shapes_ids.index(bind["id"])]
                    instance = DOMGroup()
                    for b_i, bitmap in enumerate(reversed(shape.bitmaps)):
                        slice = DOMShape()
                        slice.is_drawing_object = True

                        uv_index = shapes_uvs.index(bitmap.uv_coords)

                        if shapes_box[uv_index] is None:
                            resource_name = f"M {uv_index}"
                            image_name = f"{uv_index}.png"

                            matrix, sprite_box, nearest = bitmap.get_matrix(None, True)
                            shapes_box[uv_index] = sprite_box

                            image = bitmap.get_image(swf.textures)

                            if nearest in [270, -90]:
                                image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                            elif nearest in [180, -180]:
                                image = cv2.rotate(image, cv2.ROTATE_180)
                            elif nearest in [90, -270]:
                                image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

                            dom_bitmap = DOMBitmapItem(f"Resources/{uv_index}", f"{resource_name}.dat")
                            dom_bitmap.use_imported_jpeg_data = False
                            dom_bitmap.img = "lossless"
                            dom_bitmap.image = image
                            dom_bitmap.allow_smoothing = False or not swf.textures[
                                bitmap.texture_index].linear
                            dom_bitmap.source_external_filepath = f"Resources/{image_name}"
                            cv2.imwrite(f"{image_path}{image_name}", image)
                            sc_xfl.media.update({uv_index: dom_bitmap})
                        else:
                            matrix, sprite_box, _ = bitmap.get_matrix(shapes_box[uv_index], False)

                        values = matrix.get_matrix()

                        bitmap_matrix = Matrix(values[0][0], values[1][0], values[0][1],
                                               values[1][1], values[0][2], values[1][2])

                        slice_edge = ""
                        for x, curr in enumerate(sprite_box):
                            nxt = sprite_box[(x + 1) % len(sprite_box)]
                            slice_edge += f"!{round(curr[0] * 20)} {round(curr[1] * 20)}|{round(nxt[0] * 20)} {round(nxt[1] * 20)}"

                        slice_style = FillStyle(1)
                        slice_bitmap_fill = BitmapFill(f"Resources/{uv_index}")
                        slice_bitmap_fill.matrix = Matrix(20, 0, 0, 20, 0, 0) #sy*20, round(tx, 2), round(ty, 2))
                        slice_style.data = slice_bitmap_fill

                        slice_shape = Edge()
                        slice_shape.edges = slice_edge
                        slice_shape.fill_style1 = 1

                        slice.fills.append(slice_style)
                        slice.edges.append(slice_shape)
                        slice.matrix = bitmap_matrix
                        instance.members.append(slice)

                elif bind['id'] in swf.shapes_ids or bind['id'] in swf.movie_ids:
                    instance = DOMSymbolInstance()

                    if bind["id"] in swf.shapes_ids:
                        shape = swf.shapes[swf.shapes_ids.index(bind["id"])]
                        name = f"Shapes/{bind['id']}"
                        instance.library_item_name = name
                        if name not in sc_xfl.symbols:
                            shape_symboll = DOMSymbolItem(name, "graphic")
                            shape_symboll.timeline.name = name.split("/")[-1]

                            for b_i, bitmap in enumerate(reversed(shape.bitmaps)):
                                bitmap_layer = DOMLayer(f"Bitmap_{b_i}")
                                bitmap_frame = DOMFrame(index=0)

                                uv_index = shapes_uvs.index(bitmap.uv_coords)

                                if not shapes_colorfill[bind['id']][b_i]:
                                    if shapes_box[uv_index] is None:
                                        resource_name = f"M {uv_index}"
                                        image_name = f"{uv_index}.png"

                                        matrix, sprite_box, nearest = bitmap.get_matrix(None, True)
                                        shapes_box[uv_index] = sprite_box

                                        image = bitmap.get_image(swf.textures)

                                        if nearest in [270, -90]:
                                            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                                        elif nearest in [180, -180]:
                                            image = cv2.rotate(image, cv2.ROTATE_180)
                                        elif nearest in [90, -270]:
                                            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

                                        dom_bitmap = DOMBitmapItem(f"Resources/{uv_index}", f"{resource_name}.dat")
                                        dom_bitmap.use_imported_jpeg_data = False
                                        dom_bitmap.img = "lossless"
                                        dom_bitmap.image = image
                                        dom_bitmap.allow_smoothing = False or not swf.textures[
                                            bitmap.texture_index].linear
                                        dom_bitmap.source_external_filepath = f"Resources/{image_name}"
                                        cv2.imwrite(f"{image_path}{image_name}", image)
                                        sc_xfl.media.update({uv_index: dom_bitmap})
                                    else:
                                        matrix, _, _ = bitmap.get_matrix(shapes_box[uv_index], False)

                                    matrix = matrix.get_matrix()

                                    bitmap_matrix = Matrix(matrix[0][0], matrix[1][0], matrix[0][1],
                                                           matrix[1][1], matrix[0][2], matrix[1][2])

                                    bitmap_instance = DOMBitmapInstance()
                                    bitmap_instance.library_item_name = f"Resources/{uv_index}"
                                    bitmap_instance.matrix = bitmap_matrix

                                    bitmap_frame.elements.append(bitmap_instance)
                                else:
                                    bitmap_frame.elements.append(shapes_colorfill[bind['id']][b_i])

                                bitmap_layer.frames.append(bitmap_frame)
                                shape_symboll.timeline.layers.append(bitmap_layer)

                            sc_xfl.symbols.update({name: shape_symboll})

                    elif bind["id"] in swf.movie_ids:
                        if not swf.movieclips[swf.movie_ids.index(bind['id'])].nine_slice and not bind['name']:
                            instance.type = "graphic"

                        if bind['id'] in swf.exports:
                            instance.library_item_name = f"Exports/{swf.exports[bind['id']][0]}"
                        else:
                            instance.library_item_name = bind['id']

                elif bind['id'] in swf.fields_ids:
                    bind_text = swf.text_fields[swf.fields_ids.index(bind["id"])]

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

                movie_bind_instances.append(instance)
                continue

            bind_layers.append(None)
            movie_bind_instances.append(None)

        layer_sequence = [bind_layers.index(lay) for lay in [layer for layer in bind_layers if layer != None]]
        parent_layers = {}
        for i, frame in enumerate(movieclip.frames):
            empty_frames = []
            mask = False
            mask_child = False
            mask_idx = None
            element_idx = 0
            frame_elements = [element['bind'] for element in frame.elements if movieclip.binds[element['bind']]['id'] not in swf.modifers_ids]
            for element in frame.elements:
                empty_frames.append(element['bind'])
                if movieclip.binds[element['bind']]['id'] in swf.modifers_ids:
                    modifer_value = swf.movieclip_modifiers[swf.modifers_ids.index(movieclip.binds[element['bind']]['id'])].type
                    if modifer_value == 2:
                        mask = True
                    elif modifer_value == 3:
                        mask_child = True
                    elif modifer_value == 4:
                        mask_child = False
                    continue
                else:
                    element_pos = frame_elements.index(element["bind"])
                    element_list_pos = layer_sequence.index(element["bind"])
                    for list_element in frame_elements:
                        if element != list_element:
                            list_element_pos = frame_elements.index(list_element)
                            list_element_list_pos = layer_sequence.index(list_element)

                            layer_pos = element_pos > list_element_pos
                            layer_list_pos = element_list_pos > list_element_list_pos

                            if layer_pos != layer_list_pos:
                                if not layer_list_pos:
                                    active_layer_element = layer_sequence.pop(list_element_list_pos)
                                    layer_sequence.insert(layer_sequence.index(element["bind"]), active_layer_element)

                bind_layer = bind_layers[element['bind']]

                if mask:
                    bind_layer.layer_type = "mask"
                    bind_layer.is_locked = True
                    mask_idx = element['bind']
                    mask = False
                if mask_child and mask_idx:
                    if mask_idx not in parent_layers:
                        parent_layers[mask_idx] = []

                    bind_layer.is_locked = True
                    if bind_layer not in parent_layers[mask_idx]:
                        parent_layers[mask_idx].append(bind_layer)

                if i and element in movieclip.frames[i - 1].elements and frame.name == movieclip.frames[i-1].name:
                    bind_layer.frames[-1].duration += 1
                    continue

                bind_frame = DOMFrame(index=i)
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
                bind_layer.frames.append(bind_frame)
                bind_layers[element['bind']] = bind_layer
                element_idx += 1

            for bind_i in range(len(movieclip.binds)):
                if bind_i not in [element['bind'] for element in frame.elements]:
                    layer = bind_layers[bind_i]
                    if layer is not None:
                        if i + 1 != len(layer.frames):
                            if not i or len(layer.frames[-1].elements) != 0:
                                layer.frames.append(DOMFrame(index=i))
                            else:
                                layer.frames[-1].duration += 1

        for layer_key in reversed(layer_sequence):
            bind_layer = bind_layers[layer_key]

            movie_symbol.timeline.layers.append(bind_layer)

        for layer_idx in parent_layers:
            layers = parent_layers[layer_idx]
            for child_layer in layers:
                names = [layer.name for layer in movie_symbol.timeline.layers]
                parent_idx = names.index(f"Layer_{layer_idx}")
                child_layer.parent_layer_index = parent_idx
                movie_symbol.timeline.layers.insert(parent_idx + 1, child_layer)

        if movieclip.id in swf.exports:
            for export in swf.exports[movieclip.id]:
                export_instance = copy.deepcopy(movie_symbol)
                symbol_name = f"Exports/{export}"
                export_instance.timeline.name = export
                export_instance.name = symbol_name

                sc_xfl.symbols.update({symbol_name: export_instance})
        else:
            movie_symbol.timeline.name = movieclip.id
            movie_symbol.name = movieclip.id
            sc_xfl.symbols.update({movieclip.id: movie_symbol})

    # XFL.save(f"{projectdir}.fla", sc_xfl)
    sc_xfl.save(projectdir)  # save as xfl
