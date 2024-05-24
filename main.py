# week 1
# gm1 checkpoint system and lives 7
# bh1 scrolling background 4/3 - add extension
# bh2 destroy some rock obstacles - edit tilemap then code 3
# bh3 animate lava tiles 2/3

@namespace
class SpriteKind:
    enemy_projectile = SpriteKind.create()

# sprites
shrimp = sprites.create(assets.image("shrimp right"), SpriteKind.player)
shrimp.ay = 325
scene.camera_follow_sprite(shrimp)
characterAnimations.run_frames(shrimp, [assets.image("shrimp right")], 1, characterAnimations.rule(Predicate.FACING_RIGHT))
characterAnimations.run_frames(shrimp, [assets.image("shrimp left")], 1, characterAnimations.rule(Predicate.FACING_LEFT))

# variables
levels = [
    assets.tilemap("level 1"),
    assets.tilemap("level 2"),
    assets.tilemap("level 3"),
]
level = 2
gravity = 8
jump_count = 2
facing_right = True

# setup
# bh1
# scene.set_background_color(6) # comment out
scene.set_background_image(assets.image("background"))
scroller.scroll_background_with_camera(scroller.CameraScrollMode.ONLY_HORIZONTAL)
# /bh1
# gm1
info.set_life(3)
# /gm1

# bh3
def animate_lava():
    for lava_tile in tiles.get_tiles_by_type(assets.tile("lava")):
        effect_sprite = sprites.create(image.create(1, 1))
        tiles.place_on_tile(effect_sprite, lava_tile)
        effect_sprite.y -= 8
        effect_sprite.start_effect(effects.bubbles)
# /bh3

def load_level():
    shrimp.set_velocity(0, 0)
    scene.set_tile_map_level(levels[level - 1])
    tiles.place_on_random_tile(shrimp, assets.tile("player spawn"))
# gm1
    # tiles.set_tile_at(shrimp.tilemap_location(), image.create(16, 16)) # remove
    tiles.set_tile_at(shrimp.tilemap_location(), assets.tile("checkpoint collected"))
# /gm1
    for urchin_tile in tiles.get_tiles_by_type(assets.tile("enemy spawn")):
        urchin = sprites.create(assets.image("urchin"), SpriteKind.enemy)
        tiles.place_on_tile(urchin, urchin_tile)
        tiles.set_tile_at(urchin_tile, image.create(16, 16))
# bh3
    animate_lava()
# /bh3
load_level()

def player_fire():
    proj = sprites.create_projectile_from_sprite(assets.image("shockwave"), shrimp, 0, 0)
    proj.scale = 0.5
    if facing_right:
        proj.vx = 200
        animation.run_image_animation(shrimp, assets.animation("attack right"), 100, False)
    else:
        proj.vx = -200
        proj.image.flip_x()
        animation.run_image_animation(shrimp, assets.animation("attack left"), 100, False)

def throttle_fire():
    timer.throttle("player fire", 300, player_fire)
controller.A.on_event(ControllerButtonEvent.PRESSED, throttle_fire)

def jump():
    global jump_count
    if jump_count < 1:
        shrimp.vy = -155
        jump_count += 1
controller.up.on_event(ControllerButtonEvent.PRESSED, jump)

# gm1
def take_damage():
    info.change_life_by(-1)
    shrimp.set_velocity(0, 0)
    tiles.place_on_random_tile(shrimp, assets.tile("checkpoint collected"))
# /gm1

def hit(shrimp, spine):
# gm1
    # game.over(False) # remove
    timer.throttle("take damage", 1000, take_damage)
# /gm1
# sprites.on_overlap(SpriteKind.player, SpriteKind.enemy_projectile, hit)

def hit_lava(shrimp, location):
# gm1
    # game.over(False) # remove
    timer.throttle("take damage", 1000, take_damage)
# /gm1
scene.on_overlap_tile(SpriteKind.player, assets.tile("lava"), hit_lava)

# gm1
def reach_checkpoint(shrimp, checkpoint):
    for checkpoint_collected in tiles.get_tiles_by_type(assets.tile("checkpoint collected")):
        tiles.set_tile_at(checkpoint_collected, image.create(16, 16))
    tiles.set_tile_at(checkpoint, assets.tile("checkpoint collected"))
scene.on_overlap_tile(SpriteKind.player, assets.tile("checkpoint uncollected"), reach_checkpoint)
# /gm1

# bh2
def hit_wall(proj, location):
    if tiles.tile_image_at_location(location).equals(assets.tile("breakable rock")):
        tiles.set_tile_at(location, image.create(16, 16))
        tiles.set_wall_at(location, False)
        effect_sprite = sprites.create(assets.tile("breakable rock"))
        tiles.place_on_tile(effect_sprite, location)
        effect_sprite.destroy(effects.disintegrate, 500)
scene.on_hit_wall(SpriteKind.projectile, hit_wall)
# /bh2

def next_level():
    global level
    if level == len(levels):
        game.over(True)
    level += 1
    load_level()
scene.on_overlap_tile(SpriteKind.player, assets.tile("level end"), next_level)

def enemy_hit(proj, enemy):
    info.change_score_by(10)
    proj.destroy()
    enemy.destroy()
sprites.on_overlap(SpriteKind.projectile, SpriteKind.enemy, enemy_hit)

def urchin_fire(urchin):
    for vx in range(-100, 101, 100):
        for vy in range(-100, 101, 100):
            if vx != 0 or vy != 0:
                spine = sprites.create_projectile_from_sprite(assets.image("spine"), urchin, vx, vy)
                spine.set_kind(SpriteKind.enemy_projectile)
                angle = spriteutils.radians_to_degrees(spriteutils.heading(spine) )
                transformSprites.rotate_sprite(spine, angle)

def urchin_behaviour():
    for urchin in sprites.all_of_kind(SpriteKind.enemy):
        urchin_fire(urchin)
game.on_update_interval(3000, urchin_behaviour)

def x_movement():
    global facing_right
    if controller.left.is_pressed():
        shrimp.vx -= 8
        facing_right = False
    elif controller.right.is_pressed():
        shrimp.vx += 8
        facing_right = True
    shrimp.vx *= 0.9

def y_movement():
    global jump_count
    if shrimp.is_hitting_tile(CollisionDirection.BOTTOM):
        jump_count = 0

def tick():
    x_movement()
    y_movement()
game.on_update(tick)
