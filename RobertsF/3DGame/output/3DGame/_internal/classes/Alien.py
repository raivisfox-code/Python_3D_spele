from ursina import *
from random import choice, uniform
from classes.GameFunctions import GameFunctions
from classes.Target import Target

class Alien(Target):
    def __init__(self, x, y, z, on_destroy):
        super().__init__(
            x=x,
            y=y,
            z=z,
            on_destroy=on_destroy,
            name="Alien",
            model="/assets/models/alien.glb",
            scale=(1/50,1/50,1/50),
            hasMovement=False,
            hasGravity=False
        )

        self.ring1 = Entity(
            parent=self,
            model="/assets/models/torus.glb",
            position=(0, -5, 0),
            scale=18,
            color=color.hex("#05D9FF"),
        )

        self.ring2 = Entity(
            parent=self,
            model="/assets/models/torus.glb",
            position=(0, -7, 0),
            scale=13,
            color=color.hex("#05D9FF"),
        )
        
        self.ring3 = Entity(
            parent=self,
            model="/assets/models/torus.glb",
            position=(0, -14, 0),
            scale=10,
            color=color.hex("#05D9FF"),
        )

        self.move_loops()
        self.animate_hover()

    def update(self):
        super().update()
        
    def move_loops(self):
        if self.destroyed:
            return
        duration = 3
        ring1Range = -random.randrange(10, 20, 1)
        ring2Range = -random.randrange(10, 20, 1)
        ring3Range = -random.randrange(10, 20, 1)
        self.ring1.animate_position(Vec3(0, ring1Range, 0), duration=duration, curve=curve.linear)
        self.ring2.animate_position(Vec3(0, ring2Range, 0), duration=duration, curve=curve.linear)
        self.ring3.animate_position(Vec3(0, ring3Range, 0), duration=duration, curve=curve.linear)

        self.ring1.animate_color(color.hex("#39f7b8"), duration=duration)
        self.ring2.animate_color(color.hex("#05D9FF"), duration=duration)
        self.ring3.animate_color(color.hex("#6a1fff"), duration=duration)
        invoke(self.animate_loops, delay = duration)

    def animate_loops(self):
        if self.destroyed:
            return
        duration = 3
        ring1Range = -random.randrange(5, 8, 1)
        ring2Range = -random.randrange(10, 20, 1)
        ring3Range = -random.randrange(10, 20, 1)
        self.ring1.animate_position(Vec3(0, ring1Range, 0), duration=duration, curve=curve.linear)
        self.ring2.animate_position(Vec3(0, ring2Range, 0), duration=duration, curve=curve.linear)
        self.ring3.animate_position(Vec3(0, ring3Range, 0), duration=duration, curve=curve.linear)

        
        self.ring1.animate_color(color.hex("#6a1fff"), duration=duration)
        self.ring2.animate_color(color.hex("#39c1f7"), duration=duration)
        self.ring3.animate_color(color.hex("#39f7b8"), duration=duration)
        invoke(self.move_loops, delay = duration)

    def animate_hover(self):
        if self.destroyed:
            return
        height= random.randrange(10, 30, 5) / 100
        duration = random.randint(3, 5)
        self.animate_position(Vec3(self.x, self.y + height, self.z), duration = duration, curve=curve.linear)
        invoke(self.move_down, delay = duration)

    def move_down(self):
        if self.destroyed:
            return
        height= random.randrange(10, 30, 5) / 100
        duration = random.randint(3, 5)
        self.animate_position(Vec3(self.x, self.y - height, self.z), duration = duration, curve=curve.linear)
        invoke(self.animate_hover, delay = duration)

    def take_damage(self, amount):         
        y_range = random.randrange(8, 15, 1)
        x_range = random.randrange(800, 1000, 1) * random.choice([1,-1])
        z_range = random.randrange(800, 1000, 1) * random.choice([1,-1])

        self.health -= amount

        if self.health <= 0:
            GameFunctions.spawn_target(x=x_range,
                                        y=y_range,
                                        z=z_range, 
                                        target_name="Ufo",
                                        on_destroy=self.on_destroy)
            destroy(self)
            destroy(self.health_bar)
            self.destroyed = True
        else: #shrink health
            health_percent = max(self.health / 100, 0) #check if health is < 0, so damage bar doesnt 'flip' to negative values
            self.health_bar.scale_x = 0.7 * health_percent #set health bar to % value of whole bar
