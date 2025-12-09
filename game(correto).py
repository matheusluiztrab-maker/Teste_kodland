# Escreva o seu código aqui :-)
import math, random

WIDTH, HEIGHT = 900, 600
TITLE = "Jogo Plataforma - Pygame Zero"

game_state = "menu"
music_enabled = True
effects_enabled = True

MUSIC_VOLUME = 0.35
EFFECT_VOLUME = 0.7

PLAYER_W, PLAYER_H = 30, 45

# Player usando Actor com imagem
player = Actor("player")
player.x = 80
player.y = HEIGHT - 200
player.vx = 0
player.vy = 0
player.speed = 4
player.jump = -15
player.on_ground = False

GRAVITY, FRICTION = 0.6, 0.85

# Plataformas
platforms = []
def make_platform(x, y, w, h=16):
    platforms.append(Rect((x,y),(w,h)))

make_platform(0, HEIGHT - 18, WIDTH, 18)
plat_data = [(60,460,220),(340,520,200),(620,420,240),
             (240,340,160),(480,260,200),(70,200,160)]
for p in plat_data: make_platform(*p)

# Inimigos
enemies = []
def spawn_enemy(p, speed):
    a = Actor("enemy")
    a.x = p.x + random.randint(0, p.width - a.width)
    a.y = p.y - a.height
    enemies.append({"actor": a, "dir": random.choice([-1,1]), "speed": speed, "platform": p})

for p in platforms[2:5]:
    spawn_enemy(p, random.uniform(1.0,1.6))

# Peixes coletáveis
collectibles = []
def spawn_collectible(x, y):
    fish = Actor("fish")
    fish.x = x
    fish.y = y
    collectibles.append({"actor": fish, "collected": False})

for p in platforms[1:]:
    for i in range(max(1,p.width//160)):
        spawn_collectible(p.x+20+i*80+random.randint(-10,10), p.y-20)

score = 0
total_collectibles = len(collectibles)

# Música
def start_music():
    if music_enabled:
        try:
            sounds.bg.play(-1)  # loop infinito
        except:
            pass

def stop_music():
    try:
        sounds.bg.stop()
    except:
        pass

# Reset do jogo
def reset_game():
    global score, total_collectibles, game_state
    player.x = 80
    player.y = HEIGHT - 200
    player.vx = 0
    player.vy = 0
    player.on_ground = False

    enemies.clear()
    for p in platforms[2:5]:
        spawn_enemy(p, random.uniform(1.0,1.6))

    collectibles.clear()
    for p in platforms[1:]:
        for i in range(max(1,p.width//160)):
            spawn_collectible(p.x+20+i*80+random.randint(-10,10), p.y-20)

    score = 0
    total_collectibles = len(collectibles)
    game_state = "playing"
    start_music()

# Controles
def on_key_down(key):
    global music_enabled, effects_enabled, game_state
    if game_state == "menu":
        if key==keys.S: game_state="playing"; start_music()
        if key==keys.Q: exit()
        return
    if key in (keys.SPACE, keys.UP) and game_state=="playing":
        if player.on_ground:
            player.vy = player.jump
            player.on_ground = False
            if effects_enabled: sounds.jump.play()
    if key==keys.R and game_state in ("lost","won"): reset_game()
    if key==keys.M:
        music_enabled = not music_enabled
        start_music() if music_enabled else stop_music()
    if key==keys.N:
        effects_enabled = not effects_enabled

# Update
def update():
    global score, game_state
    if game_state != "playing": return

    # Movimento horizontal
    if keyboard.left: player.vx = -player.speed
    elif keyboard.right: player.vx = player.speed
    else:
        player.vx *= FRICTION
        if abs(player.vx) < 0.1: player.vx = 0

    # Gravidade e movimento
    player.vy += GRAVITY
    player.x += player.vx

    r = player.collider if hasattr(player, "collider") else Rect((player.x - PLAYER_W//2, player.y - PLAYER_H//2), (PLAYER_W, PLAYER_H))

    # Colisão horizontal
    for p in platforms:
        if r.colliderect(p):
            if player.vx > 0: player.x = p.left - PLAYER_W//2
            elif player.vx < 0: player.x = p.right + PLAYER_W//2
            r.x = player.x - PLAYER_W//2

    # Colisão vertical
    player.y += player.vy
    r.y = player.y - PLAYER_H//2
    player.on_ground = False

    for p in platforms:
        if r.colliderect(p):
            if player.vy > 0:
                player.y = p.top - PLAYER_H//2
                player.vy = 0
                player.on_ground = True
            elif player.vy < 0:
                player.y = p.bottom + PLAYER_H//2
                player.vy = 0
            r.y = player.y - PLAYER_H//2

    if player.y > HEIGHT:
        game_state = "lost"
        stop_music()
        if effects_enabled: sounds.hit.play()

    # Movimentação inimigos
    for e in enemies:
        a = e["actor"]
        a.x += e["dir"] * e["speed"]
        if a.x < e["platform"].x:
            a.x = e["platform"].x
            e["dir"] = 1
        if a.right > e["platform"].right:
            a.right = e["platform"].right
            e["dir"] = -1
        if a.colliderect(player):
            game_state = "lost"
            stop_music()
            if effects_enabled: sounds.hit.play()

    # Coleta dos peixes
    for c in collectibles:
        if not c["collected"] and player.colliderect(c["actor"]):
            c["collected"] = True
            score += 1
            # Som de coleta removido

    if score >= total_collectibles:
        game_state = "won"
        stop_music()

# Draw
def draw():
    screen.fill("#1b1f2b")
    if game_state == "menu":
        screen.draw.text("JOGO PLATAFORMA", center=(WIDTH//2,150), fontsize=64, color="white")
        screen.draw.text("[S] Iniciar", center=(WIDTH//2,300), fontsize=42, color="lightgreen")
        screen.draw.text("[Q] Sair", center=(WIDTH//2,360), fontsize=42, color="tomato")
        screen.draw.text("[M] Musica [N] Efeitos", center=(WIDTH//2,440), fontsize=32, color="yellow")
        return

    for p in platforms:
        screen.draw.filled_rect(p, (100,100,100))

    # Desenha player, inimigos e peixes
    player.draw()
    for e in enemies:
        e["actor"].draw()
    for c in collectibles:
        if not c["collected"]:
            c["actor"].draw()

    screen.draw.text(f"Pontos: {score}/{total_collectibles}", (10,10), fontsize=28, color="white")

    if game_state == "won":
        screen.draw.text("VOCE VENCEU! (R)", center=(WIDTH//2, HEIGHT//2), fontsize=50, color=(100,255,150))
    if game_state == "lost":
        screen.draw.text("VOCE PERDEU! (R)", center=(WIDTH//2, HEIGHT//2), fontsize=50, color=(255,80,80))
