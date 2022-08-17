from .writable import Writable

class MatrixBank(Writable):
    def __init__(self) -> None:
        self.index: int = 0
        self.matrices_count: int = 0
        self.color_transforms_count: int = 0

    def get_matrix(self, matrix: list):
        if matrix not in self.matrices:
            return None

        return self.matrices[self.matrices.index(matrix)]

    def get_color_transform(self, color_transform: list):
        if color_transform not in self.color_transforms:
            return None

        return self.color_transforms[self.color_transforms.index(color_transform)]
    
    def load(self, swf):
        self.matrices_count = swf.reader.read_ushort()
        self.color_transforms_count = swf.reader.read_ushort()

        self.matrices: list = [[1.0, 0.0, 0.0, 1.0, 0.0, 0.0]] * self.matrices_count
        self.color_transforms: list = [[0, 0, 0, 0, 1.0, 1.0, 1.0, 1.0]] * self.color_transforms_count

    def save(self):
        super().save()

        self.write_ushort(len(self.matrices))
        self.write_ushort(len(self.color_transforms))

        return 42, self.buffer
