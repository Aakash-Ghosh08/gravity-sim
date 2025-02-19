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
        global mass
        self.velocityX = 0
        self.velocityY = 0
        self.mass = mass
        self.body = Circle(x, y, 4, fill='orange')

    def calculateForce(self, particles, dt):
        global gravitationalConstant
        totalForceX, totalForceY = 0, 0
        
        for particle in particles:
            if particle is not self:
                dx = particle.body.centerX - self.body.centerX
                dy = particle.body.centerY - self.body.centerY
                r = math.sqrt(dx ** 2 + dy ** 2)
                
                if r > 0.5:
                    F = (gravitationalConstant * self.mass * particle.mass) / (r ** 2)
                    forceX = F * (dx / r)
                    forceY = F * (dy / r)
                    totalForceX += forceX
                    totalForceY += forceY

        self.velocityX += (totalForceX / self.mass) * dt
        self.velocityY += (totalForceY / self.mass) * dt

    def move(self):
        self.body.centerX += self.velocityX
        self.body.centerY += self.velocityY
        if not (0 <= self.body.centerX <= app.width and 0 <= self.body.centerY <= app.height):
            self.body.visible = False
            return False
        return True
                    
    def moveApartIfTouching(self, particles):
        """
        Handle collisions between particles with perfect conservation of momentum.
        
        Args:
            particles: List of particle objects to check collisions against
        """
        for particle in particles:
            # Skip self-collision and check for actual collision
            if self is particle or not self.body.hitsShape(particle.body):
                continue
                
            # Calculate center-to-center vector
            dx = particle.body.centerX - self.body.centerX
            dy = particle.body.centerY - self.body.centerY
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Normalize the direction vector
            if distance < 0.0001:  # Handle edge case of perfectly overlapping particles
                dx, dy = 1, 0
                distance = 0.0001
            else:
                dx, dy = dx/distance, dy/distance
                
            # Calculate overlap and separate particles
            overlap = (self.body.radius + particle.body.radius - distance)
            if overlap > 0:
                # Move particles apart just enough to prevent overlap
                moveX = dx * overlap * 0.5
                moveY = dy * overlap * 0.5
                
                self.body.centerX -= moveX
                self.body.centerY -= moveY
                particle.body.centerX += moveX
                particle.body.centerY += moveY
                
                # Simply average the velocities - perfect conservation of momentum
                # assuming equal mass particles
                avgVelX = (self.velocityX + particle.velocityX) * 0.5
                avgVelY = (self.velocityY + particle.velocityY) * 0.5
                
                # Set both particles to the average velocity - no damping
                self.velocityX = avgVelX
                self.velocityY = avgVelY
                particle.velocityX = avgVelX
                particle.velocityY = avgVelY
                
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
        particle.calculateForce(particles, 1)
        
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