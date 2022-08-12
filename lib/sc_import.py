import copy

from lib.console import Console
from PIL import Image

from lib.sc import *
from lib.fla import *

shape_bitmaps_uvs = []
shape_bitmaps_twips = []
shapes_with_nine_slices = {}


def sc_to_fla(filepath):
    swf = SupercellSWF()
    swf.load(filepath)

    projectdir = os.path.splitext(swf.filename)[0]
    if os.path.exists(projectdir):
        rmtree(projectdir)

    os.makedirs(projectdir, exist_ok=True)

    fla = prepare_document()

    startup = DOMDocument()
    startup.load("lib/scwmake_credit")

    fla.timelines = startup.timelines

    proceed_resources(fla, swf)

    fla.save(projectdir)


def prepare_document():
    Console.info("Creating DOMDocument for Adobe Animate...")

    fla = DOMDocument()

    fla.xfl_version = 2.971

    fla.width = 1280
    fla.height = 720
    fla.frame_rate = 30
    fla.current_timeline = 1

    fla.background_color = 0x666666

    fla.creator_info = "File generated with SC tool by SCW Make! (VK: vk.com/scwmake, GITHUB: github.com/scwmake/SC)"

    folder_shapes = DOMFolderItem("shapes")
    folder_movieclips = DOMFolderItem("movieclips")
    folder_exports = DOMFolderItem("exports")
    folder_resources = DOMFolderItem("resources")

    fla.folders.append(folder_shapes)
    fla.folders.append(folder_movieclips)
    fla.folders.append(folder_exports)
    fla.folders.append(folder_resources)

    return fla


def proceed_resources(fla, swf):
    resource_counter = 0
    for id, resource in swf.resources.items():
        Console.progress_bar("Converting SupercellFlash resources to Adobe Animate...", resource_counter,
                             swf.movieclips_count + swf.shapes_count)
        if isinstance(resource, Shape):
            convert_shape(fla, swf, resource)

        elif isinstance(resource, MovieClip):
            export_names = swf.exports[id] if id in swf.exports else None
            convert_movieclip(fla, swf, resource, export_names)
        else:
            continue
        resource_counter += 1

    print()

def convert_shape(fla, swf, shape):
    graphic = DOMSymbolItem(f"shapes/shape_{shape.id}", "graphic")
    graphic.timeline.name = f"shape_{shape.id}"

    for bitmap_index, bitmap in enumerate(reversed(shape.bitmaps)):
        layer = DOMLayer(f"shape_layer_{bitmap_index}", False)
        frame = DOMFrame(index=0)

        uv_coords = bitmap.uv_coords
        xy_coords = bitmap.xy_coords

        if uv_coords.count(uv_coords[0]) == len(uv_coords):  # color fills is always 1x1
            color_fill = DOMShape()
            texture = swf.textures[bitmap.texture_index]

            x, y = uv_coords[0]
            pixel = texture.image.getpixel((int(x), int(y)))

            color = 0
            alpha = 1.0

            if len(pixel) in (4, 3):
                color |= pixel[0] << 16
                color |= (pixel[1] << 16) >> 8
                color |= pixel[2]

                if len(pixel) == 4:
                    alpha = pixel[3] / 255

            elif len(pixel) in (2, 1):
                color |= pixel[0] << 16
                color |= (pixel[0] << 16) >> 8
                color |= pixel[0]

                if len(pixel) == 2:
                    alpha = pixel[1] / 255

            color_fill_style = FillStyle(1)
            color_fill_style.data = SolidColor(color, alpha)

            final_edges = ""
            for x, curr in enumerate(xy_coords):
                nxt = xy_coords[(x + 1) % len(xy_coords)]
                final_edges += f"!{curr[0] * 20} {curr[1] * 20}|{nxt[0] * 20} {nxt[1] * 20}"  # converting pixels to twips

            color_fill_edge = Edge()
            color_fill_edge.edges = final_edges
            color_fill_edge.fill_style1 = 1

            color_fill.fills.append(color_fill_style)
            color_fill.edges.append(color_fill_edge)

            frame.elements.append(color_fill)

        else:
            if uv_coords not in shape_bitmaps_uvs:
                shape_bitmaps_uvs.append(uv_coords)

                uvs_index = shape_bitmaps_uvs.index(uv_coords)
                resource_name = f"M {uvs_index}"

                matrix, twips, rotation, mirror = bitmap.get_matrix(use_nearest=True)
                shape_bitmaps_twips.append(twips)

                bitmap_item = DOMBitmapItem(f"resources/{uvs_index}", f"{resource_name}.dat")

                bitmap_item.quality = 100
                bitmap_item.use_imported_jpeg_data = False
                bitmap_item.allow_smoothing = swf.textures[bitmap.texture_index].linear != True
                bitmap_item.source_external_filepath = f"LIBRARY/resources/{uvs_index}.png"

                sprite = bitmap.get_image(swf)
                sprite = sprite.rotate(-rotation, expand = True)
                if mirror:
                    sprite.transpose(Image.FLIP_LEFT_RIGHT)
                bitmap_item.image = sprite

                fla.media[uvs_index] = bitmap_item

            else:
                matrix, _, _, _ = bitmap.get_matrix(shape_bitmaps_twips[shape_bitmaps_uvs.index(uv_coords)])

            uvs_index = shape_bitmaps_uvs.index(uv_coords)

            bitmap_instance = DOMBitmapInstance()
            bitmap_instance.library_item_name = f"resources/{uvs_index}"

            a, c, b, d, tx, ty = matrix.params
            bitmap_instance.matrix = Matrix(a, b, c, d, tx, ty)

            frame.elements.append(bitmap_instance)

        layer.frames.append(frame)
        graphic.timeline.layers.append(layer)

    fla.symbols[graphic.name] = graphic


