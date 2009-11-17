import sys
import os
sys.path.append(os.getcwd()) 

from pyPaint import PyPaintContext as Context
from util import random

import ant_lib as ants

def setup():
    # Starts a colony with 30 ants in it.
    global colony
    colony = ants.colony(30, WIDTH/2, HEIGHT/2, 100)
    
    # Add some food in the vicinity of the colony.
    for i in range(8):
        x = 50 + random(WIDTH-100)
        y = 50 + random(HEIGHT-100)
        s = random(20, 40)
        colony.foodsources.append(ants.food(x,y,s))
    

def draw(ctx):
    global colony
    
    ctx.fill(0.2)
    ctx.rect(0, 0, WIDTH, HEIGHT)
    
    # Draw the hoarded food in the colony.
    ctx.fill(0.3)
    s = colony.food
    ctx.oval(colony.x-s/2, colony.y-s/2, s, s)
    
    # Draw each foodsource in green.
    # Watch it shrink as the ants eat away its size parameter!
    ctx.fill(0.6, 0.8, 0, 0.1)
    for f in colony.foodsources:
        ctx.oval(f.x-f.size/2, f.y-f.size/2, f.size, f.size)
    
    for ant in colony:
        ctx.stroke(0.8, 0.8, 0.8, 1.0)
        ctx.strokewidth(0.5)
        ctx.nofill()
        ctx.autoclosepath(False)
        
        # Draw the pheromone trail for each ant.
        # Ants leave a trail of scent from the foodsource,
        # enabling other ants to find the food as well!
        if len(ant.trail) > 0:
            ctx.beginpath(ant.trail[0].x, ant.trail[0].y)

            for p in ant.trail: 
                ctx.lineto(p.x, p.y)
                
            ctx.endpath()
        
        ## Change ant color when carrying food.
        ctx.nostroke()
        ctx.fill(0.8, 0.8, 0.8, 0.5)
        if ant.has_food: 
            ctx.fill(0.6, 0.8, 0)
        
        # The main ant behaviour:
        # 1) follow an encountered trail,
        # 2) harvest nearby food source,
        # 3) bring food back to colony,
        # 4) wander aimlessly
        ant.forage()
        ctx.oval(ant.x, ant.y, 3, 3)


def main():
    ctx = Context()

    global WIDTH
    global HEIGHT 
    
    WIDTH  = ctx.Width()
    HEIGHT = ctx.Height()

    setup()
    draw(ctx)

    ctx.save('temp.png')

if __name__ == "__main__":
    main()
