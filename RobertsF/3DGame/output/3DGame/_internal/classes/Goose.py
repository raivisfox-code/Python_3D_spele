from ursina import *
from random import choice, uniform
from classes.GameFunctions import GameFunctions
from classes.Target import Target

class Goose(Target):
    def __init__(self, x, y, z, on_destroy):
        super().__init__(
            x=x,
            y=y,
            z=z,
            on_destroy=on_destroy,
            name="Goose",
            model="assets/models/goose.glb",
            scale=(1/30, 1/30, 1/30),
            hasMovement=True,
            hasGravity=True,
            initial_move_pos=0
        )
        
        self.rotation_y = 55
        self.spawn_position = Vec3(*self.position)

    def update(self):
        super().update()
        if self.hasMovement:
            if not self.spawned:
                self.spawn()
            else:
                self.move()

    def take_damage(self, amount):        
        self.health -= amount
        if self.health <= 0:
            GameFunctions.spawn_target(x=self.spawn_position.x,
                                        y=self.spawn_position.y,
                                        z=self.spawn_position.z, 
                                        target_name=self.name,
                                        on_destroy=self.on_destroy)
            destroy(self)
            destroy(self.health_bar)
            self.destroyed = True
        else: #shrink health
            health_percent = max(self.health / 100, 0) #check if health is < 0, so damage bar doesnt 'flip' to negative values
            self.health_bar.scale_x = 0.7 * health_percent #set health bar to % value of whole bar

    def spawn(self):
        if not self.spawned:
            if self.x <= self.initial_move_pos:
                self.position += self.forward * time.dt * self.speed
            elif self.x > self.initial_move_pos:
                rotation = random.randrange(0, 180, 20)
                self.rotation_y += rotation
                self.spawned = True

    def move(self):
        if self.hasMovement and self.spawned:
            self.position += self.forward * time.dt * self.speed
            if (self.x >= 10 or self.x <= -10) or (self.z >= 10 or self.z <= -30):
                rotation = random.randrange(0, 180, 20)
                self.rotation_y += rotation