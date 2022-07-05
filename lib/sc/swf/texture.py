from .writable import Writable

from lib.utils import *


class SWFTexture(Writable):
    def __init__(self) -> None:
        self.pixel_format: str = "GL_RGBA"
        self.pixel_internal_format: str = "GL_RGBA8"
        self.pixel_type: str = "GL_UNSIGNED_BYTE"

        self.mag_filter: str = "GL_LINEAR"
        self.min_filter: str = "GL_NEAREST"
        self.linear: bool = True
        self.downscaling: bool = True

        self.width: int = 0
        self.height: int = 0

        self.image = None
    
    def load(self, swf, tag: int, has_external_texture: bool):
        pixel_type_index = swf.reader.read_uchar()

        self.pixel_format = PIXEL_FORMATS[pixel_type_index]
        self.pixel_internal_format = PIXEL_INTERNAL_FORMATS[pixel_type_index]
        self.pixel_type = PIXEL_TYPES[pixel_type_index]

        self.mag_filter = "GL_LINEAR"
        self.min_filter = "GL_NEAREST"
        if tag in [16, 19, 29]:
            self.mag_filter = "GL_LINEAR"
            self.min_filter = "GL_LINEAR_MIPMAP_NEAREST"
        elif tag == 34:
            self.mag_filter = "GL_NEAREST"
            self.min_filter = "GL_NEAREST"
        
        self.linear = True if tag not in [27, 28, 29] else False
        self.downscaling = True if tag in [1, 16, 28, 29] else False

        self.width = swf.reader.read_ushort()
        self.height = swf.reader.read_ushort()

        if not has_external_texture:
            load_image(self, swf)
    
    def save(self, has_external_texture: bool):
        super().save()

        height, width, channels = self.image.shape

        self.width = width
        self.height = height

        if channels == 4 and (self.pixel_format, self.pixel_internal_format) != ("GL_LUMINANCE_ALPHA", "GL_LUMINANCE8_ALPHA8"):
            self.pixel_format = "GL_RGBA"

            if self.pixel_type == "GL_UNSIGNED_BYTE":
                self.pixel_internal_format = "GL_RGBA8"
            
            elif self.pixel_type == "GL_UNSIGNED_SHORT_4_4_4_4":
                self.pixel_internal_format = "GL_RGBA4"
            
            else:
                self.pixel_internal_format = "GL_RGB5_A1"
        
        elif channels == 3:
            self.pixel_format = "GL_RGB"
            self.pixel_type = "GL_UNSIGNED_SHORT_5_6_5"
            self.pixel_internal_format = "GL_RGB565"
        
        elif channels == 4 and (self.pixel_format, self.pixel_internal_format) == ("GL_LUMINANCE_ALPHA", "GL_LUMINANCE8_ALPHA8"): # OpenCV doesn't support LUMINANCE_ALPHA :(((
            self.pixel_format = "GL_LUMINANCE_ALPHA"
            self.pixel_type = "GL_UNSIGNED_BYTE"
            self.pixel_internal_format = "GL_LUMINANCE8_ALPHA8"
        
        else:
            self.pixel_format = "GL_LUMINANCE"
            self.pixel_type = "GL_UNSIGNED_BYTE"
            self.pixel_internal_format = "GL_LUMINANCE8"

        pixel_type_index = PIXEL_INTERNAL_FORMATS.index(self.pixel_internal_format)

        tag = 1
        if (self.mag_filter, self.min_filter) == ("GL_LINEAR", "GL_NEAREST"):
            if not self.linear:
                tag = 27 if not self.downscaling else 28
            else:
                tag = 24 if not self.downscaling else 1
        
        if (self.mag_filter, self.min_filter) == ("GL_LINEAR", "GL_LINEAR_MIPMAP_NEAREST"):
            if not self.linear and not self.downscaling:
                tag = 29
            else:
                tag = 19 if not self.downscaling else 16
        
        if (self.mag_filter, self.min_filter) == ("GL_NEAREST", "GL_NEAREST"):
            tag = 34

        self.write_uchar(pixel_type_index)

        self.write_ushort(self.width)
        self.write_ushort(self.height)

        if not has_external_texture:
            save_image(self)

        return tag, self.buffer
