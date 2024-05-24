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
scene.setBackgroundColor(6)
function load_level() {
    let urchin: Sprite;
    shrimp.setVelocity(0, 0)
    scene.setTileMapLevel(levels[level - 1])
    tiles.placeOnRandomTile(shrimp, assets.tile`player spawn`)
    for (let urchin_tile of tiles.getTilesByType(assets.tile`enemy spawn`)) {
        urchin = sprites.create(assets.image`urchin`, SpriteKind.Enemy)
        tiles.placeOnTile(urchin, urchin_tile)
        tiles.setTileAt(urchin_tile, image.create(16, 16))
    }
}

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
sprites.onOverlap(SpriteKind.Player, SpriteKind.enemy_projectile, function hit(shrimp: Sprite, spine: Sprite) {
    game.over(false)
})
scene.onOverlapTile(SpriteKind.Player, assets.tile`lava`, function hit_lava(shrimp: Sprite, location: tiles.Location) {
    game.over(false)
})
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
