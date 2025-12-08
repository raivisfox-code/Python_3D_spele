from ursina.prefabs.health_bar import HealthBar
import random
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math


app = Ursina()
ammo_pickups = []
shootables_parent = Entity()


# Configuration
WALL_HEIGHT = 8
GROUND_SIZE = 100
WALL_TEXTURE = 'Bricks052_2K-JPG/Bricks052_2K-JPG_Color.jpg'
PLAYER_SPEED = 20
BLOCK_UPDATE_DISTANCE = 50

random.seed(0)
window.vsync = True

# =====================================================
# PLAYER
# =====================================================
player = FirstPersonController(speed=PLAYER_SPEED, position=(0, 0, -30))
player.cursor.visible = True

# ======================================================
#  DAMAGE FLOATING TEXT
# ======================================================


class DamageText(Text):
    def __init__(self, value, position):
        super().__init__(
            text=f"-{value}",
            color=color.red,
            position=position,
            scale=2,  # smaller scale
            origin=(0, 0),  # center origin
            world_parent=scene
        )
        self.animate_position(self.position + Vec3(0, 1, 0), duration=1)
        self.fade_out(duration=1)
        destroy(self, delay=1.1)


# ======================================================
#  GUN CLASS
# ======================================================
class Gun(Entity):

    def __init__(self, **kwargs):
        super().__init__(
            parent=camera,
            model='cartoon_rifle.glb',
            position=(.1, -.60, .20),
            rotation=(-8, -10, 0),
            scale=.1,
            color=color.gold,
            flip_faces=True,
            **kwargs
        )
        # === Shooting system ===
        self.on_cooldown = False
        self.cooldown_time = 0.12
        self.recoil_amount = 4

        self.mag_size = 30        # bullets per mag
        self.mag = self.mag_size  # current mag
        self.reserve = 120        # bullets left in inventory
        self.reloading = False

        self._orig_rotation_z = self.rotation_z

        # Barrel offset
        self.barrel_offset = Vec3(1.5, 3.7, 5.5)

        # Replace quad with .glb muzzle flash
        self.muzzle_flash = Entity(
            parent=self,
            model='muzzle_meshes.glb',  # .glb file here
            color=color.yellow,
            scale=0.001,                # adjust scale as needed
            enabled=False,
            position=self.barrel_offset
        )

        self.gunshot = Audio('single-gunshot-54-40780.mp3',
                             volume=0.8, autoplay=False)

    def _reload_animation_return(self):
        # return to normal position + rotation
        self.animate_position(
            self.position - Vec3(0, 0.35, -0.1), duration=0.15, curve=curve.in_out_quad)
        self.animate_rotation(self.rotation - Vec3(-10, 0, 5),
                              duration=0.15, curve=curve.in_out_quad)

    # ---------------------------
    # RELOAD
    # ---------------------------

    def reload(self):
        if self.reloading:
            return
        if self.mag == self.mag_size:
            return
        if self.reserve <= 0:
            return

        self.reloading = True
        reload_sound.play()

        # --- RELOAD ANIMATION ---
    # Move gun Up + tilt
        self.animate_position(
            self.position + Vec3(0, 0.35, -0.1), duration=0.18, curve=curve.in_out_quad)
        self.animate_rotation(self.rotation + Vec3(-10, 0, 5),
                              duration=0.18, curve=curve.in_out_quad)

    # After animation → return gun to original pose
        # timing matches reload time
        invoke(self._reload_animation_return, delay=2)

    # Finish reload logic
        invoke(self._finish_reload, delay=1.2)

        # Delay to simulate reload animation (1.2 sec)
        invoke(self._finish_reload, delay=1.2)

    def _finish_reload(self):
        missing = self.mag_size - self.mag
        to_load = min(missing, self.reserve)

        self.mag += to_load
        self.reserve -= to_load

        self.reloading = False
        update_ammo_ui()

    # ---------------------------
    # SHOOT
    # ---------------------------
    def shoot(self):
        if self.reloading:
            return

        if self.mag <= 0:
            empty_click.play()
            print("Out of ammo! Press 'R' to reload.")
            return

        if self.on_cooldown:
            return

        # consume ammo
        self.mag -= 1
        update_ammo_ui()

        self.on_cooldown = True

        # sound
        try:
            self.gunshot.play()
        except:
            pass

        # Flash
        self.muzzle_flash.enabled = True
        invoke(self.muzzle_flash.disable, delay=0.05)

        # recoil
        self.rotation_z += random.uniform(-self.recoil_amount,
                                          self.recoil_amount)
        invoke(lambda: setattr(self, 'rotation_z',
               self._orig_rotation_z), delay=0.1)

        # Raycast
        barrel_world = self.world_position + self.up * \
            self.barrel_offset.y + self.forward * self.barrel_offset.z
        hit = raycast(camera.world_position, camera.forward,
                      distance=200, ignore=(player, self))

        if hit.hit and hasattr(hit.entity, "hp"):
            hit.entity.hp -= 10

        invoke(self._reset_cooldown, delay=self.cooldown_time)

    def _reset_cooldown(self):
        self.on_cooldown = False

    def add_ammo(self, amount):
        self.reserve += amount
        pickup_sound.play()
        update_ammo_ui()
        print(f"Picked up {amount} ammo! Reserve = {self.reserve}")