def patch_shape_nine_slice(fla, shape):
    if shape.id in shapes_with_nine_slices:
        return shapes_with_nine_slices[shape.id]

    shape_slice = DOMGroup()

    shape_symbol = fla.symbols[f"shapes/shape_{shape.id}"]

    for l, layer in enumerate(shape_symbol.timeline.layers):
        for f, frame in enumerate(layer.frames):
            for e, element in enumerate(frame.elements):
                if isinstance(element, DOMBitmapInstance):
                    element_media = fla.media[int(element.library_item_name.split("/")[1])]
                    element_sprite = element_media.image
                    w, h = element_sprite.size

                    extrude_sprite = element_sprite.resize((w + 2, h + 2))
                    extrude_sprite.paste(element_sprite, (1, 1))
                    element_media.image = extrude_sprite

                    sprite_twip = [[0, 0], [w, 0], [w, h], [0, h]]

                    slice = DOMShape()
                    slice.is_drawing_object = True

                    edge_shape = ""
                    for x, curr in enumerate(sprite_twip):
                        nxt = sprite_twip[(x + 1) % len(sprite_twip)]
                        edge_shape += f"!{round(curr[0] * 20)} {round(curr[1] * 20)}|{round(nxt[0] * 20)} {round(nxt[1] * 20)}"

                    slice_style = FillStyle(1)
                    slice_bitmap_fill = BitmapFill(element.library_item_name)
                    slice_bitmap_fill.matrix = Matrix(20, 0, 0, 20, -1, -1)
                    slice_style.data = slice_bitmap_fill

                    slice_shape = Edge()
                    slice_shape.edges = edge_shape
                    slice_shape.fill_style1 = 1

                    slice.fills.append(slice_style)
                    slice.edges.append(slice_shape)
                    slice.matrix = element.matrix

                    shape_slice.members.append(slice)

                    shape_symbol.timeline.layers[l].frames[f].elements[e] = slice

    shapes_with_nine_slices[shape.id] = shape_slice
    return shape_slice


