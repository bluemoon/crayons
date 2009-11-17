import sys
import os
sys.path.append(os.getcwd()) 

from pyPaint import PyPaintContext as Context
import boids

WIDTH  = 500
HEIGHT = 500

def setup(ctx):    
    # Create 3 flocks each with 10 boids.
    # Each flock crowds around the center of the canvas.
    global flocks
    flocks = []
    for i in range(3):
        flock = boids.flock(10, 0, 0, WIDTH, HEIGHT, ctx)
        flock.goal(WIDTH/2, HEIGHT/2, 0)
        flocks.append(flock)
    
def draw(ctx):
    ctx.background(0.2)
    
    ctx.fill(0.8)
    #fontsize(20)
    #w = textwidth("STATUE")
    #text("STATUE", WIDTH/2-w/2, HEIGHT/2)

    # Update each flock.
    global flocks

    for flock in flocks:
        flock.update(goal=40)
        
        # Draw a grey arrow for each boid in a block.
        # Radius and opacity depend on the boids z-position.
        for boid in flock:
            r = 10 + boid.z * 0.25
            alpha = 0.5 + boid.z*0.01
            fill(0.6, 0.6, 0.6, alpha)
            rotate(-boid.angle)
            arrow(boid.x-r/2, boid.y-r/2, r)
            #reset()


def main():
    ctx = Context(width=500, height=500)
    
    setup(ctx)
    draw(ctx)




if __name__ == "__main__":

    main()
