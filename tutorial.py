
import os
import random
import math

from os import listdir
from os.path import isfile, join
import random

from playerclass import Player
from gameobjs import Object, Block, Fire

import Physics 

phy = Physics.physics()

# print(phy)

phy.init()
phy.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5


window = phy.display.set_mode((WIDTH, HEIGHT))
font = phy.font.Font(None, 36)



# def generate_terrain(start_x, end_x, terrain_assets, spike_assets):
#     terrain_types = list(terrain_assets.keys())
#     spike_types = list(spike_assets.keys())

#     terrain = []
#     spikelist= []
#     block_size = 96
#     for x in range(-WIDTH // block_size, (WIDTH * 2) // block_size, 96): # Assuming each terrain piece is 96 pixels wide
#         # Randomly select a terrain type
#         terrain_type = random.choice(terrain_types)
#         # terrain_sprite = random.choice(terrain_assets[terrain_type])

#         # Randomly add a spike
        
    
#         block = Block(x, HEIGHT - 96, 96)
#         # block.image.blit(terrain_sprite, (0, 0))
#         # block.mask = phy.mask.from_surface(block.image)
#         terrain.append(block)

#         print(spikelist)

#     return (terrain, spikelist)

def flip(sprites):
    return [phy.transform.flip(sprite, True, False) for sprite in sprites]
 

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = phy.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = phy.Surface((width, height), phy.SRCALPHA, 32)
            rect = phy.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(phy.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

# Assuming you have terrain and spike assets in the "assets" directory



def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = phy.image.load(path).convert_alpha()
    surface = phy.Surface((size, size), phy.SRCALPHA, 32)
    rect = phy.Rect(96, 128, size, size)
    surface.blit(image, (0, 0), rect)
    return phy.transform.scale2x(surface)



def get_custom_block(size, offset=0):
    path = join("assets", "Terrain", "Terrain.png")
    image = phy.image.load(path).convert_alpha()
    surface = phy.Surface((size, size), phy.SRCALPHA, 32)
    rect = phy.Rect(96, 64*offset, size, size)
    surface.blit(image, (0, 0), rect)
    return phy.transform.scale2x(surface)


def get_ice_block(size, offset):
    path = join("assets", "Traps", "Sand Mud Ice" , "sandmudice.png")
    image = phy.image.load(path).convert_alpha()
    surface = phy.Surface((size, size), phy.SRCALPHA, 32)
    rect = phy.Rect( 64* offset, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return phy.transform.scale2x(surface)

class Player(phy.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = phy.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.hp = 100


    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = phy.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
    
    def slide(self):
        
        self.move(self.x_vel, 0)    


class Object(phy.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = phy.Rect(x, y, width, height)
        self.image = phy.Surface((width, height), phy.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

   


class Block(Object):
    def __init__(self, x, y, size, offset):
        super().__init__(x, y, size, size)
        offset = random.randint(0, 2)
        block = get_custom_block(size, offset)
        self.image.blit(block, (0, 0))
        self.mask = phy.mask.from_surface(self.image)

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))




class IceBlock(Object):
    def __init__(self, x, y, size, offset):
        super().__init__(x, y, size, size)
        offset = 2
        block = get_ice_block(size, offset)
        self.image.blit(block, (0, 0))
        self.mask = phy.mask.from_surface(self.image)

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class SandBlock(Object):
    def __init__(self, x, y, size, offset):
        super().__init__(x, y, size, size)
        offset = 1
        block = get_custom_block(size, offset)
        self.image.blit(block, (0, 0))
        self.mask = phy.mask.from_surface(self.image)

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))



class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = phy.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = phy.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = phy.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    
    start_block_y = HEIGHT - 96 * 2 # Place the start block directly above the first block
    end_block_x = (WIDTH * 2) - 96 # Place the end block at the end of the floor sequence
    end_block_y = HEIGHT - 96

    hp_text = font.render(f"HP: {player.hp}", True, (255, 255, 255)) # Create the text surface
    window.blit(hp_text, (10, 10))

    phy.draw.rect(window, (255, 0, 0), (start_block_y, end_block_x, 96, 96)) # Draw the start block
    phy.draw.rect(window, (255, 0, 0), (end_block_x, end_block_y, 96, 96)) # Draw the end block

     
    phy.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if phy.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
                
            if obj and obj.name == "IceBlock":
                print("This is working")
                player.landed()
                player.slide()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()


            collided_objects.append(obj)

    return collided_objects


def handle_block_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if phy.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects



def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if phy.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = phy.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)
 
    if keys[phy.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[phy.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)


    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    
    to_check = [collide_left, collide_right, *vertical_collide]




    for obj in to_check:

        if obj and obj.name == "fire":
            player.make_hit()
            player.hp -= 0.5
            if player.hp <= 0:
                print("Player has died!")
                exit(1)

        if obj and obj.name == "spike":
            player.make_hit()
            player.hp -= 0.5
            if player.hp <= 0:
                print("Player has died!")
                exit(1)
        if obj and obj.name == "IceBlock":
            # Prevent increasing x_vel beyond a certain limit
            player.landed()
            player.x_vel = min(player.x_vel, 2) # Adjust the limit as needed
            # Temporarily disable jumping by not allowing the jump action to be processed
            if keys[phy.K_SPACE]:
                keys[phy.K_SPACE] = False # This prevents the jump action from being processed

        if obj and obj.name == "SandBlock":
            # Reduce x_vel to simulate walking on sand
            player.x_vel *= 0.5 # Reduce by 50%



class Spike(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, "spike")
        self.image = phy.image.load(join("assets", "Traps", "Spike_Head", "Idle.png")).convert_alpha()
        if self.image is None:
            print("Spike image not loaded")
        self.mask = phy.mask.from_surface(self.image)    
        self.blink_timer = 0
        self.blink_state = True


    def update(self):
        self.mask = phy.mask.from_surface(self.image)
        self.blink_timer += 1
        if self.image is not None:
            self.mask = phy.mask.from_surface(self.image)
        else:
            print("Image not loaded for object")
        if self.blink_timer > 30: 
            self.blink_state = not self.blink_state
            self.blink_timer = 0
        if not self.blink_state:
            self.image.fill((0, 0, 0, 0)) # Make the spike invisible
        else:
            self.image.fill((255, 255, 255, 255)) # Make the spike visible
        self.mask = phy.mask.from_surface(self.image)
    
def main(window):
    # TERRAIN_ASSETS = load_sprite_sheets("Terrain", "", 96, 96)
    # SPIKE_ASSETS = load_sprite_sheets("Traps", "Saw", 96, 96)
    # SPIKE_ASSETS = load_sprite_sheets("Traps", "Spike_Head", 96, 96)


    clock = phy.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(100, 100, 50, 50)

     
    distance = random.randint(1, 10) * 100

    fire = [Fire(i * random.randrange(0,8), HEIGHT - block_size - 64, 16, 32) for i in range(100, WIDTH * 8, 100)]
    
    

    for fires in fire:
        fires.on()
    floor = []
    x = 0
    for i in range(-WIDTH // block_size, (WIDTH * 8) // block_size):
        # Create a block at the current x position
        # block = Block(x, HEIGHT - block_size, block_size, 0)
        
        # Add the block to the floor array
        # floor.append(block)
        
        # Increment x by block_size for the next block

        # Generate a random number to decide if the block should be a different type
        random_block = random.random()

        # If the random number is less than or equal to 0.2, create a different type of block
        if random_block <= 0.5:
            # Create a new block of a different type and add it to the floor array
            block = IceBlock(x, HEIGHT - block_size, block_size, 1)
            floor.append(block)
            x += block_size
        else:
            # Create a new block of a different type and add it to the floor array
            block = SandBlock(x, HEIGHT - block_size, block_size, 2)
            floor.append(block)
            x += block_size
        
    
    print(floor)
    # floor2, spikes = generate_terrain(-WIDTH // 96, (WIDTH * 2) // 96, TERRAIN_ASSETS, SPIKE_ASSETS)

    # print(floor2, spikes)

    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size, 0),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size, 0), *fire]

    print(objects)

    
    spikes = []

    # Spike(i * x, HEIGHT - block_size + 10, block_size) for i in range(-WIDTH // block_size, (WIDTH * 2) // 48)


    for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size):
        x = random.randint(1, 10) * 100

        spike = Spike(i * x, HEIGHT - block_size - 100, block_size * 100)
        spikes.append(spike)

    objects.extend(spikes)

    if player.hp <= 0:
        print("Player has died!")
    # In your game loop, after handling player movement, check for collisions with spikes

            

    
    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:

        clock.tick(FPS)

       
        
        for event in phy.event.get():
            if event.type == phy.QUIT:
                run = False
                break

            if event.type == phy.KEYDOWN:
                if event.key == phy.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        for fires in fire:
            fires.loop()


        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)


        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    phy.quit()
    quit()


if __name__ == "__main__":
    main(window)