# ======================================================
#  WORLD ENTITIES
# ======================================================
shootables_parent = Entity()
mouse.traverse_target = shootables_parent

# --- Ammo ---


def update_ammo_ui():
    ammo_text.text = f"{gun.mag} / {gun.reserve}"


# --- Gun / Ammo Sounds ---
empty_click = Audio('empty_bullet.mp3', volume=5, autoplay=False)
reload_sound = Audio('mag-reload-81594.mp3', volume=5, autoplay=False)
pickup_sound = Audio('take-it-90781.mp3', autoplay=False, volume=1)

# --- Player Sounds ---
walk = Audio('walking-sound-effect.mp3', volume=1, autoplay=False, loop=False)
jump_sound = Audio('jumplanding.mp3', volume=1, autoplay=False, loop=False)
hit_sound = Audio('080998_bullet-hit-39870.mp3',
                  volume=0.6, autoplay=False, loop=False)
pickup_sound = Audio('take-it-90781.mp3', autoplay=False, volume=1)


# --- Ground ---
ground = Entity(
    model='plane',
    texture='Grass008_2K-JPG/Grass008_2K-JPG_Color.jpg',
    collider='mesh',
    scale=(GROUND_SIZE, 1, GROUND_SIZE),
    texture_scale=(GROUND_SIZE/5, GROUND_SIZE/5)
)

# --- Car ---
car = Entity(
    model='transformers_rotf_psp_ratchet.glb',
    position=(-40, 0.3, -16),
    rotation=(0, 88, 0),
    collider='box',
    scale=(1, .9, 1)
)
# --- Text ---
msg = Text(
    scale=2,
    position=(-0.9, 0.5)
)
ammo_text = Text(
    text="30 / 120",
    scale=2,
    position=(0.72, -0.45),   # lower-right
    origin=(0, 0),
    color=color.white
)
player_hp_text = Text(
    text="HP: 100",
    origin=(0, 0),
    position=(0.70, 0.45),
    scale=2,
    color=color.red
)
# --- Trees ---
trees = []
for pos in [(39, 0, 39), (-39, 0, -39), (39, 0, -39), (-39, 0, 39)]:
    trees.append(Entity(
        model='linden_tree.glb',
        position=pos,
        scale=(3, 2, 3),
        collider=None
    ))
trees = []
for pos in [(25, 0, 43), (-23, 0, -43), (20, 0, -43), (-22, 0, 43)]:
    trees.append(Entity(
        model='spruce_trees.glb',
        position=pos,
        scale=(.4, .4, .4),
        collider=None
    ))
trees = []
for pos in [(21, 0, 25), (-18, 0, -33), (15, 0, -33), (-18, 0, 33)]:
    trees.append(Entity(
        model='blue_spruce_tree.glb',
        position=pos,
        scale=(1, 1, 1),
        collider=None
    ))
trees = []
for pos in [(-48, 0, -9), (-33, 0, -33), (-42, 0, -9), (-38, 0, -9), (-34, 0, -9)]:
    trees.append(Entity(
        model='real_bush.glb',
        position=pos,
        scale=(.03, .02, .03),
        collider=None
    ))
