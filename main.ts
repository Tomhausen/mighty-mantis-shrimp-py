//  week 1
//  gm1 checkpoint system and lives 7
//  bh1 scrolling background 4/3 - add extension
//  bh2 destroy some rock obstacles - edit tilemap then code 3
//  bh3 animate lava tiles 2/3
//  week 2
//  gm2 moving platforms 6 place on tilemap
//  bh4 sharks that swin across the screen 6
//  bh5 new level 4 - make tilemap
//  bh6 level save 1/2
//  week 3
//  gm3 shrimp that patrols 9
//  bh7 animate enemy dying and falling off 3
//  bh8 ladder 5
//  bh9 collectables - assets, tilemap, func, edit load, collect 5
namespace SpriteKind {
    export const enemy_projectile = SpriteKind.create()
    export const moving_platform = SpriteKind.create()
    export const platform_hitbox = SpriteKind.create()
    export const floating_enemy = SpriteKind.create()
    //  gm3
    export const patrolling_enemy = SpriteKind.create()
    //  /gm3
    //  bh7 if you did not do bh3
    export const effect = SpriteKind.create()
}

//  /bh7
//  sprites
let shrimp = sprites.create(assets.image`shrimp right`, SpriteKind.Player)
shrimp.ay = 325
scene.cameraFollowSprite(shrimp)
characterAnimations.runFrames(shrimp, [assets.image`shrimp right`], 1, characterAnimations.rule(Predicate.FacingRight))
characterAnimations.runFrames(shrimp, [assets.image`shrimp left`], 1, characterAnimations.rule(Predicate.FacingLeft))
//  variables
let levels = [assets.tilemap`level 1`, assets.tilemap`level 2`, assets.tilemap`level 3`, assets.tilemap`level 4`]
let level = 3
let jump_count = 2
let facing_right = true
//  setup
scene.setBackgroundImage(assets.image`background`)
scroller.scrollBackgroundWithCamera(scroller.CameraScrollMode.OnlyHorizontal)
info.setLife(3)
function animate_lava() {
    let effect_sprite: Sprite;
    sprites.destroyAllSpritesOfKind(SpriteKind.effect)
    for (let lava_tile of tiles.getTilesByType(assets.tile`lava`)) {
        effect_sprite = sprites.create(image.create(1, 1), SpriteKind.effect)
        tiles.placeOnTile(effect_sprite, lava_tile)
        effect_sprite.y -= 8
        effect_sprite.startEffect(effects.bubbles)
    }
}

function make_moving_platforms() {
    let moving_platform: Sprite;
    let hitbox: Sprite;
    for (let moving_platform_tile of tiles.getTilesByType(assets.tile`moving platform`)) {
        moving_platform = sprites.create(assets.tile`moving platform`, SpriteKind.moving_platform)
        tiles.placeOnTile(moving_platform, moving_platform_tile)
        tiles.setTileAt(moving_platform_tile, image.create(16, 16))
        moving_platform.setFlag(SpriteFlag.BounceOnWall, true)
        moving_platform.vx = 30
        hitbox = sprites.create(image.create(16, 4), SpriteKind.platform_hitbox)
        sprites.setDataSprite(hitbox, "platform", moving_platform)
        hitbox.image.fill(1)
        hitbox.setFlag(SpriteFlag.Invisible, true)
    }
}

function load_save() {
    
    if (game.ask("Would you like to load your previous game?")) {
        if (database.existsKey("level")) {
            level = database.getNumberValue("level")
        } else {
            game.splash("No save file found")
        }
        
    }
    
}

load_save()
//  bh9
function spawn_coins() {
    let coin: Sprite;
    sprites.destroyAllSpritesOfKind(SpriteKind.Food)
    for (let coin_spawn of tiles.getTilesByType(assets.tile`coin spawn`)) {
        coin = sprites.create(assets.image`coin`, SpriteKind.Food)
        tiles.placeOnTile(coin, coin_spawn)
        tiles.setTileAt(coin_spawn, image.create(16, 16))
    }
}

//  /bh9
//  gm3
function make_crabs() {
    let crab: Sprite;
    sprites.allOfKind(SpriteKind.patrolling_enemy)
    for (let crab_spawn of tiles.getTilesByType(assets.tile`enemy crab spawn`)) {
        crab = sprites.create(assets.image`enemy crab`, SpriteKind.patrolling_enemy)
        crab.setFlag(SpriteFlag.BounceOnWall, true)
        crab.vx = 50
        tiles.placeOnTile(crab, crab_spawn)
        tiles.setTileAt(crab_spawn, image.create(16, 16))
    }
}

