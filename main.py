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

# week 3
# gm3 shrimp that patrols 9
# bh7 animate enemy dying and falling off 3
# bh8 ladder 5
# bh9 collectables - assets, tilemap, func, edit load, collect 5

@namespace
class SpriteKind:
    enemy_projectile = SpriteKind.create()
    moving_platform = SpriteKind.create()
    platform_hitbox = SpriteKind.create()
    floating_enemy = SpriteKind.create()
# gm3
    patrolling_enemy = SpriteKind.create()
# /gm3
# bh7 if you did not do bh3
    effect = SpriteKind.create()
# /bh7

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
    assets.tilemap("level 4")
]
level = 3
jump_count = 2
facing_right = True

# setup
scene.set_background_image(assets.image("background"))
scroller.scroll_background_with_camera(scroller.CameraScrollMode.ONLY_HORIZONTAL)
info.set_life(3)

def animate_lava():
    sprites.destroy_all_sprites_of_kind(SpriteKind.effect)
    for lava_tile in tiles.get_tiles_by_type(assets.tile("lava")):
        effect_sprite = sprites.create(image.create(1, 1), SpriteKind.effect)
        tiles.place_on_tile(effect_sprite, lava_tile)
        effect_sprite.y -= 8
        effect_sprite.start_effect(effects.bubbles)

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

def load_save():
    global level
    if game.ask("Would you like to load your previous game?"):
        if database.exists_key("level"):
            level = database.get_number_value("level")
        else:
            game.splash("No save file found")
load_save()

# bh9
def spawn_coins():
    sprites.destroy_all_sprites_of_kind(SpriteKind.food)
    for coin_spawn in tiles.get_tiles_by_type(assets.tile("coin spawn")):
        coin = sprites.create(assets.image("coin"), SpriteKind.food)
        tiles.place_on_tile(coin, coin_spawn)
        tiles.set_tile_at(coin_spawn, image.create(16, 16))
# /bh9

# gm3
def make_crabs():
    sprites.all_of_kind(SpriteKind.patrolling_enemy)
    for crab_spawn in tiles.get_tiles_by_type(assets.tile("enemy crab spawn")):
        crab = sprites.create(assets.image("enemy crab"), SpriteKind.patrolling_enemy)
        crab.set_flag(SpriteFlag.BOUNCE_ON_WALL, True)
        crab.vx = 50
        tiles.place_on_tile(crab, crab_spawn)
        tiles.set_tile_at(crab_spawn, image.create(16, 16))
# /gm3

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
    make_moving_platforms()
    database.set_number_value("level", level)
# gm3
    make_crabs()
# /gm3
# bh9
    spawn_coins()
# /bh9
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
# sprites.on_overlap(SpriteKind.player, SpriteKind.enemy_projectile, hit)
# sprites.on_overlap(SpriteKind.player, SpriteKind.floating_enemy, hit)
# gm3
# sprites.on_overlap(SpriteKind.player, SpriteKind.patrolling_enemy, hit)
# /gm3

# bh9
def get_coin(shrimp, coin):
    info.change_score_by(500)
    music.power_up.play()
    coin.destroy()
sprites.on_overlap(SpriteKind.player, SpriteKind.food, get_coin)
# /bh9

def hit_lava(shrimp, location):
    timer.throttle("take damage", 1000, take_damage)
scene.on_overlap_tile(SpriteKind.player, assets.tile("lava"), hit_lava)

# bh8
def use_ladder(shrimp, location):
    shrimp.vy = 0
    if controller.up.is_pressed():
        shrimp.vy = -50
    elif controller.down.is_pressed():
        shrimp.vy = 50
scene.on_overlap_tile(SpriteKind.player, assets.tile("ladder"), use_ladder)
# /bh8

def reach_checkpoint(shrimp, checkpoint):
    for checkpoint_collected in tiles.get_tiles_by_type(assets.tile("checkpoint collected")):
        tiles.set_tile_at(checkpoint_collected, image.create(16, 16))
    tiles.set_tile_at(checkpoint, assets.tile("checkpoint collected"))
scene.on_overlap_tile(SpriteKind.player, assets.tile("checkpoint uncollected"), reach_checkpoint)

def hit_wall(proj, location):
    if tiles.tile_image_at_location(location).equals(assets.tile("breakable rock")):
        tiles.set_tile_at(location, image.create(16, 16))
        tiles.set_wall_at(location, False)
        effect_sprite = sprites.create(assets.tile("breakable rock"))
        tiles.place_on_tile(effect_sprite, location)
        effect_sprite.destroy(effects.disintegrate, 500)
scene.on_hit_wall(SpriteKind.projectile, hit_wall)

def next_level():
    global level
    if level == len(levels):
        game.over(True)
    level += 1
    load_level()
scene.on_overlap_tile(SpriteKind.player, assets.tile("level end"), next_level)

# bh7
def enemy_animate(enemy: Sprite):
    enemy.image.flip_y()
    for colour in range(1, 16):
        enemy.image.replace(colour, 1)
    enemy.set_kind(SpriteKind.effect)
    enemy.set_flag(SpriteFlag.GHOST, True)
    enemy.set_flag(SpriteFlag.AUTO_DESTROY, True)
    enemy.ay = 325
    enemy.vy = -100
# /bh7

def enemy_hit(proj, enemy):
    info.change_score_by(10)
    proj.destroy()
# bh7
    # enemy.destroy()
    enemy_animate(enemy)
# /bh7
sprites.on_overlap(SpriteKind.projectile, SpriteKind.enemy, enemy_hit)
sprites.on_overlap(SpriteKind.projectile, SpriteKind.floating_enemy, enemy_hit)
# gm3
sprites.on_overlap(SpriteKind.projectile, SpriteKind.patrolling_enemy, enemy_hit)
# /gm3

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

def shark_behaviour():
    for shark in sprites.all_of_kind(SpriteKind.floating_enemy):
        if shark.left > tilesAdvanced.get_tilemap_width() * 16 or shark.right < 0:
            shark.destroy()
        start_y = sprites.read_data_number(shark, "start y")
        shark.y = (Math.sin(shark.x / 20) * 20) + start_y

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

# bh8
def check_on_ladder():
    if tiles.tile_at_location_equals(shrimp.tilemap_location(), assets.tile("ladder")):
        shrimp.ay = 0
    else:
        shrimp.ay = 325
# /bh8

# gm3
def crab_behaviour():
    if len(sprites.all_of_kind(SpriteKind.patrolling_enemy)) < 1:
        return
    for crab in sprites.all_of_kind(SpriteKind.patrolling_enemy):
        location = crab.tilemap_location()
        tile_infront = tiles.get_tile_location(location.col, location.row + 1)
        if not tiles.tile_at_location_is_wall(tile_infront):
            crab.vx *= -1
            crab.image.flip_x()
# /gm3

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

def tick():
    x_movement()
    y_movement()
    use_moving_platform()
    shark_behaviour()

# gm3
    crab_behaviour()
# /gm3
# bh8
    check_on_ladder()
# /bh8
game.on_update(tick)
