from ursina import *
from random import choice, uniform
from ursina.shaders import lit_with_shadows_shader
from classes.GameFunctions import GameFunctions

class Target(Entity):
    def __init__(self,
                x, y, z,
                on_destroy,
                name = "cube",
                speed = None,
                initial_move_pos = None,
                hasMovement = False,
                hasGravity = True,
                model = 'cube',
                scale = (1, 2, 1)):
        super().__init__(
            name=name,
            model=model,
            parent = scene,
            scale = scale, 
            position = (x, y, z),
            collider = 'box',
            shader=lit_with_shadows_shader
        )

        self.health = 100
        self.destroyed = False
        self.spawned = False
        
        self.on_destroy = on_destroy
        self.hasMovement = hasMovement

        if self.model.name == 'cube':
            self.texture = 'white_cube'
            self.color = color.gold


        self.initial_move_pos = initial_move_pos if initial_move_pos is not None else 0
        self.speed = speed if speed is not None else 10*6

        self.hasGravity = hasGravity
        self.falling_velocity = 0
        self.gravity = -9.8

        self.health_bar = Entity(
            parent=scene,
            model='cube',
            color=color.green,
            scale=(.7, .1, .1),
            position=(self.x, self.y+2, self.z) 
        )

    def update(self):
        # update health location and direction
        self.health_bar.position = (self.x, self.y+2, self.z)
        self.set_health_display_direction()

        if self.hasGravity:
            #set gravity
            dt = time.dt
            self.falling_velocity += self.gravity * dt
            self.y += self.falling_velocity * dt

            ground_y = 0
            bottom_y = self.y - self.scale_y / 2

            if bottom_y < ground_y:
                self.y = ground_y + self.scale_y / 2
                self.falling_velocity = 0

    def set_health_display_direction(self):
        direction = camera.world_position - self.health_bar.world_position
        direction.y = 0
        self.health_bar.look_at(self.health_bar.world_position + direction)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            GameFunctions.spawn_target(x=uniform(-5, 5),
                                    y=1,
                                    z=uniform(-5, 5), 
                                    target_name=self.name,
                                    on_destroy=self.on_destroy)
            destroy(self)
            destroy(self.health_bar)
            self.destroyed = True
        else: #shrink health
            health_percent = max(self.health / 100, 0) #check if health is < 0, so damage bar doesnt 'flip' to negative values
            self.health_bar.scale_x = 0.7 * health_percent #set health bar to % value of whole bar