import os

import cv2
#import numpy as np

from sc.swf import SupercellSWF
#from sc.xfl import XFlash

from sc.xfl import convert_sc_to_xfl
#from sc.utils.json_converter import convert_sc_to_json


if __name__ == "__main__":
    sc = SupercellSWF()
    sc.load("assets/characters.sc")

    #print(sc.textures[0].image.shape)

    #for texture in sc.textures:
        #cv2.imwrite(f"assets/{os.path.basename(os.path.splitext(sc.filename)[0])}_texture_{sc.textures.index(texture)}.png", texture.image)

    #xfl = XFlash()
    #xfl.load_from_sc(sc)

    convert_sc_to_xfl(sc)

    #convert_sc_to_json("assets/characters.sc")
