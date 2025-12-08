from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

class Player(FirstPersonController):
    def __init__(self):
        super().__init__(
            height = 2,
            collider = 'box',
            position=(35, 1 ,10),
            rotation=(0, 270, 0)
        )

        self.cursor.visible = True

        self.walk_sound = Audio(
            'assets\sounds\sound_walking01.mp3',
            loop=True,
            autoplay=False,
            volume=.2
        )
        
        self.jump_sound = Audio(
            'assets\sounds\sound_jump.mp3',
            loop=False,
            autoplay=False,
            volume=.2
        )
    
    def set_walking(self):
        walking = held_keys['a'] or held_keys['s'] or held_keys['d'] or held_keys['w']
        if walking:
            if not self.walk_sound.playing:
                self.walk_sound.play()
        else:
            if self.walk_sound.playing:
                self.walk_sound.stop()

    def set_jumping(self):
        jump = held_keys['space']
        if jump:
            if not self.jump_sound.playing:
                self.jump_sound.play()
        else:
            if self.jump_sound.playing:
                self.jump_sound.stop()

