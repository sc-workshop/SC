import cv2
import numpy as np

from sc.swf import SupercellSWF

from sc.swf.texture import SWFTexture
from sc.swf.shape import Shape, ShapeDrawBitmapCommand
from sc.swf.text_field import TextField
from sc.swf.matrix_bank import MatrixBank
from sc.swf.movieclip import MovieClipModifier, MovieClip, MovieClipFrame



if __name__ == "__main__":
    swf = SupercellSWF()

    texture = SWFTexture()
    texture.image = cv2.imread("assets/fish.png")
    
    height, width, channels = texture.image.shape

    texture.width = width
    texture.height = height
    print(width, height, channels)

    shape = Shape()
    shape.id = 0

    bmp = ShapeDrawBitmapCommand()
    bmp.texture_index = 0
    bmp.xy_coords = [[-410, -299.5], [410, -299.5], [410, 299.5], [-410, 299.5]]
    bmp.uv_coords = [[0, 0], [820, 0], [820, 599], [0, 599]]

    shape.bitmaps.append(bmp)

    mb = MatrixBank()

    mb.matrices.append([
        1, 0, 0, 1, 0, 0
    ])

    mb.color_transforms.append([
        0, 0, 0, 0, 1, 1, 1, 1
    ])

    mc = MovieClip()
    mc.id = 1

    mc.binds.append({
        "id": shape.id,
        "blend": "Mix",
        "name": "gp"
    })

    frame = MovieClipFrame()
    frame.name = "single"
    frame.elements.append({
        "bind": 0,
        "matrix": 0,
        "color": 0
    })

    mc.frames.append(frame)

    swf.exports[mc.id] = "fish"

    swf.textures.append(texture)
    swf.shapes.append(shape)
    swf.matrix_banks.append(mb)
    swf.movieclips.append(mc)

    swf.save("assets/fish.sc", True, True, False)
