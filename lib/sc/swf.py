import copy
import os
from typing import List, Dict

from sc_compression import Decompressor, Compressor
from sc_compression.signatures import Signatures

from lib.console import Console
from lib.utils import BinaryReader, BinaryWriter
from .matrix_bank import MatrixBank
from .movie_clip import MovieClip, MovieClipModifier
from .movie_clip.movie_clip_modifier import save_movie_clip_modifiers_count
from .resource import Resource
from .savable import Savable
from .shape import Shape
from .text_field import TextField
from .texture import SWFTexture
from .texture.texture import save_texture
from ..utils.writer import write_block


class SupercellSWF:
    TEXTURE_EXTENSION = "_tex.sc"

    END_TAG = 0

    USE_LOWRES_TEXTURE_TAG = 23
    USE_EXTERNAL_TEXTURE_TAG = 26
    USE_UNCOMMON_RESOLUTION_TAG = 30
    TEXTURE_POSTFIXES_TAG = 32

    MOVIE_CLIP_MODIFIERS_COUNT_TAG = 37
    MOVIE_CLIP_MODIFIER_TAGS = (38, 39, 40)

    TEXTURE_TAGS = (1, 16, 19, 24, 27, 28, 29, 34)
    SHAPE_TAGS = (2, 18)
    MOVIE_CLIP_TAGS = (3, 10, 12, 14, 35)
    TEXT_FIELD_TAGS = (7, 15, 20, 21, 25, 33, 43, 44)

    MATRIX_TAGS = (8, 36)
    COLOR_TRANSFORM_TAG = 9
    MATRIX_BANK_TAG = 42

    def __init__(self) -> None:
        self.filename: str or None = None

        self.use_uncommon_texture: bool = False
        self.use_lowres_texture: bool = False

        self.textures_count: int = 0
        self.movie_clip_modifiers_count: int = 0
        self.shapes_count: int = 0
        self.text_fields_count: int = 0
        self.movieclips_count: int = 0

        self.has_external_texture: bool = False

        self.textures: List[SWFTexture] = []
        self.matrix_banks: List[MatrixBank] = [MatrixBank()]
        self.resources: Dict[int, Resource] = {}

        self.exports: dict = {}

        self.highres_texture_postfix: str = "_highres"
        self.lowres_texture_postfix: str = "_lowres"

        self.reader: BinaryReader or None = None
        self.writer: BinaryWriter or None = None

    def load(self, filepath: str):
        Console.info(f"Reading {filepath} SupercellFlash asset file...")
        print()

        self.filename = filepath

        self.load_internal(filepath, False)

        if self.has_external_texture:
            texture_filename = os.path.splitext(self.filename)[0] + self.TEXTURE_EXTENSION
            highres_path = f"{os.path.splitext(self.filename)[0]}{self.highres_texture_postfix}{self.TEXTURE_EXTENSION}"
            lowres_path = f"{os.path.splitext(self.filename)[0]}{self.lowres_texture_postfix}{self.TEXTURE_EXTENSION}"

            if self.use_uncommon_texture:
                if os.path.isfile(highres_path):
                    self.load_internal(highres_path, True)
                elif os.path.isfile(lowres_path):
                    Console.warning(f"Cannot find higrhes texture file {highres_path} for {self.filename}. Skipping...")
                    self.load_internal(lowres_path, True)
                else:
                    Console.error(
                        f"Cannot find any external texture file asset for {self.filename}! Textures not loaded! Aborting...")
                    raise TypeError()

            else:
                if self.use_lowres_texture:
                    if not os.path.exists(texture_filename) and os.path.exists(lowres_path):
                        Console.info(
                            f"Cannot find external texture file {texture_filename} for {self.filename}! Loading lowres texture asset...")
                        self.load_internal(lowres_path, True)

                if os.path.exists(texture_filename):
                    self.load_internal(texture_filename, True)
                else:
                    Console.error(
                        f"Cannot find external texture file {texture_filename} for {self.filename}! Textures not loaded! Aborting...")
                    raise TypeError()

    def load_internal(self, filepath: str, is_texture: bool):
        with open(filepath, 'rb') as file:
            compressed = file.read().split(b"START")[0]  # TODO: Vorono4ka, fix your sc-compression please...

            decompressor = Decompressor()
            self.reader = BinaryReader(decompressor.decompress(compressed))

        if not is_texture:
            Console.info("Reading main asset file...")

            self.shapes_count = self.reader.read_ushort()
            self.movieclips_count = self.reader.read_ushort()
            self.textures_count = self.reader.read_ushort()
            self.text_fields_count = self.reader.read_ushort()

            self.matrix_banks[-1].load(self)

            self.reader.skip(5)  # unused

            exports_count = self.reader.read_ushort()

            export_ids = [self.reader.read_ushort() for _ in range(exports_count)]
            self.exports = {id: [] for id in export_ids}

            for export_id in export_ids:
                export_name = self.reader.read_ascii()

                self.exports[export_id].append(export_name)

            print()

            self.textures = [_class() for _class in [SWFTexture] * self.textures_count]

        else:
            Console.info("Reading external texture asset file...")
            print()

        self.load_tags()

    def load_tags(self):
        has_external_texture = False

        textures_loaded = 0

        matrices_loaded = 0
        color_transforms_loaded = 0

        movieclip_modifiers_loaded = 0
        shapes_loaded = 0
        text_fields_loaded = 0
        movieclips_loaded = 0

        while True:
            tag = self.reader.read_uchar()
            tag_length = self.reader.read_int()

            if tag == SupercellSWF.END_TAG:
                print()
                Console.info("End tag.")
                print()
                Console.info("Reading completed.")

                break

            if tag == SupercellSWF.USE_LOWRES_TEXTURE_TAG:
                self.use_lowres_texture = True

                continue

            elif tag == SupercellSWF.USE_EXTERNAL_TEXTURE_TAG:
                has_external_texture = True
                self.has_external_texture = True
                continue

            elif tag == SupercellSWF.USE_UNCOMMON_RESOLUTION_TAG:
                self.use_uncommon_texture = True
                self.use_lowres_texture = True

                continue

            elif tag == SupercellSWF.TEXTURE_POSTFIXES_TAG:
                self.highres_texture_postfix = self.reader.read_ascii()
                self.lowres_texture_postfix = self.reader.read_ascii()
                continue

            elif tag in SupercellSWF.TEXTURE_TAGS:
                self.textures[textures_loaded].load(self, tag, has_external_texture)

                textures_loaded += 1
                if textures_loaded > self.textures_count:
                    Console.error("Trying to load too many SWFTextures! Aborting...")
                    raise TypeError()

                continue

            elif tag == SupercellSWF.MOVIE_CLIP_MODIFIERS_COUNT_TAG:
                self.movie_clip_modifiers_count = self.reader.read_ushort()
                continue

            elif tag in SupercellSWF.MOVIE_CLIP_MODIFIER_TAGS:
                movie_clip_modifier = MovieClipModifier()
                movie_clip_modifier.load(self, tag)

                self.resources[movie_clip_modifier.id] = movie_clip_modifier

                movieclip_modifiers_loaded += 1
                if movieclip_modifiers_loaded > self.movie_clip_modifiers_count:
                    Console.error("Trying to load too many MovieClipModifiers! Aborting...")
                    raise TypeError()

                continue

            elif tag in SupercellSWF.SHAPE_TAGS:
                Console.progress_bar("Shapes loading...", shapes_loaded, self.shapes_count)
                shape = Shape()
                shape.load(self, tag)

                self.resources[shape.id] = shape

                shapes_loaded += 1
                if shapes_loaded > self.shapes_count:
                    Console.error("Trying to load too many Shapes! Aborting...")
                    raise TypeError()

                continue

            elif tag in SupercellSWF.TEXT_FIELD_TAGS:
                Console.progress_bar("Text fields loading...", text_fields_loaded, self.text_fields_count)
                text_field = TextField()
                text_field.load(self, tag)

                self.resources[text_field.id] = text_field

                text_fields_loaded += 1
                if text_fields_loaded > self.text_fields_count:
                    Console.error("Trying to load too many TextFields! Aborting...")
                    raise TypeError()

                continue

            elif tag == SupercellSWF.MATRIX_BANK_TAG:
                matrix_bank = MatrixBank()
                matrix_bank.index = len(self.matrix_banks)
                matrix_bank.load(self)
                self.matrix_banks.append(matrix_bank)

                matrices_loaded = 0
                color_transforms_loaded = 0
                continue

            elif tag in SupercellSWF.MATRIX_TAGS:
                Console.progress_bar("Matrices loading...", matrices_loaded, self.matrix_banks[-1].matrices_count)

                self.matrix_banks[-1].matrices[matrices_loaded].load(self, tag)

                matrices_loaded += 1
                if matrices_loaded == self.matrix_banks[-1].matrices_count:
                    print()

                continue

            elif tag == SupercellSWF.COLOR_TRANSFORM_TAG:
                Console.progress_bar("ColorTransforms loading...", color_transforms_loaded,
                                     self.matrix_banks[-1].color_transforms_count)

                self.matrix_banks[-1].color_transforms[color_transforms_loaded].load(self, tag)

                color_transforms_loaded += 1
                if color_transforms_loaded == self.matrix_banks[-1].color_transforms_count:
                    print()

                continue

            elif tag in SupercellSWF.MOVIE_CLIP_TAGS:
                Console.progress_bar("Movieclip loading...", movieclips_loaded, self.movieclips_count)
                movieclip = MovieClip()
                movieclip.load(self, tag)

                self.resources[movieclip.id] = movieclip

                movieclips_loaded += 1
                if movieclips_loaded > self.movieclips_count:
                    Console.error("Trying to load too many MovieClips! Aborting...")
                    raise TypeError()

                continue

            Console.warning(f"{self.filename} has unknown tag {tag} with length {tag_length}! Skipped...")
            self.reader.skip(tag_length)

    def save(self, filepath: str):
        Console.info(f"Writing {filepath} SupercellFlash asset file...")
        print()

        self.filename = filepath

        self.save_internal(filepath, False, False)

        if self.has_external_texture:
            texture_filename = os.path.splitext(self.filename)[0] + self.TEXTURE_EXTENSION
            highres_path = f"{os.path.splitext(self.filename)[0]}{self.highres_texture_postfix}{self.TEXTURE_EXTENSION}"
            lowres_path = f"{os.path.splitext(self.filename)[0]}{self.lowres_texture_postfix}{self.TEXTURE_EXTENSION}"

            if self.use_uncommon_texture:
                self.save_internal(highres_path, True, False)

            else:
                self.save_internal(texture_filename, True, False)

            if self.use_lowres_texture:
                self.save_internal(lowres_path, True, True)

    def save_internal(self, filepath: str, is_texture: bool, is_lowres: bool):
        self.writer = BinaryWriter()

        sorted_resources_id = []
        sorted_resources = []
        id_list = {}

        if not is_texture:
            Console.info("Writing main asset file...")

            self.textures_count = len(self.textures)
            self.shapes_count = 0
            self.movieclips_count = 0
            self.text_fields_count = 0
            self.movie_clip_modifiers_count = 0

            for resource in self.resources.values():
                if isinstance(resource, Shape):
                    self.shapes_count += 1
                if isinstance(resource, MovieClip):
                    self.movieclips_count += 1
                if isinstance(resource, TextField):
                    self.text_fields_count += 1
                if isinstance(resource, MovieClipModifier):
                    self.movie_clip_modifiers_count += 1

            self.writer.write_ushort(self.shapes_count)
            self.writer.write_ushort(self.movieclips_count)
            self.writer.write_ushort(self.textures_count)
            self.writer.write_ushort(self.text_fields_count)

            if not self.matrix_banks:
                self.matrix_banks.append(MatrixBank())

            matrix_bank = self.matrix_banks[0]
            _, data = matrix_bank.save(self.writer)
            self.writer.write(data)

            self.writer.write(bytes(5))  # unused

            data_struct = [MovieClipModifier,
                           Shape,
                           TextField,
                           MatrixBank,
                           MovieClip]
            Console.info("Resource filtering...")

            resources = {}

            id_counter = 0
            for identifier, resource in self.resources.items():
                resource_values = list(resources.values())
                if resource in resource_values:  # TODO: change
                    id_list[identifier] = list(resources.items())[resource_values.index(resource)]
                else:
                    resources[identifier] = resource
                    id_list[identifier] = id_counter
                    id_counter += 1

            resources_keys = list(resources)
            resources_values = list(resources.values())

            sorted_resources_id = []
            sorted_resources: List[Resource or MatrixBank] = (
                resources_values +
                sorted(self.matrix_banks, key=lambda bank: bank.index)
            )
            sorted_resources.sort(key=lambda x: data_struct.index(type(x)))

            for resource in sorted_resources:
                if resource in resources_values:
                    sorted_resources_id.append(resources_keys[resources_values.index(resource)])
                else:
                    sorted_resources_id.append(None)

            export_ids = []
            export_names = []
            for export_id in self.exports:
                for export_name in self.exports[export_id]:
                    export_ids.append(id_list[export_id])
                    export_names.append(export_name)

            self.writer.write_ushort(len(export_ids))

            for export_id in export_ids:
                self.writer.write_ushort(export_id)

            for export_name in export_names:
                self.writer.write_ascii(export_name)

        else:
            Console.info("Writing external texture asset file...")
            print()

        self.save_tags((sorted_resources_id, sorted_resources), id_list, is_texture, is_lowres)
        print()

        with open(filepath, 'wb') as file:
            Console.info("File compressing...")
            compressor = Compressor()
            compressed = compressor.compress(self.writer.buffer, Signatures.SC, 1)
            Console.info("Writing to file..")
            file.write(compressed)

        Console.info("Writing completed.")

    def save_tags(self, resources, id_list, is_texture: bool, is_lowres: bool):
        written_shapes = 0
        written_movieclips = 0
        written_fields = 0

        if is_texture:
            for texture in self.textures:
                texture = copy.deepcopy(texture)
                if is_lowres:
                    Console.info("Writing lowres texture asset...")
                    sheet = texture.get_image()
                    w, h = sheet.size
                    texture.set_image(sheet.resize((int(w / 2), int(h / 2))))

                write_block(self.writer, texture.get_tag(), save_texture(texture, False))
            return

        if self.use_uncommon_texture:
            write_block(self.writer, SupercellSWF.USE_UNCOMMON_RESOLUTION_TAG, None)

        if self.has_external_texture:
            write_block(self.writer, SupercellSWF.USE_EXTERNAL_TEXTURE_TAG, None)

        if not self.use_uncommon_texture and self.use_lowres_texture:
            write_block(self.writer, SupercellSWF.USE_LOWRES_TEXTURE_TAG, None)

        for texture in self.textures:
            if self.has_external_texture:
                texture = copy.deepcopy(texture)
                texture.linear = False

            write_block(self.writer, texture.get_tag(), save_texture(texture, self.has_external_texture))

        if self.movie_clip_modifiers_count:
            write_block(
                self.writer,
                SupercellSWF.MOVIE_CLIP_MODIFIERS_COUNT_TAG,
                save_movie_clip_modifiers_count(self.movie_clip_modifiers_count)
            )

        ids, resources = resources
        ids: List[int]
        resources: List[Savable]
        for identifier, resource in zip(ids, resources):
            if isinstance(resource, MovieClipModifier):
                write_block(self.writer, resource.get_tag(), resource.save)

            elif isinstance(resource, Shape):
                Console.progress_bar("Shapes writing...", written_shapes, self.shapes_count)
                write_block(self.writer, resource.get_tag(), resource.save)
                written_shapes += 1
                if written_shapes == self.shapes_count:
                    print()

            elif isinstance(resource, TextField):
                Console.progress_bar("Text fields writing...", written_fields, self.text_fields_count)
                write_block(self.writer, resource.get_tag(), resource.save)
                written_fields += 1
                if written_fields == self.text_fields_count:
                    print()

            elif isinstance(resource, MatrixBank):
                written_transforms = 0
                if resource.index > 0:
                    write_block(self.writer, resource.get_tag(), resource.save)

                for matrix in resource.matrices:
                    Console.progress_bar(f"Matrices bank {resource.index} writing...", written_transforms,
                                         len(resource.matrices))

                    write_block(self.writer, matrix.get_tag(), matrix.save)

                    written_transforms += 1
                print()
                written_transforms = 0
                for color_transform in resource.color_transforms:
                    Console.progress_bar(f"Colors bank {resource.index} writing...", written_transforms,
                                         len(resource.color_transforms))
                    write_block(self.writer, color_transform.get_tag(), color_transform.save)

                    written_transforms += 1
                print()

            elif isinstance(resource, MovieClip):
                Console.progress_bar("Movieclips writing...", written_movieclips, self.movieclips_count)
                resource.set_id_list(id_list)
                write_block(self.writer, resource.get_tag(), resource.save)
                written_movieclips += 1
                if written_movieclips == self.movieclips_count:
                    print()

        self.writer.write(bytes(5))  # end tag
