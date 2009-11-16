from PIL import Image
import aggdraw

img = Image.new("RGB", (200, 200), "white")
canvas = aggdraw.Draw(img)

pen = aggdraw.Pen("black")
path = aggdraw.Path()

path.moveto(10, 10)
path.curveto(0, 60, 40, 100, 100, 100)
#path.close()
canvas.path(path, pen)
canvas.flush()

#img.save("curve.png", "PNG")
img.show()
