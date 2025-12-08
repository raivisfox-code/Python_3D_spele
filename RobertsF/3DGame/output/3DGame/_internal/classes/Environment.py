from ursina import *
from random import choice, uniform
from ursina.shaders import lit_with_shadows_shader

wall_height = 6
ground_size = 100
spawn_area = (ground_size - 20)

jabami_tree_path = "assets/models/jabami_tree_v3.glb"
wall_texture = 'assets/wall/brick_crosswalk_diff_2k.jpg'
sky_texture = "/assets/sky/industrial_sunset_02_puresky.jpg"
house_model_path = "/assets/models/house/house.obj"
house_collider_path = "/assets/models/house/house_collider.obj"

class Environment():
    def __init__(self):
        self.ground = Entity(
            model='plane',
            texture='grass',
            collider='mesh',
            scale=(ground_size, 1, ground_size)
        )

        self.wall_F = self.CreateWall((0, wall_height/2, ground_size/2), (ground_size, wall_height, 1), wall_texture)
        self.wall_B = self.CreateWall((0, wall_height/2, -ground_size/2), (ground_size, wall_height, 1), wall_texture)
        self.wall_R = self.CreateWall((-ground_size/2, wall_height/2, 0), (1, wall_height, ground_size), wall_texture)
        self.wall_L = self.CreateWall((ground_size/2, wall_height/2, 0), (1, wall_height, ground_size), wall_texture)
        
        for i in range(20):
            self.CreateRandomTree(r=uniform(.8, 2.5), x=uniform(25, ground_size/2-2), y=uniform(17, ground_size/2-2))
                    
        for i in range(25):
            self.CreateRandomTree(r=uniform(.8, 2.5), x=uniform(25, ground_size/2-2), y=uniform(0, -ground_size/2-2))

        self.sky = Entity(
            model='sphere',
            texture=sky_texture,
            scale=1000,
            double_sided=True,
            rotation=(0, 180, 0)
            )

        self.house = Entity(
            model=house_model_path,
            scale=.16,
            position=(ground_size/2-6, 0 ,10),
            shader=lit_with_shadows_shader,
            rotation=(0, 270, 0)
        )
        
        self.house_collider = Entity(
            parent=self.house,
            model=house_collider_path,
            collider='mesh',
            visible=False
        )
        
        self.CreateSpaceship()

    def CreateSpaceship(self):
        self.spaceship = Entity(
            model = "/assets/models/spaceship.glb",
            shader=lit_with_shadows_shader,
            scale=2,
            rotation=(0, 190, 0),
            position=(-10, -.5, -ground_size/2+15),
        )

        ship_collider = Entity(
            parent=self.spaceship,
            collider='box',
            scale=(7, 10, 5),
            rotation=(0, 30, 0),
            position=(-1, 0, 0)
        )

    def CreateWall(self, position, scale, texture):
        return Entity(
            model='cube',
            collider='box',
            position=position,
            scale=scale,
            texture=texture,
            texture_scale=(15, 2.5)
        )
    
    def CreateTree(self, position, scale, model = jabami_tree_path):
        tree = Entity(
            model=model,
            position=position,
            scale=scale,
        )
        # apply custom collider for tree trunk
        Entity(parent=tree, position=(0,0.5,0), scale=(0.3,4,0.3), collider='box')

    def CreateRandomTree(self, r, x, y, model = jabami_tree_path):
        self.CreateTree(position=(x, -.2, y), scale=(r, r, r), model=model)

    def update(self):
        self.sky.rotation_y += time.dt * 0.3
