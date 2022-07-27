class MatrixBank:
    def __init__(self) -> None:
        self.matrices: list = []
        self.color_transforms: list = []

    def get_matrix(self, matrix):
        if len(matrix) != 6:
            matrix = [array_value for array in matrix for array_value in array]

        if matrix not in self.matrices:
            self.matrices.append(matrix)

        return self.matrices.index(matrix)

    def get_color(self, color):
        if color not in self.color_transforms:
            self.color_transforms.append(color)

        return self.color_transforms.index(color)
