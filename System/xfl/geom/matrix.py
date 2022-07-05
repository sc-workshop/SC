from xml.etree.ElementTree import *


class Matrix:
    def __init__(self, a: float = 1.0, b: float = 0.0, c: float = 0.0, d: float = 1.0, tx: float = 0.0, ty: float = 0.0) -> None:
        # attributes
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.tx = tx
        self.ty = ty
    
    def load(self, xml: Element):
        if "a" in xml.attrib:
            self.a = float(xml.attrib["a"])
        
        if "b" in xml.attrib:
            self.b = float(xml.attrib["b"])
        
        if "c" in xml.attrib:
            self.c = float(xml.attrib["c"])
        
        if "d" in xml.attrib:
            self.d = float(xml.attrib["d"])
        
        if "tx" in xml.attrib:
            self.tx = float(xml.attrib["tx"])
        
        if "ty" in xml.attrib:
            self.ty = float(xml.attrib["ty"])
    
    def save(self):
        xml = Element("Matrix")

        if self.a is not None:
            xml.attrib["a"] = str(self.a)
        
        if self.b is not None:
            xml.attrib["b"] = str(self.b)
        
        if self.c is not None:
            xml.attrib["c"] = str(self.c)
        
        if self.d is not None:
            xml.attrib["d"] = str(self.d)
        
        if self.tx is not None :
            xml.attrib["tx"] = str(self.tx)
        
        if self.ty is not None :
            xml.attrib["ty"] = str(self.ty)

        return xml
