from lib.sc import *
import os
from shutil import rmtree
from PIL import Image
from lib.console import Console
import ujson

shape_bitmaps_uvs = []
shape_bitmaps_twips = []

def convert_shape(swf, id, shape: Shape, sprite_folder):
    shape_base = {"Name": id,
                  "Bitmaps": []}

    bitmap_library = shape_base["Bitmaps"]

    for bitmap in shape.bitmaps:
        bitmap_base = {}
        uv_coords = bitmap.uv_coords
        xy_coords = bitmap.xy_coords

        if uv_coords.count(uv_coords[0]) == len(uv_coords):
            texture = swf.textures[bitmap.texture_index]

            x, y = uv_coords[0]
            pixel = texture.image.getpixel((int(x), int(y)))

            bitmap_base["Color"] = pixel
            bitmap_base["Shape"] = xy_coords

        else:
            if uv_coords not in shape_bitmaps_uvs:
                shape_bitmaps_uvs.append(uv_coords)

                uvs_index = shape_bitmaps_uvs.index(uv_coords)

                matrix, twips, rotation, mirror = bitmap.get_matrix(use_nearest=True)
                shape_bitmaps_twips.append(twips)

                sprite = bitmap.get_image(swf)
                sprite = sprite.rotate(-rotation, expand = True)
                if mirror:
                    sprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
                sprite_path =f"{sprite_folder}/{uvs_index}.png"
                sprite.save(sprite_path)

                bitmap_base["Uri"] = os.path.abspath(sprite_path)
            else:
                uvs_index = shape_bitmaps_uvs.index(uv_coords)
                bitmap_base["Uri"] = os.path.abspath(f"{sprite_folder}/{uvs_index}.png")
                matrix, _, _, _ = bitmap.get_matrix(shape_bitmaps_twips[uvs_index])

            bitmap_base["Transforms"] = {}
            bitmap_matrix = bitmap_base["Transforms"]
            bitmap_matrix["Rot x"] = round(matrix.get_rotation_x(), 4)
            bitmap_matrix["Rot y"] = round(matrix.get_rotation_y(), 4)
            bitmap_matrix["Scale x"] = round(matrix.get_scale_x(), 4)
            bitmap_matrix["Scale y"] = round(matrix.get_scale_y(), 4)
            tx, ty = matrix.get_translation()
            bitmap_matrix["Pos x"] = round(tx)
            bitmap_matrix["Pos y"] = round(ty)

        bitmap_library.append(bitmap_base)

    return shape_base

def convert_field(id, field: TextField):
    field_base = {"Name": id,
                  "Font name": field.font_name,
                  "Outline color": field.font_color,
                  "Font size": field.font_size,
                  "Font align": field.font_align,
                  "Bold": field.bold,
                  "Italic": field.italic,
                  "Multiline": field.multiline,
                  "Outline": field.outline,
                  "Left corner": field.left_corner,
                  "Top corner": field.top_corner,
                  "Right corner": field.right_corner,
                  "Bottom corner": field.bottom_corner,
                  "Text": field.text,
                  "Flag1": field.flag1,
                  "Flag2": field.flag2,
                  "Flag3": field.flag3,
                  "C1": field.c1,
                  "C2": field.c2}

    return field_base

def convert_movie(swf: SupercellSWF, id, movie: MovieClip):
    movie_base = {"Name": id}

    if id in swf.exports:
        movie_base["Framerate"] = movie.frame_rate
        movie_base["Exports"] = swf.exports[id]

    if movie.nine_slice:
        movie_base["Nine slice"] = movie.nine_slice

    movie_base["Binds"] = movie.binds

    movie_base["Frames"] = [{"Name": frame.name,
                             "Elements": []}
                            for frame in movie.frames]
    frames = movie_base["Frames"]

    for i, frame in enumerate(movie.frames):
        for element in frame.elements:
            frame_element = {"BindIndex": element["bind"]}
            if element["matrix"] != 0xFFFF:
                frame_element["Matrix"] = swf.matrix_banks[movie.matrix_bank].matrices[element["matrix"]]
            if element["color"] != 0xFFFF:
                frame_element["Color"] = swf.matrix_banks[movie.matrix_bank].color_transforms[element["color"]]
            frames[i]["Elements"].append(frame_element)

    return movie_base

def sc_to_json(filepath):
    swf = SupercellSWF()
    swf.load(filepath)
    filename = os.path.splitext(filepath)[0]

    json_base = {"Shapes": [],
                    "Textfields": [],
                    "Modifiers": [],
                    "Movieclips": []}

    shape_library = json_base["Shapes"]
    field_library = json_base["Textfields"]
    modifier_library = json_base["Modifiers"]
    movie_library = json_base["Movieclips"]

    sprite_folder = filename + "_sprites"
    if os.path.exists(sprite_folder):
        rmtree(sprite_folder)
    os.mkdir(sprite_folder)
    for i, (id, resource) in enumerate(swf.resources.items()):
        if isinstance(resource, Shape):
            shape_library.append(convert_shape(swf, id, resource, sprite_folder))
        elif isinstance(resource, TextField):
            field_library.append(convert_field(id, resource))
        elif isinstance(resource, MovieClipModifier):
            modifier_library.append({"Id": id, "Modifier": resource.modifier.name})
        elif isinstance(resource, MovieClip):
            movie_library.append(convert_movie(swf, id, resource))

        Console.progress_bar("Converting to json...", i, len(swf.resources))
    print()

    with open(filename + ".json", "w") as f:
        Console.info("Saving...")
        f.write(ujson.dumps(json_base, indent=2))
    Console.info("Convert completed.")


