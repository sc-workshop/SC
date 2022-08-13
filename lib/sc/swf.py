import os

from lib.utils import BinaryReader, BinaryWriter

from .resource import Resource

from .texture import SWFTexture
from .shape import Shape
from .text_field import TextField
from .matrix_bank import MatrixBank
from .movieclip import MovieClipModifier, MovieClip

from sc_compression.signatures import Signatures
from sc_compression import Decompressor, Compressor

from lib.console import Console



class SupercellSWF:

    TEXTURE_EXTENSION = "_tex.sc"

    END_TAG = 0

    USE_LOWRES_TEXTURE_TAG = 23
    USE_EXTERNAL_TEXTURE_TAG = 26
    USE_UNCOMMON_RESOLUTION_TAG = 30
    TEXTURE_POSTFIXS_TAG = 32

    MOVIECLIP_MODIFIERS_COUNT_TAG = 37
    MOVIECLIP_MODIFIER_TAGS = (38, 39, 40)

    TEXTURE_TAGS = (1, 16, 19, 24, 27, 28, 29, 34)

    SHAPE_TAGS = (2, 18)

    TEXT_FIELD_TAGS = (7, 15, 20, 21, 25, 33, 43, 44)

    MATRIX_BANK_TAG = 42
    MATRIX_TAGS = (8, 36)
    COLOR_TRANSFORM_TAG = 9

    MOVIECLIP_TAGS = (3, 10, 12, 14, 35)

    def __init__(self) -> None:
        self.filename: str = None

        self.use_uncommon_texture: bool = False
        self.use_lowres_texture: bool = False

        self.uncommon_texture_filename: str = None

        self.textures_count: int = 0
        self.movieclip_modifiers_count: int = 0
        self.shapes_count: int = 0
        self.text_fields_count: int = 0
        self.movieclips_count: int = 0

        self.textures: list = []
        self.matrix_banks: list = []
        self.resources: dict = {}

        self.exports: dict = {}

        self.highres_texture_postfix: str = "_highres"
        self.lowres_texture_postfix: str = "_lowres"

        self.reader: BinaryReader = None
        self.writer: BinaryWriter = None
    
    def add_resource(self, resource: Resource):
        self.resources[resource.id] = resource
    
    def load(self, filepath: str):
        Console.info(f"Reading {filepath} SupercellFlash asset file...")
        print()

        self.filename = filepath

        has_external_texture = self.load_internal(filepath, False)

        if has_external_texture:

            if self.use_uncommon_texture:
                self.load_internal(self.uncommon_texture_filename, True)
            
            else:
                texture_filename = os.path.splitext(self.filename)[0] + SupercellSWF.TEXTURE_EXTENSION

                if not os.path.exists(texture_filename):
                    Console.error(f"Cannot find external texture file {texture_filename} for {self.filename}! Textures not loaded! Aborting...")
                    raise TypeError()
                
                self.load_internal(texture_filename, True)

    def load_internal(self, filepath: str, is_texture: bool):
        with open(filepath, 'rb') as file:
            compressed = file.read().split(b"START")[0] # TODO: Vorono4ka, fix your sc-compression please...

            decompressor = Decompressor()
            self.reader = BinaryReader(decompressor.decompress(compressed))

        if not is_texture:
            Console.info("Reading main asset file...")
            print()

            self.shapes_count = self.reader.read_ushort()
            self.movieclips_count = self.reader.read_ushort()
            self.textures_count = self.reader.read_ushort()
            self.text_fields_count = self.reader.read_ushort()

            matrix_bank = MatrixBank()
            matrix_bank.load(self)
            self.matrix_banks.append(matrix_bank)

            self.reader.skip(5)  # unused

            exports_count = self.reader.read_ushort()

            export_ids = [self.reader.read_ushort() for x in range(exports_count)]
            self.exports = {id: [] for id in export_ids}
            
            for export_id in export_ids:
                export_name = self.reader.read_ascii()

                self.exports[export_id].append(export_name)

                Console.info(f"Export {export_name} with id {export_id}")
            
            print()
            
            self.textures = [_class() for _class in [SWFTexture] * self.textures_count]
        
        else:
            Console.info("Reading external texture asset file...")
            print()

        return self.load_tags()

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
                Console.info("End tag.")
                print()
                Console.info("Reading completed.")

                break

            if tag == SupercellSWF.USE_LOWRES_TEXTURE_TAG:
                Console.info("Use low resolution texture tag")

                lowres_texture_filename = os.path.splitext(self.filename)[0] + self.lowres_texture_postfix + SupercellSWF.TEXTURE_EXTENSION

                if not os.path.exists(lowres_texture_filename):
                    Console.warning(f"Cannot find low resolution texture for {self.filename}! Skipping...")
                
                else:
                    self.use_uncommon_texture = True

                    self.uncommon_texture_filename = lowres_texture_filename
                    self.use_lowres_texture = True
                
                continue

            elif tag == SupercellSWF.USE_EXTERNAL_TEXTURE_TAG:
                Console.info("Use external texture file tag")
                has_external_texture = True
                continue

            elif tag == SupercellSWF.USE_UNCOMMON_RESOLUTION_TAG:
                Console.info("Use uncommon resolution texture tag")

                highres_texture_filename = os.path.splitext(self.filename)[0] + self.highres_texture_postfix + SupercellSWF.TEXTURE_EXTENSION
                lowres_texture_filename = os.path.splitext(self.filename)[0] + self.lowres_texture_postfix + SupercellSWF.TEXTURE_EXTENSION
                
                if not os.path.exists(highres_texture_filename):
                    Console.warning(f"Cannot find high resolution texture for {self.filename}! Trying to find low resoulution...")

                    if not os.path.exists(lowres_texture_filename):
                        Console.warning(f"Cannot find low resolution texture for {self.filename}! Skipping...")
                    else:
                        self.use_uncommon_texture = True

                        self.uncommon_texture_filename = lowres_texture_filename
                        self.use_lowres_texture = True
                else:
                    self.use_uncommon_texture = True
                    self.uncommon_texture_filename = highres_texture_filename
                
                continue

            elif tag == SupercellSWF.TEXTURE_POSTFIXS_TAG:
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

            elif tag == SupercellSWF.MOVIECLIP_MODIFIERS_COUNT_TAG:
                self.movieclip_modifiers_count = self.reader.read_ushort()
                continue

            elif tag in SupercellSWF.MOVIECLIP_MODIFIER_TAGS:
                movieclip_modifier = MovieClipModifier()
                movieclip_modifier.load(self, tag)

                self.add_resource(movieclip_modifier)

                movieclip_modifiers_loaded += 1
                if movieclip_modifiers_loaded > self.movieclip_modifiers_count:
                    Console.error("Trying to load too many MovieClipModifiers! Aborting...")
                    raise TypeError()
                
                continue

            elif tag in SupercellSWF.SHAPE_TAGS:
                shape = Shape()
                shape.load(self, tag)

                self.add_resource(shape)

                shapes_loaded += 1
                if shapes_loaded > self.shapes_count:
                    Console.error("Trying to load too many Shapes! Aborting...")
                    raise TypeError()

                continue

            elif tag in SupercellSWF.TEXT_FIELD_TAGS:
                text_field = TextField()
                text_field.load(self, tag)

                self.add_resource(text_field)

                text_fields_loaded += 1
                if text_fields_loaded > self.text_fields_count:
                    Console.error("Trying to load too many TextFields! Aborting...")
                    raise TypeError()
                
                continue

            elif tag == SupercellSWF.MATRIX_BANK_TAG:
                matrix_bank = MatrixBank()
                matrix_bank.load(self)
                self.matrix_banks.append(matrix_bank)

                matrices_loaded = 0
                color_transforms_loaded = 0
                continue

            elif tag in SupercellSWF.MATRIX_TAGS:
                Console.progress_bar("Matrices loading...", matrices_loaded, self.matrix_banks[-1].matrices_count)

                matrix = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

                divider = 1024 if tag == 8 else 65535

                matrix[0] = self.reader.read_int() / divider  # scale x
                matrix[1] = self.reader.read_int() / divider  # rotation x
                matrix[2] = self.reader.read_int() / divider  # rotation y
                matrix[3] = self.reader.read_int() / divider  # scale y

                matrix[4] = self.reader.read_twip()  # tx
                matrix[5] = self.reader.read_twip()  # ty

                self.matrix_banks[-1].matrices[matrices_loaded] = matrix

                matrices_loaded += 1
                if matrices_loaded == self.matrix_banks[-1].matrices_count:
                    print()
                
                continue

            elif tag == SupercellSWF.COLOR_TRANSFORM_TAG:
                Console.progress_bar("ColorTransforms loading...", color_transforms_loaded, self.matrix_banks[-1].color_transforms_count)

                color = [0, 0, 0, 0, 1.0, 1.0, 1.0, 1.0]

                color[0] = self.reader.read_uchar()  # red addition
                color[1] = self.reader.read_uchar()  # green addition
                color[2] = self.reader.read_uchar()  # blue addition

                color[7] = self.reader.read_uchar() / 255  # alpha multiplier
                color[4] = self.reader.read_uchar() / 255  # red multiplier
                color[5] = self.reader.read_uchar() / 255  # green multiplier
                color[6] = self.reader.read_uchar() / 255  # blue multiplier

                self.matrix_banks[-1].color_transforms[color_transforms_loaded] = color

                color_transforms_loaded += 1
                if color_transforms_loaded == self.matrix_banks[-1].color_transforms_count:
                    print()
                
                continue

            elif tag in SupercellSWF.MOVIECLIP_TAGS:
                movieclip = MovieClip()
                movieclip.load(self, tag)

                self.add_resource(movieclip)

                movieclips_loaded += 1
                if movieclips_loaded > self.movieclips_count:
                    Console.error("Trying to load too many MovieClips! Aborting...")
                    raise TypeError()
                
                continue

            Console.warning(f"{self.filename} has unknown tag {tag} with length {tag_length}! Skipped...")
            self.reader.skip(tag_length)

        return has_external_texture
    
    def save(self, filepath: str, use_external_texture: bool):
        self.filename = filepath

        self.save_internal(filepath, use_external_texture, False)

        if use_external_texture:
            if self.use_uncommon_texture:
                self.save_internal(self.uncommon_texture_filename, False, True)

            else:
                texture_filename = os.path.splitext(self.filename)[0] + SupercellSWF.TEXTURE_EXTENSION
                self.save_internal(texture_filename, False, True)

    def save_internal(self, filepath: str, use_external_texture: bool, is_texture: bool):
        self.writer = BinaryWriter()

        if not is_texture:
            # TODO: Fix SC header!!!
            self.writer.write_ushort(0)
            self.writer.write_ushort(0)
            self.writer.write_ushort(len(self.textures))
            self.writer.write_ushort(0)

            if not self.matrix_banks:
                self.matrix_banks.append(MatrixBank())
            
            matrix_bank = self.matrix_banks[0]
            _, data = matrix_bank.save()
            self.writer.write(data)

            self.writer.write(bytes(5)) # unused

            export_ids = []
            export_names = []
            for export_id in self.exports:
                for export_name in self.exports[export_id]:
                    export_ids.append(export_id)
                    export_names.append(export_name)
            
            self.writer.write_ushort(len(export_ids))
            
            for export_id in export_ids:
                self.writer.write_ushort(export_id)
            
            for export_name in export_names:
                self.writer.write_ascii(export_name)

        self.save_tags(use_external_texture, is_texture)

        with open(filepath, 'wb') as file:
            compressor = Compressor()
            file.write(compressor.compress(self.writer.buffer, Signatures.SC, 1))

    def save_tags(self, use_external_texture: bool, is_texture: bool):
        def save_tag(tag, data):
            self.writer.write_uchar(tag)
            self.writer.write_int(len(data))
            self.writer.write(data)

        if is_texture:
            for texture in self.textures:
                tag, data = texture.load(use_external_texture)
                save_tag(tag, data)
            
            return
        
        if self.use_lowres_texture:
            save_tag(SupercellSWF.USE_LOWRES_TEXTURE_TAG, bytes())

        if use_external_texture:
            save_tag(SupercellSWF.USE_EXTERNAL_TEXTURE_TAG, bytes())

        if self.use_uncommon_texture:
            save_tag(SupercellSWF.USE_UNCOMMON_RESOLUTION_TAG, bytes())
        
        for texture in self.textures:
            tag, data = texture.load(use_external_texture)
            save_tag(tag, data)
        
        movieclip_modifiers = []
        shapes = []
        text_fields = []
        movieclips = []

        for id in self.resources:
            resource = self.resources[id]

            if isinstance(resource, MovieClipModifier):
                movieclip_modifiers.append(resource)
            
            elif isinstance(resource, Shape):
                shapes.append(resource)
            
            elif isinstance(resource, TextField):
                text_fields.append(resource)
            
            elif isinstance(resource, MovieClip):
                movieclips.append(resource)
        
        for movieclip_modifier in movieclip_modifiers:
            tag, data = movieclip_modifier.save()
            save_tag(tag, data)
        
        for shape in shapes:
            tag, data = shape.save(self)
            save_tag(tag, data)
        
        for text_field in text_fields:
            tag, data = text_field.save()
            save_tag(tag, data)
        
        for i, matrix_bank in enumerate(self.matrix_banks):
            if i > 0:
                tag, data = matrix_bank.save()
                save_tag(tag, data)

            for matrix in matrix_bank.matrices:
                a, b, c, d, tx, ty = matrix

                self.writer.write_uchar(8)
                self.writer.write_int(24)

                self.writer.write_int(int(round(a * 1024)))
                self.writer.write_int(int(round(b * 1024)))
                self.writer.write_int(int(round(c * 1024)))
                self.writer.write_int(int(round(d * 1024)))

                self.writer.write_twip(tx)
                self.writer.write_twip(ty)

            for color_transform in matrix_bank.color_transforms:
                r_add, g_add, b_add, _, r_mul, g_mul, b_mul, a_mul = color_transform
                
                self.writer.write_uchar(9)
                self.writer.write_int(7)
                
                self.writer.write_uchar(r_add)
                self.writer.write_uchar(g_add)
                self.writer.write_uchar(b_add)

                self.writer.write_uchar(r_mul)
                self.writer.write_uchar(g_mul)
                self.writer.write_uchar(b_mul)
                self.writer.write_uchar(a_mul)
        
        for movieclip in movieclips:
            tag, data = movieclip.save()
            save_tag(tag, data)
        
        self.writer.write(bytes(5)) # end tag
