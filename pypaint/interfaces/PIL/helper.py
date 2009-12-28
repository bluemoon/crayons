
class PILHelper:
    def decToRgba(self, RGBA):
        R = int(RGBA.r * 255)
        G = int(RGBA.g * 255)
        B = int(RGBA.b * 255)
        A = int(RGBA.a * 255)
        return (R, G, B, A)
