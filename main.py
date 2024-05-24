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
scene.set_background_color(6)

def load_level():
    shrimp.set_velocity(0, 0)
    scene.set_tile_map_level(levels[level - 1])
    tiles.place_on_random_tile(shrimp, assets.tile("player spawn"))
    for urchin_tile in tiles.get_tiles_by_type(assets.tile("enemy spawn")):
        urchin = sprites.create(assets.image("urchin"), SpriteKind.enemy)
        tiles.place_on_tile(urchin, urchin_tile)
        tiles.set_tile_at(urchin_tile, image.create(16, 16))
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

def hit(shrimp, spine):
    game.over(False)
sprites.on_overlap(SpriteKind.player, SpriteKind.enemy_projectile, hit)

def hit_lava(shrimp, location):
    game.over(False)
scene.on_overlap_tile(SpriteKind.player, assets.tile("lava"), hit_lava)

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
