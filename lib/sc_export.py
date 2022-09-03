import copy

from lib.fla import *
from lib.sc import *

sprites_list = []
prepared_shapes = {}
'''and False not in [frame.duration == 1 and False not in [element for element in frame.elements] frame for frame in layer.frames]'''
def check_shape_symbol(symbol: DOMSymbolItem):
    return True if False not in [len(layer.frames) == 1 and False not in [frame.duration == 1 and False not in [isinstance(element, DOMBitmapInstance) or isinstance(element, Edge) for element in frame.elements] for frame in layer.frames] for timeline in symbol.timeline for layer in timeline.layers] else False
def convert_movieclip(swf, symbol: DOMSymbolItem):
    movieclip = MovieClip()

    bind_elements = []

    for timeline in symbol.timeline:
        for layer in reversed(timeline.layers):
            for frame in layer.frames:
                frame_elements = []

                for element in frame.elements:
                    bind_element = copy.deepcopy(element)
                    if isinstance(element, DOMSymbolInstance) or isinstance(element, DOMDynamicText):
                        bind_element.matirx = None
                        bind_element.color = None
                    elif isinstance(element, DOMBitmapInstance):
                        bind_element.matrix = None

                    if bind_element not in bind_elements:
                        bind_elements.append(bind_element)
                    else:




def prepare_shape(symbol: DOMSymbolItem):
    prepared_shapes[symbol.name] = []
    for timeline in symbol.timeline:
        for layer in timeline.layers:
            for frame in layer.frames:
                for element in frame.elements:
                    prepared_shapes[symbol.name].append(element)
def convert_shape(library):
    pass

def fla_to_sc(filepath):
    project = XFL().load(filepath)
    swf = SupercellSWF()

    for name, symbol in project.symbols.items():
        if symbol.symbol_type == "graphic" and check_shape_symbol(symbol):
            prepare_shape(symbol)

        swf.resources[symbol.name] = convert_movieclip(swf, symbol)

    '''for name, bitmaps in prepared_shapes.items():
        for bitmap in bitmaps:
            if isinstance(bitmap, DOMBitmapInstance):'''







