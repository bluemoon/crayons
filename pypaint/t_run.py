from pypaint.canvas import Canvas
from pypaint.path   import path
from pypaint.shape  import shape


canvas = Canvas(600, 600)
shape  = shape()


arrow = shape.arrow(200, 100)
arrow.fill_color = (0.2)
arrow.rotate(90)

canvas.add(arrow)
canvas.draw()
canvas.show()

#ctx = Context(width=600, height=600)

#ctx.translate(300, 300)
#ctx.scale(0.04)
#ctx.nofill()
#ctx.fill(0.4)
#ctx.strokewidth(1)
#ctx.fontsize(60)
#ctx.font(fontpath="/home/bluemoon/Desktop/148Tipos/148Tipos/Top 80/TrueType/Akzidenz Grotesk/Akzidenz Grotesk CE Light Bold.ttf")

#ctx.text("Gofuckyourself", 0, 300)

#ctx.show()
#ctx.save('temp.png')
