from xml.etree.ElementTree import *

from ..edge.edge import Edge
from ..fill.fill_style import FillStyle
from ..stroke.stroke_style import StrokeStyle

from . import NAMESPACES


class DOMShape:
    def __init__(self) -> None:
        # elements
        self.edges: list = []
        self.fills: list = []
        self.strokes: list = []
    
    def load(self, xml: Element):
        fills = xml.find("./xfl:fills", NAMESPACES)
        strokes = xml.find("./xfl:strokes", NAMESPACES)
        edges = xml.find("./xfl:edges", NAMESPACES)

        if fills is not None:
            for fill_element in fills:
                fill = FillStyle()
                fill.load(fill_element)
                self.fills.append(fill)
        
        if strokes is not None:
            for stroke_element in strokes:
                stroke = StrokeStyle()
                stroke.load(stroke_element)
                self.strokes.append(stroke)
        
        if edges is not None:
            for edge_element in edges:
                edge = Edge()
                edge.load(edge_element)

                if edge.edges is not None and edge.edges != "":
                    self.edges.append(edge)
    
    def save(self):
        xml = Element("DOMShape")

        fills = SubElement(xml, "fills")
        strokes = SubElement(xml, "strokes")
        edges = SubElement(xml, "edges")

        for fill in self.fills:
            fills.append(fill.save())
        
        for stroke in self.strokes:
            strokes.append(stroke.save())
        
        for edge in self.edges:
            edges.append(edge.save())

        return xml
