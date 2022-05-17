from math import *


class AffineTransform:
    def __init__(self, a: float = 1.0, b: float = .0, c: float = .0, d: float = 1.0, tx: float = .0, ty: float = .0) -> None:
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.tx = tx
        self.ty = ty
    
    def translate(self, x: float, y: float):
        self.tx = x * self.a + y * self.b
        self.ty = x * self.c + y * self.d

    def get_translation(self):
        return self.tx, self.ty
    
    def scale(self, sx: float, sy: float):
        self.a *= sx
        self.b *= sy
        self.c *= sx
        self.d *= sy

    def get_scale(self):
        return sqrt(self.a**2 + self.c**2), sqrt(self.b**2 + self.d**2)

    def rotate90(self):
        m0 = self.a
        self.a = self.b
        self.b = m0 * -1

        m0 = self.c
        self.c = self.d
        self.d = m0 * -1

    def rotate180(self):
        self.a *= -1
        self.d *= -1

        self.b *= -1
        self.c *= -1

    def rotate270(self):
        m0 = self.a
        self.a = self.b * -1
        self.b = m0

        m0 = self.c
        self.c = self.d * -1
        self.d = m0

    def rotate(self, theta: float):
        s = sin(theta)
        if s == 1.0:
            self.rotate90()
        elif s == -1.0:
            self.rotate270()
        else:
            c = cos(theta)
            if c == -1.0:
                self.rotate180()
            elif c != 1.0:
                m0 = self.a
                m1 = self.b

                self.a = c * m0 + s * m1
                self.b = -s * m0 + c * m1

                m0 = self.c
                m1 = self.d

                self.c = c * m0 + s * m1
                self.d = -s * m0 + c * m1

    def rotate_about(self, theta: float, x: float, y: float):
        self.translate(x, y)
        self.rotate(theta)
        self.translate(-x, -y)

    def get_rotation(self):
        return atan2(self.c, self.a)
    
    def get_matrix(self):
        return self.a, self.b, self.c, self.d, self.tx, self.ty
