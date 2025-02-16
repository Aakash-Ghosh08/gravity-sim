from cmu_graphics import *
import math
import pyautogui

# Constants
gravitationalConstant = 20
mass = 1
heldParticles = []
particles = []
app.width, app.height = pyautogui.size()
app.height -= 55
isMouseDown = False
xMouse = 0
yMouse = 0

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def angleTo(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

class Particle:
    def __init__(self, x, y):
        self.velocityX = 0
        self.velocityY = 0
        self.body = Circle(x, y, 2, fill='orange')

    def calculateForce(self, particles):
        global gravitationalConstant, mass
        totalForceX, totalForceY = 0, 0
        
        for particle in particles:
            if particle is not self and distance(self.body.centerX, self.body.centerY,particle.body.centerX, particle.body.centerY) > .5:
                dx = particle.body.centerX - self.body.centerX
                dy = particle.body.centerY - self.body.centerY
                r = math.sqrt(dx ** 2 + dy ** 2)
                
                if(not r == 0):
                    F = (gravitationalConstant * mass * mass) / (r ** 2)

                if r > 0:
                    forceX = F * (dx / r)
                    forceY = F * (dy / r)
                    totalForceX += forceX
                    totalForceY += forceY

        self.velocityX += totalForceX
        self.velocityY += totalForceY

    def move(self):
        self.body.centerX += self.velocityX
        self.body.centerY += self.velocityY
        if not (0 <= self.body.centerX <= app.width and 0 <= self.body.centerY <= app.height):
            self.body.visible = False
            return False
        return True
                    
    def moveApartIfTouching(self, particles):
        for particle in particles:
            if(self is not particle and self.body.hitsShape(particle.body)):
                angle = math.radians(angleTo(self.body.centerX, self.body.centerY, particle.body.centerX, particle.body.centerY))
                offset = (2 * self.body.radius - distance(self.body.centerX,self.body.centerY, particle.body.centerX,particle.body.centerY))/2
                
                self.body.centerX += offset * math.cos(angle)
                self.body.centerY -= offset * math.sin(angle)
                particle.body.centerX -= offset * math.cos(angle)
                particle.body.centerY += offset * math.sin(angle)
                
                damping = .85
                relativeVelocityX = self.velocityX - particle.velocityX
                relativeVelocityY = self.velocityY - particle.velocityY
                self.velocityX -= damping * relativeVelocityX
                self.velocityY -= damping * relativeVelocityY
                particle.velocityX += damping * relativeVelocityX
                particle.velocityY += damping * relativeVelocityY
                
def onMouseDrag(mouseX, mouseY):
    global xMouse,yMouse,isMouseDown
    xMouse,yMouse = mouseX,mouseY

def onMousePress(mouseX,mouseY):
    global xMouse,yMouse, isMouseDown
    xMouse,yMouse = mouseX,mouseY
    isMouseDown = True

def onMouseRelease(mouseX, mouseY):
    global particles, heldParticles, isMouseDown
    particles.extend(heldParticles)
    heldParticles.clear()
    isMouseDown = False

def onStep():
    global particles, heldParticles, isMouseDown
    for particle in particles:
        particle.calculateForce(particles)
        
    particles = [p for p in particles if p.move()]
    
    for particle in particles:
        particle.moveApartIfTouching(particles)
        
    for particle in heldParticles:
        particle.move()
        particle.moveApartIfTouching(heldParticles)
    
    if(isMouseDown):
        newParticle = Particle(xMouse, yMouse)
        hitsParticle = False
        for particle in heldParticles:
            if(newParticle.body.hitsShape(particle.body)):
                hitsParticle = True
                
        if(not hitsParticle):
            heldParticles.append(newParticle)

            for particle in heldParticles:
                angle = math.radians(angleTo(particle.body.centerX, particle.body.centerY, xMouse,yMouse))
                distanceFromMouse = distance(particle.body.centerX, particle.body.centerY, xMouse,yMouse)/10
                particle.velocityX = math.cos(angle) * distanceFromMouse
                particle.velocityY = math.sin(angle) * distanceFromMouse
        else:
            newParticle.body.visible = False
            del newParticle

cmu_graphics.run()