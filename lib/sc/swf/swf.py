import os

from lib.utils import BinaryReader, BinaryWriter

from .texture import SWFTexture
from .shape import Shape
from .text_field import TextField
from .matrix_bank import MatrixBank
from .movieclip import MovieClipModifier, MovieClip

from sc_compression import Decompressor, Compressor
from sc_compression.signatures import Signatures


class SupercellSWF:
    def __init__(self) -> None:
        self.filename: str = None

        self.exports: dict = {}

        self.has_external_texture = False
        self.has_highres_texture = False
        self.has_lowres_texture = True

        self.shapes_count: int = 0
        self.movieclips_count: int = 0
        self.textures_count: int = 0
        self.text_fields_count: int = 0
        self.matrices_count: int = 0
        self.color_transforms_count: int = 0
        self.movieclip_modifiers_count: int = 0

        self.textures: list = []
        self.movieclip_modifiers: list = []
        self.shapes: list = []
        self.text_fields: list = []
        self.matrix_banks: list = []
        self.movieclips: list = []

        self.movieclip_modifiers_ids: list = []
        self.shapes_ids: list = []
        self.text_fields_ids: list = []
        self.movieclips_ids: list = []

        self.texture_asset_postfix: str = "_tex.sc"
        self.highres_asset_postfix: str = "_highres_tex.sc"
        self.lowres_asset_postfix: str = "_lowres_tex.sc"

        self.reader: BinaryReader = None
        self.writer: BinaryWriter = None
    
    def load_internal(self, filepath: str, is_texture: bool):
        with open(filepath, 'rb') as file:
            decompressor = Decompressor()
            self.reader = BinaryReader(decompressor.decompress(file.read()))
        
        if not is_texture:
            self.shapes_count = self.reader.read_ushort()
            self.movieclips_count = self.reader.read_ushort()
            self.textures_count = self.reader.read_ushort()
            self.text_fields_count = self.reader.read_ushort()
            self.matrices_count = self.reader.read_ushort()
            self.color_transforms_count = self.reader.read_ushort()

            self.reader.skip(5) # unused

            exports_count = self.reader.read_ushort()

            self.exports = [_function() for _function in [self.reader.read_ushort] * exports_count]
            self.exports = {export_id: self.reader.read_ascii() for export_id in self.exports}
            
            self.shapes = [_class() for _class in [Shape] * self.shapes_count]
            self.movieclips = [_class() for _class in [MovieClip] * self.movieclips_count]
            self.textures = [_class() for _class in [SWFTexture] * self.textures_count]
            self.text_fields = [_class() for _class in [TextField] * self.text_fields_count]
            
            matrix_bank = MatrixBank()
            matrix_bank.matrices = [[1, 0, 0, 1, 0, 0]] * self.matrices_count
            matrix_bank.color_transforms = [[0, 0, 0, 0, 1, 1, 1, 1]] * self.color_transforms_count
            self.matrix_banks.append(matrix_bank)
        
        return self.load_tags()
    
    def load_tags(self):
        has_textures = False

        shapes_loaded = 0
        movieclips_loaded = 0
        textures_loaded = 0
        text_fields_loaded = 0
        matrices_loaded = 0
        color_transforms_loaded = 0
        movieclip_modifiers_loaded = 0

        matrix_bank_offset = 0

        while True:
            tag = self.reader.read_uchar()
            tag_length = self.reader.read_int()

            if tag == 0:
                break

            if tag == 23:
                self.has_lowres_texture = False

            elif tag == 26:
                has_textures = True
                self.has_external_texture = True

            elif tag == 30:
                self.has_highres_texture = True

            elif tag == 32:
                self.highres_asset_postfix = self.reader.read_ascii()
                self.lowres_asset_postfix = self.reader.read_ascii()
                continue

            elif tag in [1, 16, 19, 24, 27, 28, 29, 34]:
                self.textures[textures_loaded].load(self, tag, has_textures)
                textures_loaded += 1
                continue

            elif tag == 37:
                self.movieclip_modifiers_count = self.reader.read_ushort()
                self.movieclip_modifiers = [_class() for _class in [MovieClipModifier] * self.movieclip_modifiers_count]
                continue

            elif tag in [38, 39, 40]:
                self.movieclip_modifiers[movieclip_modifiers_loaded].load(self, tag)
                movieclip_modifiers_loaded += 1
                continue

            elif tag in [2, 18]:
                self.shapes[shapes_loaded].load(self, tag)
                shapes_loaded += 1
                continue

            elif tag in [7, 15, 20, 21, 25, 33, 43, 44]:
                self.text_fields[text_fields_loaded].load(self, tag)
                text_fields_loaded += 1
                continue

            elif tag == 42:
                self.matrices_count = self.reader.read_ushort()
                self.color_transforms_count = self.reader.read_ushort()

                matrix_bank = MatrixBank()
                matrix_bank.matrices = [[1, 0, 0, 1, 0, 0]] * self.matrices_count
                matrix_bank.color_transforms = [[0, 0, 0, 0, 1, 1, 1, 1]] * self.color_transforms_count

                matrices_loaded = 0
                color_transforms_loaded = 0

                self.matrix_banks.append(matrix_bank)
                matrix_bank_offset += 1
                continue

            elif tag in [8, 36]:
                matrix = [1, 0, 0, 1, 0, 0]

                multiplier = 0.0009765625 if tag == 8 else 0.000015259

                matrix[0] = self.reader.read_int() * multiplier # scale x
                matrix[1] = self.reader.read_int() * multiplier # rotation x
                matrix[2] = self.reader.read_int() * multiplier # rotation y
                matrix[3] = self.reader.read_int() * multiplier # scale y

                matrix[4] = self.reader.read_twip() # tx
                matrix[5] = self.reader.read_twip() # ty

                self.matrix_banks[matrix_bank_offset].matrices[matrices_loaded] = matrix
                matrices_loaded += 1
                continue

            elif tag == 9:
                color = [0, 0, 0, 0, 1, 1, 1, 1]

                color[0] = self.reader.read_uchar()  # red addition
                color[1] = self.reader.read_uchar() # green addition
                color[2] = self.reader.read_uchar() # blue addition

                color[7] = self.reader.read_uchar() / 255  # alpha multiplier
                color[4] = self.reader.read_uchar() / 255  # red multiplier
                color[5] = self.reader.read_uchar() / 255  # green multiplier
                color[6] = self.reader.read_uchar() / 255  # blue multiplier

                self.matrix_banks[matrix_bank_offset].color_transforms[color_transforms_loaded] = color
                color_transforms_loaded += 1
                continue

            elif tag in [3, 10, 12, 14, 35]:
                self.movieclips[movieclips_loaded].load(self, tag)
                movieclips_loaded += 1
                continue

            self.reader.skip(tag_length)


    def load(self, filepath: str, load_textures: bool = True):
        self.filename = filepath
        
        self.load_internal(filepath, False)

        if load_textures:
            if self.has_external_texture:
                if self.has_highres_texture:
                    self.load_internal(os.path.splitext(filepath)[0] + self.highres_asset_postfix, True)
                else:
                    self.load_internal(os.path.splitext(filepath)[0] + self.texture_asset_postfix, True)

    
    def save_tag(self, tag, buffer):
        self.writer.write_uchar(tag)
        self.writer.write_int(len(buffer))
        self.writer.write(buffer)
    
    def save_texture(self):
        for texture in self.textures:
            tag, buffer = texture.save(False)

            self.save_tag(tag, buffer)
        
        self.writer.write(bytes(5))
    
    def save_tags(self, enable_postfix: bool = False):
        if enable_postfix:
            postfix_tag = BinaryWriter()

            postfix_tag.write_ascii(self.highres_asset_postfix)
            postfix_tag.write_ascii(self.lowres_asset_postfix)

            self.save_tag(32, postfix_tag.buffer)
        
        if not self.has_lowres_texture:
            self.save_tag(23, bytes())

        if self.has_highres_texture:
            self.save_tag(30, bytes())

        if self.has_external_texture:
            self.save_tag(26, bytes())
        
        for texture in self.textures:
            tag, buffer = texture.save(self.has_external_texture)
            
            self.save_tag(tag, buffer)
        
        if self.movieclip_modifiers:
            self.save_tag(37, len(self.movieclip_modifiers).to_bytes(2, "little"))
        
        for movieclip_modifier in self.movieclip_modifiers:
            tag, buffer = movieclip_modifier.save()

            self.save_tag(tag, buffer)

        for shape in self.shapes:
            tag, buffer = shape.save(self)

            self.save_tag(tag, buffer)

        for text_field in self.text_fields:
            tag, buffer = text_field.save()

            self.save_tag(tag, buffer)

        for matrix_bank in self.matrix_banks:
            if self.matrix_banks.index(matrix_bank):
                matrix_bank_tag = BinaryWriter()

                matrix_bank_tag.write_ushort(len(matrix_bank.matrices))
                matrix_bank_tag.write_ushort(len(matrix_bank.color_transforms))

                self.save_tag(42, matrix_bank_tag.buffer)
            
            for matrix in matrix_bank.matrices:
                matrix_tag = BinaryWriter()

                matrix_tag.write_int(int(round(matrix[0] * 1024)))
                matrix_tag.write_int(int(round(matrix[1] * 1024)))
                matrix_tag.write_int(int(round(matrix[2] * 1024)))
                matrix_tag.write_int(int(round(matrix[3] * 1024)))

                matrix_tag.write_twip(matrix[4])
                matrix_tag.write_twip(matrix[5])

                self.save_tag(8, matrix_tag.buffer)

            for color_transform in matrix_bank.color_transforms:
                color_transform_tag = BinaryWriter()

                color_transform_tag.write_uchar(int(round(color_transform[0])))
                color_transform_tag.write_uchar(int(round(color_transform[1])))
                color_transform_tag.write_uchar(int(round(color_transform[2])))

                color_transform_tag.write_uchar(int(round(color_transform[7] * 255)))
                color_transform_tag.write_uchar(int(round(color_transform[4] * 255)))
                color_transform_tag.write_uchar(int(round(color_transform[5] * 255)))
                color_transform_tag.write_uchar(int(round(color_transform[6] * 255)))

                self.save_tag(9, color_transform_tag.buffer)

        for movieclip in self.movieclips:
            tag, buffer = movieclip.save(self)

            self.save_tag(tag, buffer)

        self.writer.write(bytes(5)) # end tag

    def save_internal(self, filepath: str, is_texture: bool, enable_postfix: bool = False):
        self.writer = BinaryWriter()
        
        if not is_texture:
            self.writer.write_ushort(len(self.shapes))
            self.writer.write_ushort(len(self.movieclips))
            self.writer.write_ushort(len(self.textures))
            self.writer.write_ushort(len(self.text_fields))

            if not self.matrix_banks:
                self.matrix_banks.append(MatrixBank())
            
            matrix_bank = self.matrix_banks[0]
            self.writer.write_ushort(len(matrix_bank.matrices))
            self.writer.write_ushort(len(matrix_bank.color_transforms))

            self.writer.write(bytes(5)) # unused

            self.writer.write_ushort(len(self.exports))

            for export_id in self.exports:
                self.writer.write_ushort(export_id)
            
            for export_id in self.exports:
                self.writer.write_ascii(self.exports[export_id])

            self.save_tags(enable_postfix)
        
        else:
            self.save_texture()

        with open(filepath, 'wb') as file:
            compressor = Compressor()
            file.write(compressor.compress(self.writer.buffer, Signatures.SC, 1))
            #file.write(self.writer.buffer)

    def save(self, filepath: str, save_textures: bool = True, custom_postfix = ("_highres_tex.sc", "_lowres_tex.sc")):
        self.filename = filepath

        postfix_enable = False

        highres_postfix, lowres_postfix = custom_postfix

        if self.has_highres_texture or self.has_lowres_texture:
            if highres_postfix != self.highres_asset_postfix or lowres_postfix != self.lowres_asset_postfix:
                postfix_enable = True
                self.highres_asset_postfix = highres_postfix
                self.lowres_asset_postfix = lowres_postfix

        self.save_internal(filepath, False, postfix_enable)

        if save_textures:
            if self.has_external_texture:
                if self.has_highres_texture and not self.has_lowres_texture:
                    self.save_internal(os.path.splitext(filepath)[0] + self.texture_asset_postfix, True)
                    return

                # TODO auto generate lowres
                '''if has_highres_texture:
                    self.save_internal(os.path.splitext(filepath)[0] + self.highres_asset_postfix, True, False, True, True)
                    return
    
                if has_lowres_texture:
                    self.save_internal(os.path.splitext(filepath)[0] + self.lowres_asset_postfix, True, False, True, True)
                    return'''

                self.save_internal(os.path.splitext(filepath)[0] + self.texture_asset_postfix, True)

