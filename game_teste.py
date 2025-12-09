import math, random

WIDTH, HEIGHT = 900, 600
TITLE = "Jogo Plataforma - Pygame Zero"

game_state = "menu"
music_enabled = True
effects_enabled = True

MUSIC_VOLUME = 0.35
EFFECT_VOLUME = 0.7
bg_music_ref = None

def start_music():
    global bg_music_ref
    if music_enabled:
        try:
            bg_music_ref = sounds.bg.play(-1)
            bg_music_ref.volume = MUSIC_VOLUME
        except:
            pass

def stop_music():
    global bg_music_ref
    try:
        if bg_music_ref: bg_music_ref.stop()
    except:
        pass

PLAYER_W, PLAYER_H = 30, 45

player = {"x": 80, "y": HEIGHT - 200, "vx": 0, "vy": 0,
          "speed": 4, "jump": -15, "on_ground": False,
          "color": (40,160,255)}

GRAVITY, FRICTION = 0.6, 0.85

platforms = []
def make_platform(x, y, w, h=16): platforms.append(Rect((x,y),(w,h)))

make_platform(0, HEIGHT - 18, WIDTH, 18)
plat_data = [(60,460,220),(340,520,200),(620,420,240),
             (240,340,160),(480,260,200),(70,200,160)]
for p in plat_data: make_platform(*p)

enemies = []
def spawn_enemy(p, speed):
    w = h = 36
    x = p.x + random.randint(0, p.width-w)
    y = p.y - h
    enemies.append({"rect": Rect((x,y),(w,h)),
                    "dir": random.choice([-1,1]),
                    "speed": speed, "platform": p})

for p in platforms[2:5]:
    spawn_enemy(p, random.uniform(1.0,1.6))

collectibles = []
def spawn_collectible(x,y):
    r=12; collectibles.append({"rect":Rect((x-r,y-r),(r*2,r*2)),
                               "collected":False})

for p in platforms[1:]:
    for i in range(max(1,p.width//160)):
        spawn_collectible(p.x+20+i*80+random.randint(-10,10), p.y-20)

score = 0
total_collectibles = len(collectibles)

def reset_game():
    global score, total_collectibles, game_state
    player.update({"x":80,"y":HEIGHT-200,"vx":0,"vy":0,"on_ground":False})
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

def on_key_down(key):
    global music_enabled, effects_enabled, game_state
    if game_state == "menu":
        if key==keys.S: game_state="playing"; start_music()
        if key==keys.Q: exit()
        return
    if key in (keys.SPACE,keys.UP) and game_state=="playing":
        if player["on_ground"]:
            player["vy"]=player["jump"]; player["on_ground"]=False
            if effects_enabled: sounds.jump.play()
    if key==keys.R and game_state in ("lost","won"): reset_game()
    if key==keys.M:
        music_enabled=not music_enabled
        start_music() if music_enabled else stop_music()
    if key==keys.N: effects_enabled=not effects_enabled

def update():
    global score, game_state
    if game_state!="playing": return

    if keyboard.left: player["vx"]=-player["speed"]
    elif keyboard.right: player["vx"]=player["speed"]
    else:
        player["vx"]*=FRICTION
        if abs(player["vx"])<.1: player["vx"]=0

    player["vy"] += GRAVITY
    player["x"] += player["vx"]

    r = Rect((player["x"],player["y"]),(PLAYER_W,PLAYER_H))

    for p in platforms:
        if r.colliderect(p):
            player["x"]=p.left-PLAYER_W if player["vx"]>0 else p.right
            r.x=player["x"]

    player["y"] += player["vy"]
    r.y = player["y"]
    player["on_ground"]=False

    for p in platforms:
        if r.colliderect(p):
            if player["vy"]>0:
                player["y"]=p.top-PLAYER_H; player["vy"]=0; player["on_ground"]=True
            else:
                player["y"]=p.bottom; player["vy"]=0
            r.y=player["y"]

    if player["y"]>HEIGHT:
        game_state="lost";
        stop_music()
        if effects_enabled: sounds.hit.play()

    for e in enemies:
        er=e["rect"]; er.x+=e["dir"]*e["speed"]
        if er.x < e["platform"].x:
            er.x=e["platform"].x; e["dir"]=1
        if er.right > e["platform"].right:
            er.right=e["platform"].right; e["dir"]=-1
        if er.colliderect(r):
            game_state="lost"; stop_music()
            if effects_enabled: sounds.hit.play()

    for c in collectibles:
        if not c["collected"] and c["rect"].colliderect(r):
            c["collected"]=True; score+=1

    if score>=total_collectibles:
        game_state="won"; stop_music()

def draw():
    screen.fill("#1b1f2b")
    if game_state=="menu":
        screen.draw.text("JOGO PLATAFORMA",center=(WIDTH//2,150),fontsize=64,color="white")
        screen.draw.text("[S] Iniciar",center=(WIDTH//2,300),fontsize=42,color="lightgreen")
        screen.draw.text("[Q] Sair",center=(WIDTH//2,360),fontsize=42,color="tomato")
        screen.draw.text("[M] Musica [N] Efeitos",center=(WIDTH//2,440),fontsize=32,color="yellow")
        return

    for p in platforms: screen.draw.filled_rect(p,(100,100,100))
    screen.draw.filled_rect(Rect((player["x"],player["y"]),(PLAYER_W,PLAYER_H)), player["color"])
    for e in enemies: screen.draw.filled_rect(e["rect"],(200,40,40))
    for c in collectibles:
        if not c["collected"]:
            screen.draw.filled_circle(c["rect"].center, c["rect"].width//2, (255,215,0))

    screen.draw.text(f"Pontos: {score}/{total_collectibles}",(10,10),fontsize=28,color="white")

    if game_state=="won":
        screen.draw.text("VOCE VENCEU! (R)",center=(WIDTH//2,HEIGHT//2),fontsize=50,color=(100,255,150))
    if game_state=="lost":
        screen.draw.text("VOCE PERDEU! (R)",center=(WIDTH//2,HEIGHT//2),fontsize=50,color=(255,80,80))