trees = []
for pos in [(-44, 0, 12), (-35, 0, -4), (-40, 0, 4), (-25, 0, 6), (-25, 0, 20)]:
    trees.append(Entity(
        model='pine_tree.glb',
        position=pos,
        scale=(5, 4, 5),
        collider=None
    ))
trees = []
for pos in [(-44, 0, -4), (-44, 0, 20), (-32, 0, 12), (-35, 0, 20), (-25, 0, -7)]:
    trees.append(Entity(
        model='birch_tree.glb',
        position=pos,
        scale=(3, 2, 3),
        collider=None
    ))


house = Entity(
    model='wooden_cottage_house_psx.glb',
    position=(-30, 0, -26),
    collider=None,
    scale=(70, 50, 70)
)

# --- Moving Blocks ---
blocks = []
block_dirs = []

for i in range(9):
    b = Entity(
        model='cube',
        position=(8, 1 + i, 8 + 5 * i),
        texture='painted_concrete_diff_2k.jpg',
        collider='box',
        scale=(5, 0.5, 5)
    )
    blocks.append(b)

    # block movement direction (left/right)
    block_dirs.append(random.uniform(-0.03, 0.03))

# --- Walls ---
half = GROUND_SIZE / 2
wall_thickness = 1
walls = [
    Entity(model='cube', position=(0, WALL_HEIGHT/2, -half),
           scale=(GROUND_SIZE, WALL_HEIGHT, wall_thickness),
           collider='box', texture=WALL_TEXTURE, texture_scale=(30, 2.5)),
    Entity(model='cube', position=(0, WALL_HEIGHT/2, half),
           scale=(GROUND_SIZE, WALL_HEIGHT, wall_thickness),
           collider='box', texture=WALL_TEXTURE, texture_scale=(30, 2.5)),
    Entity(model='cube', position=(-half, WALL_HEIGHT/2, 0),
           scale=(wall_thickness, WALL_HEIGHT, GROUND_SIZE),
           collider='box', texture=WALL_TEXTURE, texture_scale=(30, 2.5)),
    Entity(model='cube', position=(half, WALL_HEIGHT/2, 0),
           scale=(wall_thickness, WALL_HEIGHT, GROUND_SIZE),
           collider='box', texture=WALL_TEXTURE, texture_scale=(30, 2.5))
]

# --- Extra Blocks ---
for i in range(25):
    Entity(
        model='cube',
        origin_y=-.4,
        scale=2,
        texture='brick',
        texture_scale=(3, 4),
        x=random.uniform(-16, 35),
        z=random.uniform(-13, 35) - 30,
        collider='box',
        scale_y=random.uniform(3, 4),
        color=color.hsv(0, 0, random.uniform(.9, 1))
    )

player = FirstPersonController(speed=PLAYER_SPEED, position=(0, 0, -30))
player.cursor.visible = True
editor_camera = EditorCamera(enabled=False, ignore_paused=True)

# --- Skybox ---
skybox = Entity(
    model='sphere',
    texture='NightSkyHDRI008_4K/NightSkyHDRI008_4K_TONEMAPPED.jpg',
    scale=1000,
    double_sided=True,
    rotation=(0, 180, 0)
)

gun = Gun()

was_on_ground = player.grounded

# ======================================================
#  ENEMY CLASS
# ======================================================


