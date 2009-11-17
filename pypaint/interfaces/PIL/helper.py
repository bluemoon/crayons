
class PILHelper:
    def decToRgba(self, RGBA):
        R = int(RGBA[0] * 255)
        G = int(RGBA[1] * 255)
        B = int(RGBA[2] * 255)
        A = int(RGBA[3] * 255)
        return (R, G, B, A)
