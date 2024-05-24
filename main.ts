//  week 1
//  gm1 checkpoint system and lives 7
//  bh1 scrolling background 4/3 - add extension
//  bh2 destroy some rock obstacles - edit tilemap then code 3
//  bh3 animate lava tiles 2/3
namespace SpriteKind {
    export const enemy_projectile = SpriteKind.create()
}

//  sprites
let shrimp = sprites.create(assets.image`shrimp right`, SpriteKind.Player)
shrimp.ay = 325
scene.cameraFollowSprite(shrimp)
characterAnimations.runFrames(shrimp, [assets.image`shrimp right`], 1, characterAnimations.rule(Predicate.FacingRight))
characterAnimations.runFrames(shrimp, [assets.image`shrimp left`], 1, characterAnimations.rule(Predicate.FacingLeft))
//  variables
let levels = [assets.tilemap`level 1`, assets.tilemap`level 2`, assets.tilemap`level 3`]
let level = 2
let gravity = 8
let jump_count = 2
let facing_right = true
//  setup
//  bh1
//  scene.set_background_color(6) # comment out
scene.setBackgroundImage(assets.image`background`)
scroller.scrollBackgroundWithCamera(scroller.CameraScrollMode.OnlyHorizontal)
//  /bh1
//  gm1
info.setLife(3)
//  /gm1
//  bh3
function animate_lava() {
    let effect_sprite: Sprite;
    for (let lava_tile of tiles.getTilesByType(assets.tile`lava`)) {
        effect_sprite = sprites.create(image.create(1, 1))
        tiles.placeOnTile(effect_sprite, lava_tile)
        effect_sprite.y -= 8
        effect_sprite.startEffect(effects.bubbles)
    }
}

//  /bh3
function load_level() {
    let urchin: Sprite;
    shrimp.setVelocity(0, 0)
    scene.setTileMapLevel(levels[level - 1])
    tiles.placeOnRandomTile(shrimp, assets.tile`player spawn`)
    //  gm1
    //  tiles.set_tile_at(shrimp.tilemap_location(), image.create(16, 16)) # remove
    tiles.setTileAt(shrimp.tilemapLocation(), assets.tile`checkpoint collected`)
    //  /gm1
    for (let urchin_tile of tiles.getTilesByType(assets.tile`enemy spawn`)) {
        urchin = sprites.create(assets.image`urchin`, SpriteKind.Enemy)
        tiles.placeOnTile(urchin, urchin_tile)
        tiles.setTileAt(urchin_tile, image.create(16, 16))
    }
    //  bh3
    animate_lava()
}

//  /bh3
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
//  gm1
function take_damage() {
    info.changeLifeBy(-1)
    shrimp.setVelocity(0, 0)
    tiles.placeOnRandomTile(shrimp, assets.tile`checkpoint collected`)
}

//  /gm1
function hit(shrimp: any, spine: any) {
    //  gm1
    //  game.over(False) # remove
    timer.throttle("take damage", 1000, take_damage)
}

//  /gm1
//  sprites.on_overlap(SpriteKind.player, SpriteKind.enemy_projectile, hit)
//  /gm1
scene.onOverlapTile(SpriteKind.Player, assets.tile`lava`, function hit_lava(shrimp: Sprite, location: tiles.Location) {
    //  gm1
    //  game.over(False) # remove
    timer.throttle("take damage", 1000, take_damage)
})
//  gm1
scene.onOverlapTile(SpriteKind.Player, assets.tile`checkpoint uncollected`, function reach_checkpoint(shrimp: Sprite, checkpoint: tiles.Location) {
    for (let checkpoint_collected of tiles.getTilesByType(assets.tile`checkpoint collected`)) {
        tiles.setTileAt(checkpoint_collected, image.create(16, 16))
    }
    tiles.setTileAt(checkpoint, assets.tile`checkpoint collected`)
})
//  /gm1
//  bh2
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
//  /bh2
scene.onOverlapTile(SpriteKind.Player, assets.tile`level end`, function next_level() {
    
    if (level == levels.length) {
        game.over(true)
    }
    
    level += 1
    load_level()
})
sprites.onOverlap(SpriteKind.Projectile, SpriteKind.Enemy, function enemy_hit(proj: Sprite, enemy: Sprite) {
    info.changeScoreBy(10)
    proj.destroy()
    enemy.destroy()
})
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

game.onUpdate(function tick() {
    x_movement()
    y_movement()
})
