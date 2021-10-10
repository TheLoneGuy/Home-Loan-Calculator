from tkinter import Canvas
import random
import math

random.seed()

# Snow or Rain
class Drop:
    def __init__(self):
        self.x = random.randrange(width)
        self.y = random.randrange(-400, -20)
        self.z = random.randrange(0, 20)
        self.yspeed = random.randrange(5, 30)
        self.length = random.randrange(10, 20)

        self.line = c.create_line(self.x, self.y, self.x, self.y+10, fill="purple", width="1")

    def fall(self):
        self.y += self.yspeed
        self.yspeed += 0.2

        if(self.y > height):
            self.y = random.randrange(-200, -100)
            self.yspeed = random.randrange(4, 10)

    def show(self):
        c.coords(self.line, self.x, self.y, self.x, self.y+self.length)


class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Particle:
    def __init__(self, canvas, color):
        self.parent = canvas
        width = self.parent.CANVAS_WIDTH
        height = self.parent.CANVAS_HEIGHT

        self.size = 4 + random.random() * 8
        self.pos = Vector(max(min(random.random()*width, width-self.size), self.size), 
        max(min(random.random()*height, height-self.size), self.size))
        self.vel = Vector(random.random()*2-1, random.random()*2-1)

        self.circle = self.parent.create_oval(self.pos.x-self.size, self.pos.y-self.size, self.pos.x+self.size, self.pos.y+self.size)
        self.parent.itemconfigure(self.circle, fill=color, outline=color)

    def update(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

        if self.pos.x+self.size > self.parent.CANVAS_WIDTH:
            self.vel.x = -1-random.random()
        elif self.pos.x-self.size < 0:
            self.vel.x = 1+random.random()
        else:
            self.vel.x *= 1 + (random.random()*0.005)

        if self.pos.y+self.size > self.parent.CANVAS_HEIGHT:
            self.vel.y = -1-random.random()
        elif self.pos.y-self.size < 0:
            self.vel.y = 1+random.random()
        else:
            self.vel.y *= 1 + (random.random()*0.005)

    def show(self):
        vr_size = self.size * max(min(15 - (self.dist(self.parent.mouse, self.pos) / 10), 10), 1)
        self.parent.coords(self.circle, self.pos.x-vr_size, self.pos.y-vr_size, self.pos.x+vr_size, self.pos.y+vr_size)

    @staticmethod
    def dist(p1, p2):
        # pythagoras theorem
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        return math.sqrt(dx*dx + dy*dy)

class Background(Canvas):
    def __init__(self, master, quantity=50, colors=["#BDE8FF", "#FFD0DB"]):
        super().__init__(master)
        self.configure(height=master.winfo_height(), width=master.winfo_width(), bg="white")
        self.pack(side="top", fill="both", expand=True)
        self.update()

        self.CANVAS_HEIGHT = self.winfo_height()
        self.CANVAS_WIDTH = self.winfo_width()
        self.quantity = quantity
        self.colors = colors

        self.elements = []
        self.mouse = Vector()
        
        self.bind("<Motion>", self.MouseMove)

    def MouseMove(self, e):
        self.mouse.x, self.mouse.y = e.x, e.y

    def setup(self):
        for i in range(self.quantity):
            color = random.choice(self.colors)
            self.elements.append(Particle(self, color=color))

    def animation(self):
        for i in range(self.quantity):
            self.elements[i].update()
            self.elements[i].show()

        self.update()
        self.after(30, self.animation) 
