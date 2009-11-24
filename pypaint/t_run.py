from pypaint.context          import *
from pypaint.utils.p_random   import random

ctx = Context(width=300, height=300)

ctx.stroke(0.2)
ctx.fontsize(10)
ctx.font(fontpath="/home/bluemoon/Projects/shoebot-19b6b98eb602/assets/notcouriersans.ttf")
ctx.text("hi hi", 100, 100)

ctx.save('temp.png')
