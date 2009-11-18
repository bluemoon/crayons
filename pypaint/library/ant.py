from pypaint.context         import Context
from pypaint.utils.p_random  import random
from math                    import *

class Food:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

class Pheromone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.strength = 1.0
        
    def evaporate(self, d=0.985):
        self.strength *= d
        if self.strength < 0.05: self.strength = 0

class Ant:
    def __init__(self, colony, x, y):
        self.colony = colony
    
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        
        self.has_food = False
        self.trail = []
        self.wandering = random(10)
    
    def near(self, obj, radius=10):
        
        """Checks if something is nearby.
        
        If the object's x and y properties are within 
        the radius of the ant, returns true.
        
        """
        
        dx = abs(self.x-obj.x)
        dy = abs(self.y-obj.y)
        if dx < radius and dy < radius: return True
        else: return False
        
    def goal(self, obj):
        
        """Set a goal to move towards.
        
        Sets the object, which has x and y properties, as goal.
        The ant starts moving towards it.
        
        """
        
        self.vx = (obj.x-self.x) / abs(obj.x-self.x+0.0001)
        self.vy = (obj.y-self.y) / abs(obj.y-self.y+0.0001)
        
        try:
            self.vy /= abs(obj.x-self.x) / abs(obj.y-self.y+0.0001) #w to h ratio
        except ZeroDivisionError:
            pass
        
        self.wandering = 0
    
    def wander(self, d=0.3):
        """
        Wander around randomly.
        
        Ants wander around randomly until they find food.
        The d parameter controls the chaos with which the ant moves:
        a higher d means a more erratic ant,
        but too high is inefficient as the ant becomes indecisive.
        
        Eventually, ants that have been doing nothing to long,
        return to the colony.
        
        """
        
        self.vx += random(-d, d)
        self.vy += random(-d, d)
        
        print self.vx

        self.wandering += 1

        if self.wandering > self.colony.r: 
            self.goal(self.colony)

        if self.near(self.colony): 
            self.wandering = 0
    
    def follow(self):
        
        """Follow a nearby pheromone trail.
        
        If the ant is not carrying food to the colony,
        follow any nearby trail.
        If the pheromone has evaporated to much,
        the ant might lose interest in the trail,
        this ensures it doesn't get "stuck" on a useless trail.
        
        """
        
        for ant in self.colony:
            if ant != self or self.has_food == False:
                for pheromone in ant.trail:
                    if self.near(pheromone):
                        if random() > pheromone.strength: return
                        self.goal(pheromone)
                        if pheromone.strength > 0.5: return
                        else: break
    
    def harvest(self):
        
        """Collect nearby food.
        
        If the ant is not carrying anything,
        and it is near a source of food,
        pick up food and start marking the trail home.
        
        """

        for food in self.colony.foodsources:
            if self.near(food, radius=max(2,food.size/2)) and self.has_food == False: 
                food.size -= 1
                if food.size == 0: self.colony.foodsources.remove(food)
                self.trail = [Pheromone(food.x, food.y)]
                self.trail.append(Pheromone(self.x, self.y))
                self.has_food = True
        
    def hoard(self, trail=0.5):
        
        """Return straight home with food.
        
        Leave a trail of pheromone markers,
        which the other ants smell and follow to the food.
        
        """
        
        if self.has_food:
            self.goal(self.colony)
            if random() < trail:
                self.trail.append(Pheromone(self.x, self.y))
        
        #Drop food and start wandering again
        if self.near(self.colony) and self.has_food:
            self.trail.append(Pheromone(self.colony.x, self.colony.y))
            self.vx = 0
            self.vy = 0
            self.has_food = False
            self.colony.food += 1
    
    def forage(self, speed=2):
        self.follow() #follow nearby trails to food.
        self.harvest() #harvest nearby food source
        self.hoard() #bring food directly to colony
        self.wander() #some random wandering is more efficient

        self.vx = max(-speed, min(self.vx, speed))
        self.vy = max(-speed, min(self.vy, speed))        
        
        self.x += self.vx
        self.y += self.vy
        
        #trail evaporation
        for pheromone in self.trail:
            pheromone.evaporate()
            if pheromone.strength == 0:
                self.trail.remove(pheromone)

class Colony(list):
    def __init__(self, n, x, y, r):
        self.foodsources = []
        self.food = 0
        
        for i in range(n):
            self.append(Ant(self, x, y))
                             
        self.x = x
        self.y = y
        self.r = r

def colony(n, x, y, r):
    return Colony(n, x, y, r)
    
def food(x, y, size):
    return Food(x, y, size)


#### Demo stuff ####
def demo_setup():
    ## Starts a colony with 30 ants in it.
    global colony
    colony = colony(30, WIDTH/2, HEIGHT/2, 100)
    
    ## Add some food in the vicinity of the colony.
    for i in range(8):
        x = 50 + random(WIDTH-100)
        y = 50 + random(HEIGHT-100)
        s = random(20, 40)
        
        colony.foodsources.append(food(x, y, s))
    
def demo_draw(ctx):
    global colony
    
    ctx.fill(0.2)
    ctx.rect(0, 0, WIDTH, HEIGHT)
    
    ## Draw the hoarded food in the colony.
    ctx.fill(0.3)
    s = colony.food
    ctx.oval(colony.x-s/2, colony.y-s/2, s, s)
    
    ## Draw each foodsource in green.
    ## Watch it shrink as the ants eat away its size parameter!
    ctx.fill(0.6, 0.8, 0, 0.1)

    for f in colony.foodsources:
        ctx.oval(f.x-f.size/2, f.y-f.size/2, f.size, f.size)
    
    for ant in colony:
        ctx.stroke(0.8, 0.8, 0.8, 1.0)
        ctx.strokewidth(0.5)
        ctx.nofill()
        ctx.autoclosepath(False)
        
        ## Draw the pheromone trail for each ant.
        ## Ants leave a trail of scent from the foodsource,
        ## enabling other ants to find the food as well!
        if len(ant.trail) > 0:
            ctx.beginpath(ant.trail[0].x, ant.trail[0].y)

            for p in trail: 
                ctx.lineto(p.x, p.y)
                
            ctx.endpath()
        
        ## Change ant color when carrying food.
        ctx.nostroke()
        ctx.fill(0.8, 0.8, 0.8, 0.5)

        if ant.has_food: 
            ctx.fill(0.6, 0.8, 0)
        
        ## The main ant behaviour:
        ## 1) follow an encountered trail,
        ## 2) harvest nearby food source,
        ## 3) bring food back to colony,
        ## 4) wander aimlessly
        ant.forage()
        ctx.oval(ant.x, ant.y, 3, 3)


def main():
    ctx = Context()

    global WIDTH
    global HEIGHT 
    
    WIDTH  = ctx.Width()
    HEIGHT = ctx.Height()

    demo_setup()
    demo_draw(ctx)

    ctx.save('temp.png')

if __name__ == "__main__":
    main()
