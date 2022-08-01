from xml.etree.ElementTree import *

from ..geom.matrix import Matrix
from .shape import DOMShape

from . import NAMESPACES


class DOMGroup:
    def __init__(self):
        self.members: list = []
        self.matrix: Matrix = None

    def load(self, xml: Element):
        matrix = xml.find("./xfl:matrix", NAMESPACES)
        if matrix is not None:
            for matrix_element in matrix:
                self.matrix = Matrix()
                self.matrix.load(matrix_element)
        for member in xml.find("./xfl:elements", NAMESPACES):
            if member.tag.endswith("DOMShape"):
                    shape = DOMShape()
                    shape.load(member)
                    self.members.append(shape)

    def save(self):
        xml = Element("DOMGroup")

        if self.matrix is not None:
            matrix = SubElement(xml, "matrix")
            matrix.append(self.matrix.save())

        members = Element("members")
        for member in self.members:
            members.append(member.save())
        xml.append(members)

        return xml
