from pypaint.canvas import Canvas
from pypaint.path   import path
from pypaint.shape  import shape
from pypaint.text   import text


canvas = Canvas(600, 600)
shape  = shape()

txt = text("hi", 100, 100, font_name="DejaVu Sans")
txt.fill_color = (0.4)
txt.font_size  = 30
#txt.rotate(45)

canvas.add(txt)

arrow = shape.arrow(200, 100)
arrow.fill_color = (0.0)
arrow.rotate(100)

canvas.add(arrow)
canvas.draw()
canvas.show()