//  /gm3
function load_level() {
    let urchin: Sprite;
    shrimp.setVelocity(0, 0)
    scene.setTileMapLevel(levels[level - 1])
    tiles.placeOnRandomTile(shrimp, assets.tile`player spawn`)
    tiles.setTileAt(shrimp.tilemapLocation(), assets.tile`checkpoint collected`)
    sprites.destroyAllSpritesOfKind(SpriteKind.Enemy)
    for (let urchin_tile of tiles.getTilesByType(assets.tile`enemy spawn`)) {
        urchin = sprites.create(assets.image`urchin`, SpriteKind.Enemy)
        tiles.placeOnTile(urchin, urchin_tile)
        tiles.setTileAt(urchin_tile, image.create(16, 16))
    }
    animate_lava()
    make_moving_platforms()
    database.setNumberValue("level", level)
    //  gm3
    make_crabs()
    //  /gm3
    //  bh9
    spawn_coins()
}

//  /bh9
load_level()
controller.A.onEvent(ControllerButtonEvent.Pressed, function throttle_fire() {
    timer.throttle("player fire", 300, function player_fire() {
        let proj = sprites.createProjectileFromSprite(assets.image`shockwave`, shrimp, 0, 0)
        proj.scale = 0.5
        if (facing_right) {
            proj.vx = 200
            animation.runImageAnimation(shrimp, assets.animation`attack right`, 100, false)
        } else {
            proj.vx = -200
            proj.image.flipX()
            animation.runImageAnimation(shrimp, assets.animation`attack left`, 100, false)
        }
        
    })
})
controller.up.onEvent(ControllerButtonEvent.Pressed, function jump() {
    
    if (jump_count < 1) {
        shrimp.vy = -155
        jump_count += 1
    }
    
})
function take_damage() {
    info.changeLifeBy(-1)
    shrimp.setVelocity(0, 0)
    tiles.placeOnRandomTile(shrimp, assets.tile`checkpoint collected`)
}

function hit(shrimp: any, spine: any) {
    timer.throttle("take damage", 1000, take_damage)
}

//  sprites.on_overlap(SpriteKind.player, SpriteKind.enemy_projectile, hit)
//  sprites.on_overlap(SpriteKind.player, SpriteKind.floating_enemy, hit)
//  gm3
//  sprites.on_overlap(SpriteKind.player, SpriteKind.patrolling_enemy, hit)
//  /gm3
//  bh9
sprites.onOverlap(SpriteKind.Player, SpriteKind.Food, function get_coin(shrimp: Sprite, coin: Sprite) {
    info.changeScoreBy(500)
    music.powerUp.play()
    coin.destroy()
})
//  /bh9
scene.onOverlapTile(SpriteKind.Player, assets.tile`lava`, function hit_lava(shrimp: Sprite, location: tiles.Location) {
    timer.throttle("take damage", 1000, take_damage)
})
//  bh8
scene.onOverlapTile(SpriteKind.Player, assets.tile`ladder`, function use_ladder(shrimp: Sprite, location: tiles.Location) {
    shrimp.vy = 0
    if (controller.up.isPressed()) {
        shrimp.vy = -50
    } else if (controller.down.isPressed()) {
        shrimp.vy = 50
    }
    
})
//  /bh8
scene.onOverlapTile(SpriteKind.Player, assets.tile`checkpoint uncollected`, function reach_checkpoint(shrimp: Sprite, checkpoint: tiles.Location) {
    for (let checkpoint_collected of tiles.getTilesByType(assets.tile`checkpoint collected`)) {
        tiles.setTileAt(checkpoint_collected, image.create(16, 16))
    }
    tiles.setTileAt(checkpoint, assets.tile`checkpoint collected`)
})
scene.onHitWall(SpriteKind.Projectile, function hit_wall(proj: Sprite, location: tiles.Location) {
    let effect_sprite: Sprite;
    if (tiles.tileImageAtLocation(location).equals(assets.tile`breakable rock`)) {
        tiles.setTileAt(location, image.create(16, 16))
        tiles.setWallAt(location, false)
        effect_sprite = sprites.create(assets.tile`breakable rock`)
        tiles.placeOnTile(effect_sprite, location)
        effect_sprite.destroy(effects.disintegrate, 500)
    }
    
})
scene.onOverlapTile(SpriteKind.Player, assets.tile`level end`, function next_level() {
    
    if (level == levels.length) {
        game.over(true)
    }
    
    level += 1
    load_level()
})
//  bh7
function enemy_animate(enemy: Sprite) {
    enemy.image.flipY()
    for (let colour = 1; colour < 16; colour++) {
        enemy.image.replace(colour, 1)
    }
    enemy.setKind(SpriteKind.effect)
    enemy.setFlag(SpriteFlag.Ghost, true)
    enemy.setFlag(SpriteFlag.AutoDestroy, true)
    enemy.ay = 325
    enemy.vy = -100
}

//  /bh7
function enemy_hit(proj: Sprite, enemy: Sprite) {
    info.changeScoreBy(10)
    proj.destroy()
    //  bh7
    //  enemy.destroy()
    enemy_animate(enemy)
}

