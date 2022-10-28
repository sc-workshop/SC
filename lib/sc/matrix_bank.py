from typing import List

from .color import Color
from .matrix import Matrix
from .resource import Resource
from .savable import Savable
from ..utils import BinaryWriter


class MatrixBank(Resource, Savable):
    def __init__(self) -> None:
        self.id: int = 0  # index

        self.matrices: List[Matrix] = []
        self.color_transforms: List[Color] = []

        self.matrices_count: int = 0
        self.color_transforms_count: int = 0

    def available_for_matrix(self, count=0):
        if len(self.matrices) >= 65534 - count:
            return False
        return True

    def available_for_colors(self, count=0):
        if len(self.color_transforms) >= 65534 - count:
            return False
        return True

    def add_matrix(self, matrix: list or dict or Matrix):
        if isinstance(matrix, list):
            matrix = Matrix(matrix[0],
                            matrix[1],
                            matrix[2],
                            matrix[3],
                            matrix[4],
                            matrix[5])
        elif isinstance(matrix, dict):
            matrix = Matrix(matrix["a"],
                            matrix["b"],
                            matrix["c"],
                            matrix["d"],
                            matrix["tx"],
                            matrix["ty"])

        if matrix not in self.matrices:
            self.matrices.append(matrix)

        return self.matrices.index(matrix)

    def get_color_transform(self, color_transform: Color):
        if color_transform not in self.color_transforms:
            self.color_transforms.append(color_transform)

        return self.color_transforms.index(color_transform)

    def load(self, swf) -> None:
        self.matrices_count = swf.reader.read_ushort()
        self.color_transforms_count = swf.reader.read_ushort()

        self.matrices = [_class() for _class in [Matrix] * self.matrices_count]
        self.color_transforms = [_class() for _class in [Color] * self.color_transforms_count]

    def save(self, stream: BinaryWriter):
        stream.write_ushort(len(self.matrices))
        stream.write_ushort(len(self.color_transforms))

    def get_tag(self) -> int:
        return 42
