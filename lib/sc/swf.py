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

        self.exports_count: int = 0
        self.exports: dict = {}

        self.highres_texture_postfix: str = "_highres"
        self.lowres_texture_postfix: str = "_lowres"

        self.reader: BinaryReader = None
        self.writer: BinaryWriter = None
    
    def add_resource(self, resource: Resource):
        self.resources[resource.id] = resource
    
    def init_matrix_bank(self, matrices_count: int, color_transforms_count: int):
        Console.info(f"MatrixBank: {matrices_count} matrices and {color_transforms_count} color transforms")
        self.matrix_banks.append(MatrixBank(matrices_count, color_transforms_count))
    
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

            matrices_count = self.reader.read_ushort()
            color_transforms_count = self.reader.read_ushort()

            self.reader.skip(5)  # unused

            self.exports_count = self.reader.read_ushort()

            export_ids = [self.reader.read_ushort() for x in range(self.exports_count)]
            for export_id in export_ids:
                export_name = self.reader.read_ascii()

                self.exports[export_id] = export_name

                Console.info(f"Export {export_name} with id {export_id}")
            
            print()
            
            self.textures = [_class() for _class in [SWFTexture] * self.textures_count]
            
            self.init_matrix_bank(matrices_count, color_transforms_count)
        
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
                break

            if tag == SupercellSWF.USE_LOWRES_TEXTURE_TAG:
                Console.info("Use low resolution texture tag.")

                lowres_texture_filename = os.path.splitext(self.filename)[0] + self.lowres_texture_postfix + SupercellSWF.TEXTURE_EXTENSION

                if not os.path.exists(lowres_texture_filename):
                    Console.warning(f"Cannot find low resolution texture for {self.filename}! Skipping...")
                
                else:
                    self.use_uncommon_texture = True

                    self.uncommon_texture_filename = lowres_texture_filename
                    self.use_lowres_texture = True
                
                continue

            elif tag == SupercellSWF.USE_EXTERNAL_TEXTURE_TAG:
                Console.info("Use external texture file tag.")
                has_external_texture = True
                continue

            elif tag == SupercellSWF.USE_UNCOMMON_RESOLUTION_TAG:
                Console.info("Use uncommon resolution texture tag.")

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
                continue

            elif tag == SupercellSWF.MOVIECLIP_MODIFIERS_COUNT_TAG:
                self.movieclip_modifiers_count = self.reader.read_ushort()
                continue

            elif tag in SupercellSWF.MOVIECLIP_MODIFIER_TAGS:
                movieclip_modifier = MovieClipModifier()
                movieclip_modifier.load(self, tag)

                Console.info(f"MovieClipModifier: {movieclip_modifier.id} - {movieclip_modifier.modifier.name}")

                self.add_resource(movieclip_modifier)

                movieclip_modifiers_loaded += 1
                continue

            elif tag in SupercellSWF.SHAPE_TAGS:
                shape = Shape()
                shape.load(self, tag)

                Console.info(f"Shape: {shape.id} - {len(shape.bitmaps)} bitmaps")

                self.add_resource(shape)

                shapes_loaded += 1
                continue

            elif tag in SupercellSWF.TEXT_FIELD_TAGS:
                text_field = TextField()
                text_field.load(self, tag)

                Console.info(f"TextField: {text_field.id} - {text_field.font_name}")

                self.add_resource(text_field)

                text_fields_loaded += 1
                continue

            elif tag == SupercellSWF.MATRIX_BANK_TAG:
                matrices_count = self.reader.read_ushort()
                color_transforms_count = self.reader.read_ushort()

                self.init_matrix_bank(matrices_count, color_transforms_count)

                matrices_loaded = 0
                color_transforms_loaded = 0
                continue

            elif tag in SupercellSWF.MATRIX_TAGS:
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
                continue

            elif tag == SupercellSWF.COLOR_TRANSFORM_TAG:
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
                continue

            elif tag in SupercellSWF.MOVIECLIP_TAGS:
                movieclip = MovieClip()
                movieclip.load(self, tag)

                Console.info(f"MovieClip: {movieclip.id} - {movieclip.frame_rate} FPS and {len(movieclip.frames)} frames")

                self.add_resource(movieclip)

                movieclips_loaded += 1
                continue

            Console.warning(f"{self.filename} has unknown tag {tag} with length {tag_length}! Skipped...")
            self.reader.skip(tag_length)

        return has_external_texture