def convert_movieclip(fla, swf, movieclip: MovieClip, export_names: list = None):
    movie = DOMSymbolItem()

    layers_instance = []
    layers_order = []
    symbols_instance = []

    masked_layers = {}
    masked_layers_order = {}

    # Prepearing layers
    for i, bind in enumerate(movieclip.binds):
        bind_resource = swf.resources[bind['id']]
        if isinstance(bind_resource, MovieClipModifier):
            layers_instance.append(None)
            symbols_instance.append(bind_resource)
        else:
            # Layers
            bind_layer = DOMLayer(f"Layer_{i}")
            if bind["name"]:
                bind_layer.name = bind["name"]

            # Layer order
            layers_order.append(i)

            # Symbols instance
            if isinstance(bind_resource, Shape):
                if movieclip.nine_slice:
                    bind_instance = patch_shape_nine_slice(fla, bind_resource)

                else:
                    bind_instance = DOMSymbolInstance(library_item_name=f"shapes/shape_{bind['id']}")

            elif isinstance(bind_resource, MovieClip):
                bind_instance = DOMSymbolInstance(name=bind["name"],
                                                library_item_name=f"movieclips/movieclip_{bind['id']}"
                                                if bind['id'] not in swf.exports
                                                else f"exports/{swf.exports[bind['id']][-1]}")
                bind_instance.blend_mode = bind['blend']

            elif isinstance(bind_resource, TextField):
                bind_instance = DOMDynamicText(name=bind["name"])  # Спасибо, Солнышко :)

                # Subtracting4 because inside files it is lower by 4 than inside scene, idk why and how it works.
                bind_instance.width = bind_resource.right_corner - bind_resource.left_corner - 4
                bind_instance.height = bind_resource.bottom_corner - bind_resource.top_corner - 4

                if bind_resource.multiline:
                    bind_instance.line_type = "multiline no wrap"

                text_run = DOMTextRun()
                text_attrs = DOMTextAttrs()

                if bind_resource.text is not None:
                    text_run.characters = bind_resource.text

                text_attrs.face = bind_resource.font_name
                text_attrs.size = bind_resource.font_size
                text_attrs.bitmap_size = bind_resource.font_size * 20

                if bind_resource.bold or bind_resource.italic:
                    text_attrs.face += "-"

                if bind_resource.bold:
                    text_attrs.face += "Bold"

                if bind_resource.italic:
                    text_attrs.face += "Italic"

                text_attrs.fill_color = bind_resource.font_color & 0xFFFFFF00
                text_attrs.alpha = (bind_resource.font_color & 0x000000FF) / 255

                text_attrs.line_spacing = 0
                text_attrs.left_margin = bind_resource.font_align

                if bind_resource.outline_color:
                    glow_filter = GlowFilter()

                    glow_filter.blur_x = 2
                    glow_filter.blur_y = 2

                    glow_filter.color = bind_resource.outline_color & 0xFFFFFF00

                    glow_filter.strength = 15

                    if bind_resource.c1:
                        glow_filter.strength = bind_resource.c1 / 65535

                    bind_instance.filters.append(glow_filter)

                if bind_resource.c2:
                    drop_shadow_filter = DrowShadowFilter()

                    drop_shadow_filter.angle = (bind_resource.c2 / 65535) * 360

                    drop_shadow_filter.blur_x = 4
                    drop_shadow_filter.blur_y = 4

                    drop_shadow_filter.distance = 4

                    bind_instance.filters.append(drop_shadow_filter)

                text_run.text_attrs.append(text_attrs)

                bind_instance.text_runs.append(text_run)

            else:
                print("Unkwnown resource type")
                raise TypeError()

            symbols_instance.append(bind_instance)
            layers_instance.append(bind_layer)

    # Converting frames
    for i, frame in enumerate(movieclip.frames):
        elements = [element['bind'] for element in frame.elements]
        elements_idx = [element for element in elements if not isinstance(swf.resources[movieclip.binds[element]['id']], MovieClipModifier)]

        for element in elements_idx:
            for comparative in elements_idx:
                if comparative != element:
                    element_pos = elements_idx.index(element)
                    bind_pos = layers_order.index(element)

                    comparative_pos = elements_idx.index(comparative)
                    cmp_bind_pos = layers_order.index(comparative)

                    frame_position = element_pos > comparative_pos  # higher if True else lower
                    binds_position = bind_pos > cmp_bind_pos

                    if frame_position != binds_position:
                        layers_order.insert(layers_order.index(element), layers_order.pop(cmp_bind_pos))
        mask = False
        masked = False
        mask_layer = None
        for layer_idx, curr_layer in enumerate(layers_instance):
            if curr_layer is None:
                modifer = symbols_instance[layer_idx].modifier

                if modifer == modifer.Mask:
                    mask = True
                elif modifer == modifer.Masked:
                    mask = False
                    masked = True
                elif modifer == modifer.Unmasked:
                    masked = False
                    mask_layer = None

            else:
                if layer_idx in elements:
                    if mask:
                        curr_layer.layer_type = "mask"
                        curr_layer.is_locked = True
                        mask_layer = curr_layer
                    elif masked:
                        if mask_layer not in masked_layers:
                            masked_layers[mask_layer] = []
                            masked_layers_order[mask_layer] = []

                        if curr_layer not in masked_layers[mask_layer]:
                            masked_layers[mask_layer].append(curr_layer)
                            masked_layers_order[mask_layer].append(masked_layers[mask_layer].index(curr_layer))

                    element = frame.elements[elements.index(layer_idx)]

                    if curr_layer.frames and i:
                        if element in movieclip.frames[i-1].elements:
                            curr_layer.frames[-1].duration += 1
                            continue

                    layer_frame = DOMFrame(i)
                    instance = copy.deepcopy(symbols_instance[layer_idx])


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

                    layer_frame.elements.append(instance)
                    curr_layer.frames.append(layer_frame)

                else:
                    if curr_layer.frames and len(curr_layer.frames[-1].elements) == 0:
                        curr_layer.frames[-1].duration += 1
                    else:
                        curr_layer.frames.append(DOMFrame(i))

    layers_order = [o for o in layers_order if
                    layers_instance[o] not in [masked_layers[order_key][value] for order_key, order_list in
                                               masked_layers_order.items() for value in order_list]]

    for idx in reversed(layers_order):
        movie.timeline.layers.append(layers_instance[idx])

    for layer_key in masked_layers_order:
        for idx in masked_layers_order[layer_key]:
            mask_layer_index = movie.timeline.layers.index(layer_key)
            masked_layer = masked_layers[layer_key][idx]
            masked_layer.is_locked = True
            masked_layer.parent_layer_index = mask_layer_index
            movie.timeline.layers.insert(mask_layer_index + 1, masked_layer)

    if movieclip.nine_slice:
        x, y, width, height = movieclip.nine_slice

        movie.scale_grid_left = x
        movie.scale_grid_top = y
        movie.scale_grid_right = x + width
        movie.scale_grid_bottom = y + height

    if isinstance(export_names, list):
        for export in export_names:
            movie_instance = copy.deepcopy(movie)
            movie_instance.name = f"exports/{export}"
            movie_instance.timeline.name = export
            fla.symbols[movie_instance.name] = movie_instance
        return

    movie.name = f"movieclips/movieclip_{movieclip.id}"
    movie.timeline.name = f"movieclip_{movieclip.id}"
    fla.symbols[movie.name] = movie
