#import cv2
#import numpy as np

from sc.swf import SupercellSWF
#from sc.xfl import XFlash

from sc.xfl import convert_sc_to_xfl
#from sc.utils.json_converter import convert_sc_to_json


if __name__ == "__main__":
    sc = SupercellSWF()
    sc.load("assets/loading.sc")

    #xfl = XFlash()
    #xfl.load_from_sc(sc)

    convert_sc_to_xfl(sc)

    #convert_sc_to_json("assets/characters.sc")
