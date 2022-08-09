class MatrixBank:
    def __init__(self, matrices_count: int = 0, color_transforms_count: int = 0) -> None:
        self.matrices_count = matrices_count
        self.color_transforms_count = color_transforms_count
        
        self.matrices: list = [[1, 0, 0, 1, 0, 0]] * self.matrices_count
        self.color_transforms: list = [[0, 0, 0, 0, 1, 1, 1, 1]] * self.color_transforms_count

    def get_matrix(self, matrix: list):
        if matrix not in self.matrices:
            return None

        return self.matrices[self.matrices.index(matrix)]

    def get_color_transform(self, color_transform: list):
        if color_transform not in self.color_transforms:
            return None

        return self.color_transforms[self.color_transforms.index(color_transform)]
