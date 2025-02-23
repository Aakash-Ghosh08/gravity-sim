from cmu_graphics import *
import math
import pyautogui

# Constants
gravitationalConstant = 20
mass = 2
particles = set()
heldParticles = set()
app.width, app.height = pyautogui.size()
#app.height -= 55
isMouseDown = False
xMouse = yMouse = 0
particleCountLabel = Label(0, 50, 50, size=50, fill = "white")
maxForce = 0
app.background = "black"

def distanceSquared(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    return dx * dx + dy * dy

def angleTo(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)

class Particle:
    def __init__(self, x, y):
        self.velocityX = self.velocityY = 0
        self.body = Circle(x, y, 4, fill=rgb(0,0,255))
        self.mass = mass

    def calculateForce(self, dt):
        totalForceX = totalForceY = 0
        
        for particle in particles:
            if self is particle or self.body.hitsShape(particle.body):
                continue
            
            dx = particle.body.centerX - self.body.centerX
            dy = particle.body.centerY - self.body.centerY
            r2 = dx * dx + dy * dy
            
            if r2 > 0.25:
                r = math.sqrt(r2)
                F = (gravitationalConstant * self.mass * particle.mass) / r2
                totalForceX += F * (dx / r)
                totalForceY += F * (dy / r)

        self.velocityX += (totalForceX / self.mass) * dt
        self.velocityY += (totalForceY / self.mass) * dt
        
        F = math.sqrt(totalForceX ** 2 + totalForceY ** 2)
        F_max = 30
        F_scaled = (math.log(F + 1) / math.log(F_max + 1)) * 30  

        if F_scaled < 6:
            self.body.fill = rgb(0, int(F_scaled * 255 / 6), 255)
        elif F_scaled < 12:
            self.body.fill = rgb(0, 255, int(255 - (F_scaled - 6) * 255 / 6))
        elif F_scaled < 18:
            self.body.fill = rgb(int((F_scaled - 12) * 255 / 6), 255, 0)
        elif F_scaled < 24:
            self.body.fill = rgb(255, int(255 - (F_scaled - 18) * 255 / 6), 0)
        elif F_scaled <= 30:
            self.body.fill = rgb(255, max(0, int((30 - F_scaled) * 255 / 6)), 0)

    def move(self):
        global particleCountLabel
        self.body.centerX += self.velocityX
        self.body.centerY += self.velocityY

        if not (0 <= self.body.centerX <= app.width and 0 <= self.body.centerY <= app.height):
            self.body.visible = False
            return False
        return True

    def resolveCollisions(self):
        for particle in particles:
            if self is particle or not self.body.hitsShape(particle.body):
                continue
            
            dx = particle.body.centerX - self.body.centerX
            dy = particle.body.centerY - self.body.centerY
            r2 = dx * dx + dy * dy
            
            if r2 > 0.0001:
                r = math.sqrt(r2)
                dx, dy = dx / r, dy / r
            else:
                dx, dy = 1, 0
                r = 0.0001
            
            overlap = (self.body.radius + particle.body.radius) - r
            if overlap > 0:
                moveX = dx * overlap * 0.5
                moveY = dy * overlap * 0.5
                
                self.body.centerX -= moveX
                self.body.centerY -= moveY
                particle.body.centerX += moveX
                particle.body.centerY += moveY
                
                avgVelX = (self.velocityX + particle.velocityX) * 0.5
                avgVelY = (self.velocityY + particle.velocityY) * 0.5
                self.velocityX = particle.velocityX = avgVelX
                self.velocityY = particle.velocityY = avgVelY

def onMouseDrag(mouseX, mouseY):
    global xMouse, yMouse
    xMouse, yMouse = mouseX, mouseY

def onMousePress(mouseX, mouseY):
    global xMouse, yMouse, isMouseDown
    xMouse, yMouse = mouseX, mouseY
    isMouseDown = True

def onMouseRelease(mouseX, mouseY):
    global particles, heldParticles, isMouseDown
    particles.update(heldParticles)
    heldParticles.clear()
    isMouseDown = False

def onStep():
    global particles, heldParticles, isMouseDown, particleCountLabel
    
    particleCountLabel.value = len(particles) + len(heldParticles)
    
    for particle in particles:
        particle.calculateForce(1)
    
    particles = {p for p in particles if p.move()}
    
    for particle in particles:
        particle.resolveCollisions()
    
    for particle in heldParticles:
        particle.move()
        particle.resolveCollisions()
    
    if isMouseDown:
        newParticle = Particle(xMouse, yMouse)
        if all(not newParticle.body.hitsShape(p.body) for p in heldParticles):
            heldParticles.add(newParticle)
            for p in heldParticles:
                angle = angleTo(p.body.centerX, p.body.centerY, xMouse, yMouse)
                distFactor = math.sqrt(distanceSquared(p.body.centerX, p.body.centerY, xMouse, yMouse)) / 10
                p.velocityX = math.cos(angle) * distFactor
                p.velocityY = math.sin(angle) * distFactor
        else:
            newParticle.body.visible = False
            del newParticle

cmu_graphics.run()