from ursina import *
from random import choice, uniform

direction = 0.06
platform_scale = 3

destroyed_targets_count = 0

class GameFunctions():
    def __init__(self, player, blocks, environment, message):
        self.player = player
        self.blocks = blocks
        self.environment = environment
        self.message = message

    def moveBlocks(self):
        for block in self.blocks:
            block.x += block.direction * block.speed
            if block.x >= 10:
                block.direction = -direction
            elif block.x <= -10:
                block.direction = direction

            #check collision with block entitiy and apply movement direction to player.
            intersect_info = block.intersects()

            if intersect_info.hit and intersect_info.entity == self.player:
                self.player.x += block.speed * block.direction

    def destroyed_targets(self):
        global destroyed_targets_count
        destroyed_targets_count += 1
        self.message.text = f"Targets destroyed: {destroyed_targets_count}"

    def spawn_targets(self):
        for i in range(7):
            invoke(self.spawn_target,
                delay = i * 1.5,
                target_name="Goose",
                x=self.environment.spaceship.x,
                y=2,
                z=self.environment.spaceship.z,
                on_destroy=self.destroyed_targets)

        # for i in range(5):
        #     self.spawn_target(target_name="cube", x=uniform(-5, 5), y=1, z=uniform(-5, 5), on_destroy=self.destroyed_targets)
        
        for i in range(5):
            self.spawn_target(target_name="Alien", x=random.uniform(-5, 5), y=5, z=random.uniform(-5, 5), on_destroy=self.destroyed_targets)

        self.spawn_target(target_name="Alien", x=30, y=3 ,z=8, on_destroy=self.destroyed_targets)

    @staticmethod
    def spawn_target(x, y, z, on_destroy, target_name):
        from classes.Goose import Goose
        from classes.Alien import Alien
        from classes.Target import Target
        from classes.Ufo import Ufo
        if target_name == "Goose":
            Goose(x=x, y=y, z=z, on_destroy=on_destroy)
        elif target_name == "Alien":
            Alien(x=x, y=y, z=z, on_destroy=on_destroy)
        elif target_name == "Ufo":
            Ufo(x, y, z, on_destroy=on_destroy)
        else:
            Target(random.uniform(-5, 5), 1, random.uniform(-5, 5), on_destroy)