//  /bh7
sprites.onOverlap(SpriteKind.Projectile, SpriteKind.Enemy, enemy_hit)
sprites.onOverlap(SpriteKind.Projectile, SpriteKind.floating_enemy, enemy_hit)
//  gm3
sprites.onOverlap(SpriteKind.Projectile, SpriteKind.patrolling_enemy, enemy_hit)
//  /gm3
function urchin_fire(urchin: any) {
    let spine: Sprite;
    let angle: number;
    for (let vx = -100; vx < 101; vx += 100) {
        for (let vy = -100; vy < 101; vy += 100) {
            if (vx != 0 || vy != 0) {
                spine = sprites.createProjectileFromSprite(assets.image`spine`, urchin, vx, vy)
                spine.setKind(SpriteKind.enemy_projectile)
                angle = spriteutils.radiansToDegrees(spriteutils.heading(spine))
                transformSprites.rotateSprite(spine, angle)
            }
            
        }
    }
}

game.onUpdateInterval(3000, function urchin_behaviour() {
    for (let urchin of sprites.allOfKind(SpriteKind.Enemy)) {
        urchin_fire(urchin)
    }
})
function shark_spawn() {
    let shark = sprites.create(assets.image`shark`, SpriteKind.floating_enemy)
    if (randint(1, 2) == 1) {
        shark.image.flipX()
        shark.right = 1
        shark.vx = 50
    } else {
        shark.left = tilesAdvanced.getTilemapWidth() * 16 - 1
        shark.vx = -50
    }
    
    if (spriteutils.distanceBetween(shark, shrimp) < 120) {
        shark.destroy()
        shark_spawn
    }
    
    shark.y = shrimp.y
    sprites.setDataNumber(shark, "start y", shark.y)
    shark.setFlag(SpriteFlag.GhostThroughWalls, true)
}

game.onUpdateInterval(1000, shark_spawn)
function shark_behaviour() {
    let start_y: number;
    for (let shark of sprites.allOfKind(SpriteKind.floating_enemy)) {
        if (shark.left > tilesAdvanced.getTilemapWidth() * 16 || shark.right < 0) {
            shark.destroy()
        }
        
        start_y = sprites.readDataNumber(shark, "start y")
        shark.y = Math.sin(shark.x / 20) * 20 + start_y
    }
}

function x_movement() {
    
    if (controller.left.isPressed()) {
        shrimp.vx -= 8
        facing_right = false
    } else if (controller.right.isPressed()) {
        shrimp.vx += 8
        facing_right = true
    }
    
    shrimp.vx *= 0.9
}

function y_movement() {
    
    if (shrimp.isHittingTile(CollisionDirection.Bottom)) {
        jump_count = 0
    }
    
}

//  bh8
function check_on_ladder() {
    if (tiles.tileAtLocationEquals(shrimp.tilemapLocation(), assets.tile`ladder`)) {
        shrimp.ay = 0
    } else {
        shrimp.ay = 325
    }
    
}

//  /bh8
//  gm3
function crab_behaviour() {
    let location: tiles.Location;
    let tile_infront: tiles.Location;
    if (sprites.allOfKind(SpriteKind.patrolling_enemy).length < 1) {
        return
    }
    
    for (let crab of sprites.allOfKind(SpriteKind.patrolling_enemy)) {
        location = crab.tilemapLocation()
        tile_infront = tiles.getTileLocation(location.col, location.row + 1)
        if (!tiles.tileAtLocationIsWall(tile_infront)) {
            crab.vx *= -1
            crab.image.flipX()
        }
        
    }
}

//  /gm3
sprites.onOverlap(SpriteKind.Player, SpriteKind.moving_platform, function hit_moving_platform(shrimp: Sprite, platform: Sprite) {
    if (Math.abs(platform.x - shrimp.x) > Math.abs(platform.y - shrimp.y)) {
        shrimp.vx = 0
        while (shrimp.overlapsWith(platform)) {
            shrimp.x -= Math.sign(platform.x - shrimp.x)
            pause(0)
        }
    } else {
        shrimp.vy = 0
        while (shrimp.overlapsWith(platform)) {
            shrimp.y -= Math.sign(platform.y - shrimp.y)
            pause(0)
        }
    }
    
})
function use_moving_platform() {
    let platform: Sprite;
    let fps: number;
    
    for (let hitbox of sprites.allOfKind(SpriteKind.platform_hitbox)) {
        platform = sprites.readDataSprite(hitbox, "platform")
        hitbox.setPosition(platform.x, platform.top - 2)
        if (shrimp.overlapsWith(hitbox)) {
            jump_count = 0
            fps = 1000 / spriteutils.getDeltaTime()
            shrimp.x += platform.vx / fps
            shrimp.ay = 0
            return
        }
        
    }
    shrimp.ay = 325
}

//  /bh8
game.onUpdate(function tick() {
    x_movement()
    y_movement()
    use_moving_platform()
    shark_behaviour()
    //  gm3
    crab_behaviour()
    //  /gm3
    //  bh8
    check_on_ladder()
})
