from ursina import *
from random import choice, uniform
from classes.Alien import Alien

class Ufo(Entity):
    def __init__(self, x, y, z, on_destroy):
        super().__init__(
            model="/assets/models/ufo.glb",
            position=(
                x,
                y,
                z),
            scale=10,
        )
        self.on_destroy = on_destroy
        self.set_beam()

        self.fly_in()

    def set_beam(self):
        self.beam = Entity(
            parent=self,
            model = Cone(resolution=64, radius=7, height=100),
            position=(0, -1, 0),
            scale=1/50,
            color=color.hex("#e2c541"),
            alpha =.3
        )

    def fly_in(self):
        x = random.uniform(-10, 10,)
        z = random.uniform(-5, 5,)

        alien_spawn_y=random.uniform(2, 3)

        self.animate_position(Vec3(x, self.y, z), duration=2, curve=curve.linear)
        self.beam.visible = True
        invoke(self.spawn_alien, x=x, y=alien_spawn_y, z=z, on_destroy=self.on_destroy, delay=2.3)


    def spawn_alien(self, x, y, z, on_destroy):
        Alien(x, y, z, on_destroy=on_destroy)
        invoke(self.fly_out, delay=.5)
    
    def fly_out(self):
        x_range = random.randrange(800, 1000, 1) * random.choice([1,-1])
        y_range = random.randrange(800, 1000, 1) * random.choice([1,-1])
        self.beam.visible = False
        self.animate_position(Vec3(x_range, self.y, y_range), duration=2, curve=curve.linear)
        invoke(destroy, self, delay=2)