# week 1
# gm1 checkpoint system and lives 7
# bh1 scrolling background 4/3 - add extension
# bh2 destroy some rock obstacles - edit tilemap then code 3
# bh3 animate lava tiles 2/3

# week 2
# gm2 moving platforms 6 place on tilemap
# bh4 sharks that swin across the screen 6
# bh5 new level 4 - make tilemap
# bh6 level save 1/2

@namespace
class SpriteKind:
    enemy_projectile = SpriteKind.create()
# gm2
    moving_platform = SpriteKind.create()
    platform_hitbox = SpriteKind.create()
# /gm2
# bh4
    floating_enemy = SpriteKind.create()
# /bh4

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
    assets.tilemap("level 4") # bh5
]
level = 4
jump_count = 2
facing_right = True

# setup
scene.set_background_image(assets.image("background"))
scroller.scroll_background_with_camera(scroller.CameraScrollMode.ONLY_HORIZONTAL)
info.set_life(3)

def animate_lava():
    for lava_tile in tiles.get_tiles_by_type(assets.tile("lava")):
        effect_sprite = sprites.create(image.create(1, 1))
        tiles.place_on_tile(effect_sprite, lava_tile)
        effect_sprite.y -= 8
        effect_sprite.start_effect(effects.bubbles)

# gm2
def make_moving_platforms():
    for moving_platform_tile in tiles.get_tiles_by_type(assets.tile("moving platform")):
        moving_platform = sprites.create(assets.tile("moving platform"), SpriteKind.moving_platform)
        tiles.place_on_tile(moving_platform, moving_platform_tile)
        tiles.set_tile_at(moving_platform_tile,image.create(16, 16))
        moving_platform.set_flag(SpriteFlag.BOUNCE_ON_WALL, True)
        moving_platform.vx = 30
        hitbox = sprites.create(image.create(16, 4), SpriteKind.platform_hitbox)
        sprites.set_data_sprite(hitbox, "platform", moving_platform)
        hitbox.image.fill(1)
        hitbox.set_flag(SpriteFlag.INVISIBLE, True)
# /gm2

# bh6
def load_save():
    global level
    if game.ask("Would you like to load your previous game?"):
        if database.exists_key("level"):
            level = database.get_number_value("level")
        else:
            game.splash("No save file found")
load_save()
# /bh6

def load_level():
    shrimp.set_velocity(0, 0)
    scene.set_tile_map_level(levels[level - 1])
    tiles.place_on_random_tile(shrimp, assets.tile("player spawn"))
    tiles.set_tile_at(shrimp.tilemap_location(), assets.tile("checkpoint collected"))
    sprites.destroy_all_sprites_of_kind(SpriteKind.enemy)
    for urchin_tile in tiles.get_tiles_by_type(assets.tile("enemy spawn")):
        urchin = sprites.create(assets.image("urchin"), SpriteKind.enemy)
        tiles.place_on_tile(urchin, urchin_tile)
        tiles.set_tile_at(urchin_tile, image.create(16, 16))
    animate_lava()
# gm2
    make_moving_platforms()
# /gm2
# bh6
    database.set_number_value("level", level)
# /bh6
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

def take_damage():
    info.change_life_by(-1)
    shrimp.set_velocity(0, 0)
    tiles.place_on_random_tile(shrimp, assets.tile("checkpoint collected"))

def hit(shrimp, spine):
    timer.throttle("take damage", 1000, take_damage)
sprites.on_overlap(SpriteKind.player, SpriteKind.enemy_projectile, hit)
# bh4
sprites.on_overlap(SpriteKind.player, SpriteKind.floating_enemy, hit)
# /bh4

def hit_lava(shrimp, location):
    timer.throttle("take damage", 1000, take_damage)
scene.on_overlap_tile(SpriteKind.player, assets.tile("lava"), hit_lava)

def reach_checkpoint(shrimp, checkpoint):
    for checkpoint_collected in tiles.get_tiles_by_type(assets.tile("checkpoint collected")):
        tiles.set_tile_at(checkpoint_collected, image.create(16, 16))
    tiles.set_tile_at(checkpoint, assets.tile("checkpoint collected"))
scene.on_overlap_tile(SpriteKind.player, assets.tile("checkpoint uncollected"), reach_checkpoint)

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
# bh4
sprites.on_overlap(SpriteKind.projectile, SpriteKind.floating_enemy, enemy_hit)
# /bh4

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

# bh4
def shark_spawn():
    shark = sprites.create(assets.image("shark"), SpriteKind.floating_enemy)
    if randint(1, 2) == 1:
        shark.image.flip_x()
        shark.right = 1
        shark.vx = 50
    else:
        shark.left = (tilesAdvanced.get_tilemap_width() * 16) - 1
        shark.vx = -50
    if spriteutils.distance_between(shark, shrimp) < 120:
        shark.destroy()
        shark_spawn
    shark.y = shrimp.y
    sprites.set_data_number(shark, "start y", shark.y)
    shark.set_flag(SpriteFlag.GHOST_THROUGH_WALLS, True)
game.on_update_interval(1000, shark_spawn)
# /bh4

# bh4
def shark_behaviour():
    for shark in sprites.all_of_kind(SpriteKind.floating_enemy):
        if shark.left > tilesAdvanced.get_tilemap_width() * 16 or shark.right < 0:
            shark.destroy()
        start_y = sprites.read_data_number(shark, "start y")
        shark.y = (Math.sin(shark.x / 20) * 20) + start_y
# /bh4

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

# gm2
def hit_moving_platform(shrimp, platform):
    if Math.abs(platform.x - shrimp.x) > Math.abs(platform.y - shrimp.y):
        shrimp.vx = 0
        while shrimp.overlaps_with(platform):
            shrimp.x -= Math.sign(platform.x - shrimp.x)
            pause(0)
    else:
        shrimp.vy = 0
        while shrimp.overlaps_with(platform):
            shrimp.y -= Math.sign(platform.y - shrimp.y)
            pause(0)
sprites.on_overlap(SpriteKind.player, SpriteKind.moving_platform, hit_moving_platform)
# /gm2

# gm2
def use_moving_platform():
    global jump_count
    for hitbox in sprites.all_of_kind(SpriteKind.platform_hitbox):
        platform = sprites.read_data_sprite(hitbox, "platform")
        hitbox.set_position(platform.x, platform.top - 2)
        if shrimp.overlaps_with(hitbox):
            jump_count = 0
            fps = 1000 / spriteutils.get_delta_time()
            shrimp.x += platform.vx / fps
            shrimp.ay = 0
            return
    shrimp.ay = 325
# /gm2

def tick():
    x_movement()
    y_movement()
# gm2
    use_moving_platform()
# /gm2
# bh4
    shark_behaviour()
# /bh4
game.on_update(tick)