class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=shootables_parent,
            model='egg_drone.glb',
            scale_y=1,
            origin_y=-2,
            color=color.light_gray,
            scale=(1, 1, 1),
            collider='box',
            **kwargs
        )

        self.collider = BoxCollider(
            self, center=Vec3(0, 1, 0), size=Vec3(1, 2, 1))

        self.health_bar = Entity(
            parent=self,
            y=3,
            model='cube',
            color=color.red,
            world_scale=(.1, .1, .1)
        )

        self.max_hp = 100
        self._hp = self.max_hp
        self.hp = self.max_hp

        self.destroyed = False
        self.attack_cooldown = 0

    def update(self):
        if self.destroyed:
            return

        dist = distance(self.position, player.position)

        # --- SAFE MOVE ---
        if dist > 1.4:
            self.look_at_2d(player.position, axis='y')
            self.position += self.forward * time.dt * 1.3
        else:
            self.look_at_2d(player.position, axis='y')

        # --- SAFE ATTACK ---
        if dist < 1.4:
            if self.attack_cooldown <= 0:
                player.hp -= 10
                update_player_hp()
                hit_sound.play()
                self.attack_cooldown = 1
            else:
                self.attack_cooldown -= time.dt

        # ALWAYS update HP bar
        self.health_bar.world_scale_x = (self.hp / self.max_hp) * 1.5

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        damage = self._hp - value
        self._hp = value

        if damage > 0:
            DamageText(damage, self.world_position + Vec3(0, 2.5, 0))
            original_color = self.color
            self.color = color.white
            hit_sound.play()
            invoke(lambda: setattr(self, 'color', original_color), delay=0.1)

        if value <= 0:
            self.destroyed = True
            self.collider = None
            self.enabled = False
            destroy(self, delay=.05)

        self.health_bar.world_scale_x = (self.hp / self.max_hp) * 1.5
        self.health_bar.alpha = 1


# Spawn Enemies
enemies = [Enemy(position=(x * -5, 0, 46)) for x in range(4)]
random.shuffle(enemies)


# ======================================================
class AmmoBox(Entity):
    def __init__(self, amount=120, **kwargs):
        super().__init__(
            model='ammo_box_-_game_asset.glb',
            color=color.white,
            scale=1,
            collider='box',
            parent=scene,
            **kwargs
        )
        self.amount = amount


# Spawn Ammo Boxes
b = AmmoBox(position=(49, 8, 50))
a = AmmoBox(position=(-49, 8, 50))
ammo_pickups.append(b)
ammo_pickups.append(a)


# ======================================================
#  UPDATE LOOP
# ======================================================
def drop_ammo(position):
    box = AmmoBox(position=position + Vec3(0, 0.5, 0), amount=120)
    ammo_pickups.append(box)


def update():
    # ---- Check Ammo PICKUP ----
    for box in ammo_pickups[:]:    # copy list for safe removal
        if distance(player.position, box.position) < 2:
            gun.add_ammo(box.amount)
            destroy(box)
            ammo_pickups.remove(box)
            pickup_sound.play()

    for i, block in enumerate(blocks):

        # --- Move block ---
        block.x += block_dirs[i]

        # reverse direction at limits
        if block.x > 5:
            block_dirs[i] = -abs(block_dirs[i])
        if block.x < -5:
            block_dirs[i] = abs(block_dirs[i])

        # --- Check if player is standing on block ---
        on_top = (
            abs(player.x - block.x) < block.scale_x/2 and
            abs(player.z - block.z) < block.scale_z/2 and
            abs(player.y - (block.y + 0.3)) < 0.4
        )

        if on_top and player.grounded:
            # move player together with block
            player.x += block_dirs[i]

    msg.text = f"Youre position is: x = {int(player.x)}, y = {int(player.y)}, z = {int(player.z)}"

    # Walking sound
    walking = held_keys['a'] or held_keys['d'] or held_keys['w'] or held_keys['s']
    if walking and player.grounded and not walk.playing:
        walk.play()
    elif (not walking or not player.grounded) and walk.playing:
        walk.stop()

    if player.grounded and not was_on_ground:
        jump_sound.play()

    # Shooting
    if held_keys['left mouse'] and not gun.reloading:
        gun.shoot()


# --- Player HP System ---
player.max_hp = 100
player.hp = 100


def update_player_hp():
    player_hp_text.text = f"HP: {int(player.hp)}"


# --- Player HP System ---
player.max_hp = 100
player.hp = 100


def update_player_hp():
    player_hp_text.text = f"HP: {int(player.hp)}"
    if player.hp <= 0:
        player.hp = 0
        Text("YOU DIED", scale=5, color=color.red, origin=(0, 0))
        application.pause()
        destroy(player)


#  PAUSE
# ======================================================


def pause_input(key):
    if key == 'tab':
        editor_camera.enabled = not editor_camera.enabled
        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused = editor_camera.enabled


pause_handler = Entity(ignore_paused=True, input=pause_input)


def input(key):
    if key == 'escape':
        quit()

    if key == 'r':
        gun.reload()


app.run()
