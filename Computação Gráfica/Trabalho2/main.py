import os, math, random, time
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

pygame.init()
WIN_W, WIN_H = 1200, 800
screen = pygame.display.set_mode((WIN_W, WIN_H), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Resgate Interplanetário - Ajude o Papai Noel!")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def init_gl():
    glViewport(0, 0, WIN_W, WIN_H)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50.0, WIN_W / float(max(1, WIN_H)), 0.1, 2000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  (1.0, 0.98, 0.95, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 0.98, 0.95, 1.0))
    glClearColor(0.01, 0.01, 0.02, 1.0)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

init_gl()

def load_texture(relpath):
    path = os.path.join(BASE_DIR, relpath)
    if not os.path.isfile(path):
        print(f"[WARN] texture not found: {path}")
        return 0
    surf = pygame.image.load(path).convert_alpha()
    surf = pygame.transform.flip(surf, False, True)
    has_alpha = surf.get_bitsize() == 32
    mode = "RGBA" if has_alpha else "RGB"
    data = pygame.image.tostring(surf, mode, True)
    w, h = surf.get_size()
    texid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texid)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    if has_alpha:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    else:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
    try:
        glGenerateMipmap(GL_TEXTURE_2D)
    except Exception:
        pass
    glBindTexture(GL_TEXTURE_2D, 0)
    print(f"[OK] loaded: {relpath} -> id {texid}")
    return texid

texture_files = {
    'sun': 'textures/sun.jpg',
    'mercury': 'textures/mercury.jpg',
    'venus': 'textures/venus.jpg',
    'earth': 'textures/earth.jpg',
    'moon': 'textures/moon.jpg',
    'mars': 'textures/mars.jpg',
    'jupiter': 'textures/jupiter.jpg',
    'saturn': 'textures/saturn.jpg',
    'saturn_ring': 'textures/saturn_ring.png',
    'uranus': 'textures/uranus.jpg',
    'neptune': 'textures/neptune.jpg',
    'present': 'textures/present.jpg',
    'basket': 'textures/basket.jpg',
    'meteor': 'textures/meteor.jpg'
}
textures = {}
for k, v in texture_files.items():
    textures[k] = load_texture(v)

planet_scales = {'sun':3.2,'mercury':0.45,'venus':0.6,'earth':0.75,'moon':0.22,'mars':0.55,'jupiter':1.8,'saturn':1.6,'uranus':1.0,'neptune':1.0}
orbit_radii = {'mercury':6.0,'venus':9.0,'earth':12.0,'mars':15.0,'jupiter':19.0,'saturn':24.0,'uranus':30.0,'neptune':36.0}
orbit_speeds = {'mercury':4.2,'venus':1.6,'earth':1.0,'mars':0.8,'jupiter':0.4,'saturn':0.3,'uranus':0.2,'neptune':0.15}
spin_speeds = {'sun':0.02,'mercury':0.08,'venus':0.03,'earth':0.2,'moon':0.25,'mars':0.12,'jupiter':0.18,'saturn':0.14,'uranus':0.11,'neptune':0.11}
angles = {k: random.uniform(0,360) for k in orbit_radii.keys()}
spins = {k: random.uniform(0,360) for k in spin_speeds.keys()}

star_list = []
def generate_stars(n=600):
    star_list.clear()
    for _ in range(n):
        theta = random.uniform(0,2*math.pi)
        phi   = random.uniform(0,math.pi)
        d     = random.uniform(80.0,220.0)
        x = d*math.sin(phi)*math.cos(theta)
        y = d*math.cos(phi)
        z = d*math.sin(phi)*math.sin(theta)
        size = random.uniform(0.6,2.2)
        phase = random.uniform(0,2*math.pi)
        color = random.choice([(1,1,1),(1,0.95,0.9),(0.9,0.95,1)])
        base = random.uniform(0.6,1.0)
        star_list.append([x,y,z,size,phase,color,base])
generate_stars(600)

def draw_sphere(radius, tex_id=0, slices=48, stacks=48):
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    if tex_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        gluQuadricTexture(quad, GL_TRUE)
    else:
        gluQuadricTexture(quad, GL_FALSE)
    gluSphere(quad, radius, slices, stacks)
    if tex_id:
        glBindTexture(GL_TEXTURE_2D,0)
        glDisable(GL_TEXTURE_2D)
    gluDeleteQuadric(quad)

def draw_ring(inner_r, outer_r, tex_id=0, segments=128):
    if tex_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(segments+1):
        t = i/float(segments)
        theta = 2.0*math.pi*t
        x_out = outer_r*math.cos(theta); z_out = outer_r*math.sin(theta)
        x_in  = inner_r*math.cos(theta); z_in  = inner_r*math.sin(theta)
        if tex_id:
            glTexCoord2f(i/float(segments)*6.0, 0); glVertex3f(x_out,0,z_out)
            glTexCoord2f(i/float(segments)*6.0, 1); glVertex3f(x_in,0,z_in)
        else:
            glVertex3f(x_out,0,z_out); glVertex3f(x_in,0,z_in)
    glEnd()
    if tex_id:
        glBindTexture(GL_TEXTURE_2D,0)
        glDisable(GL_TEXTURE_2D)

camera_distance = 50.0
camera_az = 15.0
camera_el = 0.0
camera_pan_x = 0.0
camera_pan_y = 0.0
mouse_left_down = False
mouse_right_down = False
mouse_last_x = 0
mouse_last_y = 0

paused = False
show_orbits = True
wireframe = False
show_starfield = True

frames = 0; fps = 0; fps_time = time.time()
clock = pygame.time.Clock()

class FallingObject:
    def __init__(self, pos, vel, kind='present'):
        self.x, self.y, self.z = pos
        self.vx, self.vy, self.vz = vel
        self.kind = kind
        self.radius = 0.9 if kind=='present' else 1.2
        self.collected = False
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2.0, 2.0)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        self.rotation += self.rotation_speed

class Player:
    def __init__(self):
        self.x = 0.0
        self.y = -8.0   
        self.z = -15.0  
        self.width = 4.0
        self.radius = 2.5
        self.score = 0
        self.lives = 3
        self.move_speed = 25.0  

        self.min_x, self.max_x = -25.0, 25.0
        self.min_z, self.max_z = -30.0, 20.0

    def move_by(self, dx, dz):
        self.x = max(self.min_x, min(self.max_x, self.x + dx))
        self.z = max(self.min_z, min(self.max_z, self.z + dz))

    def set_position(self, x, z):
        self.x = max(self.min_x, min(self.max_x, x))
        self.z = max(self.min_z, min(self.max_z, z))

player = Player()

state = 'menu'  
current_planet = None
objects = []
spawn_timer = 0.0

# Variáveis para controle de progresso
completed_levels = []
current_level_index = 0
level_sequence = ['mars', 'jupiter', 'neptune']

# Variáveis para confetes
confetti_particles = []
earth_rotation = 0.0

# planet configs
planet_configs = {
    'mars': {'present_goal': 3, 'time_limit': 30.0, 'present_speed': -8.0, 'meteors': False, 'fall_speed_mul':1.0},
    'jupiter': {'present_goal': 5, 'time_limit': 0.0, 'present_speed': -10.0, 'meteors': True, 'fall_speed_mul':1.0},
    'neptune': {'present_goal': 6, 'time_limit': 0.0, 'present_speed': -12.0, 'meteors': True, 'fall_speed_mul':1.6},
}

level_start_time = 0.0
level_time_left = 0.0
level_goal = 0
level_collected = 0

def start_level(planet):
    global current_planet, objects, spawn_timer, level_start_time, level_time_left, level_goal, level_collected, player, state
    current_planet = planet
    objects = []
    spawn_timer = 0.0
    player.score = 0
    player.lives = 3
    level_collected = 0
    cfg = planet_configs[planet]
    level_goal = cfg['present_goal']
    level_start_time = time.time()
    level_time_left = cfg['time_limit']
    player.set_position(0.0, -15.0)
    state = 'playing'

def end_level(won):
    global state, completed_levels, current_level_index, confetti_particles, earth_rotation
    if won:
        if current_planet not in completed_levels:
            completed_levels.append(current_planet)
        state = 'level_complete'
    else:
        state = 'gameover'

def start_next_level():
    global current_level_index, confetti_particles, earth_rotation
    current_level_index += 1
    if current_level_index < len(level_sequence):
        start_level(level_sequence[current_level_index])
    else:
        state = 'final_celebration'
        earth_rotation = 0.0
        create_confetti()

def create_confetti():
    global confetti_particles
    confetti_particles = []
    for _ in range(200):
        confetti_particles.append({
            'x': random.uniform(-50, 50),
            'y': random.uniform(-30, 60),
            'z': random.uniform(-50, 50),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-1, -5),
            'vz': random.uniform(-2, 2),
            'color': random.choice([
                (1.0, 0.0, 0.0),    # Vermelho
                (0.0, 1.0, 0.0),    # Verde
                (0.0, 0.0, 1.0),    # Azul
                (1.0, 1.0, 0.0),    # Amarelo
                (1.0, 0.0, 1.0),    # Magenta
                (0.0, 1.0, 1.0),    # Ciano
                (1.0, 0.5, 0.0),    # Laranja
                (0.5, 0.0, 1.0)     # Roxo
            ]),
            'size': random.uniform(0.1, 0.3),
            'rotation': random.uniform(0, 360),
            'rotation_speed': random.uniform(-5, 5)
        })

def update_confetti(dt):
    global confetti_particles
    for confetti in confetti_particles:
        confetti['x'] += confetti['vx'] * dt
        confetti['y'] += confetti['vy'] * dt
        confetti['z'] += confetti['vz'] * dt
        confetti['rotation'] += confetti['rotation_speed'] * dt
        
        if confetti['y'] < -40:
            confetti['y'] = 60
            confetti['x'] = random.uniform(-50, 50)
            confetti['z'] = random.uniform(-50, 50)
            confetti['vy'] = random.uniform(-1, -5)

def spawn_present(fall_speed):
    x = random.uniform(player.min_x - 3.0, player.max_x + 3.0)
    z = random.uniform(-15.0, 15.0) 
    y = random.uniform(25.0, 40.0)
    vx, vy, vz = random.uniform(-0.5,0.5), fall_speed, random.uniform(-0.3,0.3)
    o = FallingObject((x,y,z),(vx,vy,vz),'present')
    objects.append(o)

def spawn_meteor(fall_speed):
    x = random.uniform(player.min_x - 5.0, player.max_x + 5.0)
    z = random.uniform(-20.0, 20.0)
    y = random.uniform(35.0, 50.0)
    vx, vy, vz = random.uniform(-2.0,2.0), fall_speed*1.3, random.uniform(-1.5,1.5)
    o = FallingObject((x,y,z),(vx,vy,vz),'meteor')
    objects.append(o)

def update_game(dt):
    global spawn_timer, level_time_left, level_collected, state
    if state != 'playing' or paused: return

    cfg = planet_configs[current_planet]
    spawn_rate = max(0.25, 1.4 - (cfg['present_goal']*0.02))
    spawn_timer += dt
    if spawn_timer >= spawn_rate:
        spawn_timer = 0.0
        for _ in range(random.choice([1,1,2])):
            spawn_present(cfg['present_speed'] * cfg['fall_speed_mul'])
    if cfg['meteors'] and random.random() < 0.035:
        spawn_meteor(cfg['present_speed'] * cfg['fall_speed_mul'])

    to_remove = []
    for o in objects:
        o.update(dt)
        if o.y < -35.0:
            to_remove.append(o)
        dx = o.x - player.x
        dz = o.z - player.z
        dy = o.y - player.y
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if o.kind == 'present' and dist < (o.radius + player.radius):
            level_collected += 1
            player.score += 10
            o.collected = True
            to_remove.append(o)
        if o.kind == 'meteor' and dist < (o.radius + player.radius):
            player.lives -= 1
            o.collected = True
            to_remove.append(o)

    for o in to_remove:
        if o in objects:
            objects.remove(o)

    # time handling for timed levels
    if planet_configs[current_planet]['time_limit'] > 0:
        elapsed = time.time() - level_start_time
        level_time_left = max(0.0, planet_configs[current_planet]['time_limit'] - elapsed)
        if level_time_left <= 0.0:
            if level_collected >= level_goal:
                end_level(True)
            else:
                end_level(False)
    if level_collected >= level_goal:
        end_level(True)
    if player.lives <= 0:
        end_level(False)

font = pygame.font.SysFont("Arial", 20)

def draw_text_2d(x, y, text, size=20, color=(255,255,255)):
    surf = font.render(str(text), True, color)
    data = pygame.image.tostring(surf, "RGBA", True)
    glWindowPos2d(int(x), int(y))
    glDrawPixels(surf.get_width(), surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)

def draw_hud():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    glOrtho(0, WIN_W, 0, WIN_H, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    draw_text_2d(10, WIN_H-30, f"Score: {player.score}")
    draw_text_2d(200, WIN_H-30, f"Collected: {level_collected}/{level_goal}")
    if planet_configs[current_planet]['time_limit'] > 0:
        draw_text_2d(420, WIN_H-30, f"Time left: {int(level_time_left)}s")
    draw_text_2d(650, WIN_H-30, f"Lives: {player.lives}")

    draw_text_2d(WIN_W-320, WIN_H-30, "ESC - Menu  |  P - Pausa  |  WASD/Setas - Mover  |  Mouse - Câmera")

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_cube(size):
    s = size / 2.0
    glBegin(GL_QUADS)
    
    glNormal3f(0, 0, 1)
    glVertex3f(-s, -s, s)
    glVertex3f(s, -s, s)
    glVertex3f(s, s, s)
    glVertex3f(-s, s, s)
    
    glNormal3f(0, 0, -1)
    glVertex3f(-s, -s, -s)
    glVertex3f(-s, s, -s)
    glVertex3f(s, s, -s)
    glVertex3f(s, -s, -s)
    
    glNormal3f(0, 1, 0)
    glVertex3f(-s, s, -s)
    glVertex3f(-s, s, s)
    glVertex3f(s, s, s)
    glVertex3f(s, s, -s)
    
    glNormal3f(0, -1, 0)
    glVertex3f(-s, -s, -s)
    glVertex3f(s, -s, -s)
    glVertex3f(s, -s, s)
    glVertex3f(-s, -s, s)
    
    glNormal3f(1, 0, 0)
    glVertex3f(s, -s, -s)
    glVertex3f(s, s, -s)
    glVertex3f(s, s, s)
    glVertex3f(s, -s, s)
    
    glNormal3f(-1, 0, 0)
    glVertex3f(-s, -s, -s)
    glVertex3f(-s, -s, s)
    glVertex3f(-s, s, s)
    glVertex3f(-s, s, -s)
    
    glEnd()

def draw_spiky_meteor(radius, spikes=8):
    glPushMatrix()
    glScalef(1.0, 0.8, 1.2) 
    draw_sphere(radius * 0.8, 0, 12, 12)
    glPopMatrix()
    
    glColor3f(0.4, 0.3, 0.2)
    for i in range(spikes):
        angle = 2 * math.pi * i / spikes
        height_var = random.uniform(0.3, 0.7)
        
        glPushMatrix()
        glRotatef(i * 45, 0, 1, 0)
        glTranslatef(radius * 0.9, 0, 0)
        
        glBegin(GL_TRIANGLES)
        glNormal3f(1, 0, 0)
        glVertex3f(radius * 0.4 * height_var, radius * 0.2, 0)
        glVertex3f(0, 0, radius * 0.2)
        glVertex3f(0, 0, -radius * 0.2)
        glEnd()
        
        glPopMatrix()

def draw_sled():
    glPushMatrix()
    glTranslatef(player.x, player.y, player.z)
    
    glColor3f(0.8, 0.1, 0.1)
    
    glBegin(GL_QUAD_STRIP)
    for i in range(13):
        t = i / 12.0
        angle = math.pi * t
        x = math.cos(angle) * player.radius
        y = math.sin(angle) * player.radius * 0.3 - player.radius * 0.3
        z_base = -player.radius * 0.8
        z_top = player.radius * 0.8
        
        glNormal3f(math.cos(angle), math.sin(angle), 0)
        glVertex3f(x, y, z_base)
        glVertex3f(x, y, z_top)
    glEnd()
  
    glColor3f(0.7, 0.08, 0.08)
    glBegin(GL_QUADS)
    glNormal3f(-1, 0, 0)
    glVertex3f(-player.radius, -player.radius * 0.6, -player.radius * 0.8)
    glVertex3f(-player.radius, -player.radius * 0.6, player.radius * 0.8)
    glVertex3f(-player.radius, player.radius * 0.2, player.radius * 0.8)
    glVertex3f(-player.radius, player.radius * 0.2, -player.radius * 0.8)
    
    glNormal3f(1, 0, 0)
    glVertex3f(player.radius, -player.radius * 0.6, -player.radius * 0.8)
    glVertex3f(player.radius, player.radius * 0.2, -player.radius * 0.8)
    glVertex3f(player.radius, player.radius * 0.2, player.radius * 0.8)
    glVertex3f(player.radius, -player.radius * 0.6, player.radius * 0.8)
    glEnd()
    
    glColor3f(0.8, 0.8, 0.9)
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(side * player.radius * 0.9, -player.radius * 0.7, 0)
        glScalef(0.1, 0.1, 1.8)
        draw_cube(1)
        glPopMatrix()
    
    glPopMatrix()

def draw_present():
    size = 1.0
    
    glColor3f(0.8, 0.1, 0.1)
   
    draw_cube(size)
 
    glColor3f(0.9, 0.9, 0.2)

    glPushMatrix()
    glTranslatef(0, size * 0.3, 0)
    glScalef(size * 1.2, size * 0.1, size * 0.1)
    draw_cube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, size * 0.3, 0)
    glScalef(size * 0.1, size * 0.1, size * 1.2)
    draw_cube(1)
    glPopMatrix()

def draw_confetti():
    glDisable(GL_LIGHTING)
    for confetti in confetti_particles:
        glPushMatrix()
        glTranslatef(confetti['x'], confetti['y'], confetti['z'])
        glRotatef(confetti['rotation'], 0, 1, 0)
        
        glColor3f(*confetti['color'])
        size = confetti['size']
        
        glBegin(GL_QUADS)
        glVertex3f(-size, -size, 0)
        glVertex3f(size, -size, 0)
        glVertex3f(size, size, 0)
        glVertex3f(-size, size, 0)
        glEnd()
        
        glPopMatrix()
    glEnable(GL_LIGHTING)

def render_game_objects():
    if state != 'playing':
        return
  
    draw_sled()
    
    for obj in objects:
        glPushMatrix()
        glTranslatef(obj.x, obj.y, obj.z)
        glRotatef(obj.rotation, 0, 1, 0) 
        
        if obj.kind == 'present':
            glColor3f(1, 1, 1)
            draw_present()
        elif obj.kind == 'meteor':
            glColor3f(0.3, 0.25, 0.2)
            draw_spiky_meteor(obj.radius)
        
        glPopMatrix()

def render_level_background():
    if current_planet is None:
        return

    glPushMatrix()
    glDisable(GL_LIGHTING)

    glColor3f(1, 1, 1)

    glTranslatef(0, 0, -120) 
    glRotatef(90, 0, 1, 0)   
    draw_sphere(35, textures.get(current_planet, 0), slices=64, stacks=64)

    glEnable(GL_LIGHTING)
    glPopMatrix()

def render_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glTranslatef(-camera_pan_x, -camera_pan_y, -camera_distance)
    glRotatef(camera_az, 1, 0, 0)
    glRotatef(camera_el, 0, 1, 0)

    if show_starfield:
        glPushMatrix()
        glDisable(GL_LIGHTING)
        t = time.time()
        glPointSize(1.2)
        glBegin(GL_POINTS)
        for s in star_list:
            b = s[6] * (0.6 + 0.4 * abs(math.sin(t*1.8 + s[4])))
            glColor3f(s[5][0]*b, s[5][1]*b, s[5][2]*b)
            glVertex3f(s[0], s[1], s[2])
        glEnd()
        glEnable(GL_LIGHTING)
        glPopMatrix()

    if state == "playing":
        render_level_background()
        render_game_objects()
    elif state == "final_celebration":
        glPushMatrix()
        glDisable(GL_LIGHTING)
        glColor3f(1, 1, 1)
        glTranslatef(0, 0, -100)
        glRotatef(earth_rotation, 0, 1, 0) 
        glRotatef(90, 0, 1, 0)
        draw_sphere(40, textures.get('earth', 0), slices=64, stacks=64)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        
        draw_confetti()
    else:
        glPushMatrix()
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 0.95)
        draw_sphere(planet_scales['sun'], textures.get('sun',0), slices=64, stacks=64)
        glEnable(GL_LIGHTING)
        glPopMatrix()

        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])

        if show_orbits:
            glDisable(GL_LIGHTING)
            glColor3f(0.45, 0.45, 0.45)
            for r in orbit_radii.values():
                glBegin(GL_LINE_LOOP)
                segs = 80
                for i in range(segs):
                    theta = 2.0 * math.pi * i / segs
                    glVertex3f(math.cos(theta) * r, 0.0, math.sin(theta) * r)
                glEnd()
            glEnable(GL_LIGHTING)

        order = ['mercury','venus','earth','mars','jupiter','saturn','uranus','neptune']
        for name in order:
            glPushMatrix()
            glRotatef(angles.get(name, 0.0), 0, 1, 0)
            r = orbit_radii.get(name, 0.0)
            glTranslatef(r, 0, 0)
            glRotatef(spins.get(name, 0.0), 0, 1, 0)
            glRotatef(90, 0, 1, 0)
            draw_sphere(planet_scales[name], textures.get(name,0), slices=32, stacks=32)
            if name == 'saturn':
                glPushMatrix()
                glRotatef(25,1,0,0)
                draw_ring(planet_scales['saturn']*1.05, planet_scales['saturn']*2.8, textures.get('saturn_ring'), segments=120)
                glPopMatrix()
            glPopMatrix()

def draw_beautiful_button(x, y, width, height, text, color=(0.2, 0.6, 0.8), hover=False):
    if hover:
        color = (min(color[0] + 0.2, 1.0), min(color[1] + 0.2, 1.0), min(color[2] + 0.2, 1.0))
    
    glBegin(GL_QUADS)
    glColor3f(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glColor3f(color[0], color[1], color[2])
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
  
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glColor3f(1.0, 1.0, 1.0)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    
    btn_font = pygame.font.SysFont("Arial", 24, bold=True)
    text_surf = btn_font.render(text, True, (255, 255, 255))
    text_data = pygame.image.tostring(text_surf, "RGBA", True)
    text_x = x + (width - text_surf.get_width()) // 2
    text_y = y + (height - text_surf.get_height()) // 2
    glWindowPos2d(int(text_x), int(text_y))
    glDrawPixels(text_surf.get_width(), text_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def draw_menu():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    glOrtho(0, WIN_W, 0, WIN_H, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    glColor4f(0.02, 0.02, 0.05, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WIN_W, 0)
    glVertex2f(WIN_W, WIN_H)
    glVertex2f(0, WIN_H)
    glEnd()

    title_font = pygame.font.SysFont("Arial", 64, bold=True)
    title_surf = title_font.render("Resgate Interplanetário", True, (255, 255, 255))
    title_data = pygame.image.tostring(title_surf, "RGBA", True)
    glWindowPos2d((WIN_W - title_surf.get_width()) // 2, WIN_H - 120)
    glDrawPixels(title_surf.get_width(), title_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, title_data)

    subtitle_font = pygame.font.SysFont("Arial", 20, italic=True)
    subtitle_text = "Ajude o Papai Noel a recuperar os presentes perdidos no espaço!"
    subtitle_surf = subtitle_font.render(subtitle_text, True, (200, 200, 255))
    subtitle_data = pygame.image.tostring(subtitle_surf, "RGBA", True)
    glWindowPos2d((WIN_W - subtitle_surf.get_width()) // 2, WIN_H - 170)
    glDrawPixels(subtitle_surf.get_width(), subtitle_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, subtitle_data)

    # Instruções - POSICIONADAS MAIS PARA BAIXO
    instruction_font = pygame.font.SysFont("Arial", 18)
    instructions = [
        "PRECISAMOS DE SUA AJUDA PARA RECUPERAR OS PRESENTES QUE CAÍRAM DA NAVE!",
        "Utilize as setas ou WASD para movimentar o trenó e passe as fases",
        "para recuperar todos os presentes espalhados pelo sistema solar."
    ]
    
    for i, instruction in enumerate(instructions):
        inst_surf = instruction_font.render(instruction, True, (255, 255, 200))
        inst_data = pygame.image.tostring(inst_surf, "RGBA", True)
        glWindowPos2d((WIN_W - inst_surf.get_width()) // 2, WIN_H - 250 - i * 25) 
    glDrawPixels(inst_surf.get_width(), inst_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, inst_data)

    buttons = [
        ("Marte - Fase 1", "mars", (0.8, 0.3, 0.3)),
        ("Júpiter - Fase 2", "jupiter", (0.3, 0.6, 0.8)),
        ("Netuno - Fase 3", "neptune", (0.8, 0.6, 0.3))
    ]
    
    bx = (WIN_W - 350) // 2
    by = WIN_H // 2 - 20  
    spacing = 80
    
    for i, (label, key, color) in enumerate(buttons):
        y = by - i * spacing
        mouse_x, mouse_y = pygame.mouse.get_pos()
        ogl_y = WIN_H - mouse_y
        hover = (bx <= mouse_x <= bx + 350 and y <= ogl_y <= y + 60)
        
        draw_beautiful_button(bx, y, 350, 60, label, color, hover)

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_level_complete():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    glOrtho(0, WIN_W, 0, WIN_H, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    glColor4f(0.02, 0.02, 0.05, 0.85)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WIN_W, 0)
    glVertex2f(WIN_W, WIN_H)
    glVertex2f(0, WIN_H)
    glEnd()

    big_font = pygame.font.SysFont("Arial", 48, bold=True)
    msg = f"Fase {current_level_index + 1} Concluída!"
    surf = big_font.render(msg, True, (100, 255, 100))
    data = pygame.image.tostring(surf, "RGBA", True)
    glWindowPos2d((WIN_W - surf.get_width()) // 2, WIN_H - 150)
    glDrawPixels(surf.get_width(), surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)

    medium_font = pygame.font.SysFont("Arial", 32)
    score_text = f"Pontuação: {player.score}"
    score_surf = medium_font.render(score_text, True, (255, 255, 100))
    data2 = pygame.image.tostring(score_surf, "RGBA", True)
    glWindowPos2d((WIN_W - score_surf.get_width()) // 2, WIN_H - 220)
    glDrawPixels(score_surf.get_width(), score_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data2)

    # Botões
    mouse_x, mouse_y = pygame.mouse.get_pos()
    ogl_y = WIN_H - mouse_y
    
    if current_level_index + 1 < len(level_sequence):
        next_rect = pygame.Rect((WIN_W - 250)//2, WIN_H//2, 250, 60)
        hover_next = next_rect.collidepoint(mouse_x, ogl_y)
        draw_beautiful_button(next_rect.x, next_rect.y, next_rect.width, next_rect.height, 
                            " Próxima Fase", (0.2, 0.7, 0.3), hover_next)
   
    menu_y = WIN_H//2 + 80 if current_level_index + 1 < len(level_sequence) else WIN_H//2
    menu_rect = pygame.Rect((WIN_W - 250)//2, menu_y, 250, 60)
    hover_menu = menu_rect.collidepoint(mouse_x, ogl_y)
    draw_beautiful_button(menu_rect.x, menu_rect.y, menu_rect.width, menu_rect.height, 
                        "Voltar ao Menu", (0.7, 0.2, 0.2), hover_menu)

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_game_over():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    glOrtho(0, WIN_W, 0, WIN_H, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    glColor4f(0.05, 0.02, 0.02, 0.9)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WIN_W, 0)
    glVertex2f(WIN_W, WIN_H)
    glVertex2f(0, WIN_H)
    glEnd()

    big_font = pygame.font.SysFont("Arial", 64, bold=True)
    title = "Fim de Jogo!"
    title_surf = big_font.render(title, True, (255, 100, 100))
    data = pygame.image.tostring(title_surf, "RGBA", True)
    glWindowPos2d((WIN_W - title_surf.get_width()) // 2, WIN_H - 150)
    glDrawPixels(title_surf.get_width(), title_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)

    medium_font = pygame.font.SysFont("Arial", 28)
    msg = "Não desista! Tente novamente e ajude o Papai Noel!"
    msg_surf = medium_font.render(msg, True, (255, 200, 200))
    data2 = pygame.image.tostring(msg_surf, "RGBA", True)
    glWindowPos2d((WIN_W - msg_surf.get_width()) // 2, WIN_H - 220)
    glDrawPixels(msg_surf.get_width(), msg_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data2)

    score_text = f"Pontuação Final: {player.score}"
    score_surf = medium_font.render(score_text, True, (255, 255, 150))
    data3 = pygame.image.tostring(score_surf, "RGBA", True)
    glWindowPos2d((WIN_W - score_surf.get_width()) // 2, WIN_H - 270)
    glDrawPixels(score_surf.get_width(), score_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data3)

    # Botões
    mouse_x, mouse_y = pygame.mouse.get_pos()
    ogl_y = WIN_H - mouse_y
    
    retry_rect = pygame.Rect((WIN_W - 300)//2, WIN_H//2, 300, 60)
    hover_retry = retry_rect.collidepoint(mouse_x, ogl_y)
    draw_beautiful_button(retry_rect.x, retry_rect.y, retry_rect.width, retry_rect.height, 
                         "Jogar Novamente", (0.8, 0.5, 0.2), hover_retry)
    
    menu_rect = pygame.Rect((WIN_W - 300)//2, WIN_H//2 + 80, 300, 60)
    hover_menu = menu_rect.collidepoint(mouse_x, ogl_y)
    draw_beautiful_button(menu_rect.x, menu_rect.y, menu_rect.width, menu_rect.height, 
                        "Voltar ao Menu", (0.3, 0.5, 0.8), hover_menu)

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_final_celebration():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    glOrtho(0, WIN_W, 0, WIN_H, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    glColor4f(0.02, 0.05, 0.02, 0.85)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WIN_W, 0)
    glVertex2f(WIN_W, WIN_H)
    glVertex2f(0, WIN_H)
    glEnd()

    big_font = pygame.font.SysFont("Arial", 56, bold=True)
    title = " MISSÃO CUMPRIDA! "
    title_surf = big_font.render(title, True, (100, 255, 100))
    data = pygame.image.tostring(title_surf, "RGBA", True)
    glWindowPos2d((WIN_W - title_surf.get_width()) // 2, WIN_H - 120)
    glDrawPixels(title_surf.get_width(), title_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)

    medium_font = pygame.font.SysFont("Arial", 32)
    msg = " OBRIGADO! AGORA O PAPAI NOEL PODE LEVAR OS PRESENTES PARA AS CRIANÇAS! "
    msg_surf = medium_font.render(msg, True, (255, 255, 200))
    data2 = pygame.image.tostring(msg_surf, "RGBA", True)
    glWindowPos2d((WIN_W - msg_surf.get_width()) // 2, WIN_H - 190)
    glDrawPixels(msg_surf.get_width(), msg_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data2)

    score_text = f"PONTUAÇÃO FINAL: {player.score}"
    score_surf = medium_font.render(score_text, True, (255, 255, 100))
    data3 = pygame.image.tostring(score_surf, "RGBA", True)
    glWindowPos2d((WIN_W - score_surf.get_width()) // 2, WIN_H - 240)
    glDrawPixels(score_surf.get_width(), score_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data3)

    # Botão menu
    mouse_x, mouse_y = pygame.mouse.get_pos()
    ogl_y = WIN_H - mouse_y
    
    menu_rect = pygame.Rect((WIN_W - 300)//2, WIN_H//2, 300, 60)
    hover_menu = menu_rect.collidepoint(mouse_x, ogl_y)
    draw_beautiful_button(menu_rect.x, menu_rect.y, menu_rect.width, menu_rect.height, 
                        " Voltar ao Menu", (0.2, 0.7, 0.3), hover_menu)

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

mouse_left = False
mouse_right = False
last_mouse = (0,0)

left_drag_mode = None  # 'player' or 'camera' or None

def handle_events():
    global mouse_left, mouse_right, last_mouse, left_drag_mode
    global camera_el, camera_az, camera_distance, camera_pan_x, camera_pan_y, paused, show_orbits, wireframe, show_starfield, state
    global current_level_index
    
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit(); raise SystemExit()
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                if state == 'menu':
                    pygame.quit(); raise SystemExit()
                else:
                    set_state_menu()
            elif e.key == K_p:
                paused = not paused
            elif e.key == K_o:
                show_orbits = not show_orbits
            elif e.key == K_w:
                wireframe = not wireframe
            elif e.key == K_s:
                show_starfield = not show_starfield
        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                mouse_left = True
                if state == 'menu':
                    mx,my = e.pos
                    if check_menu_click(mx,my):
                        pass
                elif state == 'level_complete':
                    mx,my = e.pos
                    check_level_complete_click(mx, my)
                elif state == 'gameover':
                    mx,my = e.pos
                    check_game_over_click(mx, my)
                elif state == 'final_celebration':
                    mx,my = e.pos
                    check_final_celebration_click(mx, my)
                elif state == 'playing':
                    left_drag_mode = 'camera'
            elif e.button == 3:
                mouse_right = True
            elif e.button == 4:
                camera_distance -= 3.0
            elif e.button == 5:
                camera_distance += 3.0
            last_mouse = e.pos
        if e.type == MOUSEBUTTONUP:
            if e.button == 1:
                mouse_left = False
                left_drag_mode = None
            elif e.button == 3:
                mouse_right = False
        if e.type == MOUSEMOTION:
            x,y = e.pos
            dx = x - last_mouse[0]; dy = y - last_mouse[1]
            last_mouse = e.pos
            
            if state == 'playing':
                # Mouse sempre controla a câmera durante o jogo
                if mouse_left:
                    camera_el += dx * 0.3
                    camera_az += dy * 0.3
                    camera_az = max(-89.0, min(89.0, camera_az))
                if mouse_right:
                    camera_pan_x += dx * 0.02
                    camera_pan_y -= dy * 0.02
            else:
                if mouse_left:
                    camera_el += dx * 0.3
                    camera_az += dy * 0.3
                    camera_az = max(-89.0, min(89.0, camera_az))
                if mouse_right:
                    camera_pan_x += dx * 0.02
                    camera_pan_y -= dy * 0.02

def check_menu_click(mx,my):
    global state, current_level_index
    bx = (WIN_W - 350) // 2
    by = WIN_H // 2 - 20 
    spacing = 80
    buttons = [(" Marte - Fase 1", "mars"), ("Júpiter - Fase 2", "jupiter"), ("Netuno - Fase 3", "neptune")]
    
    for i,(label,key) in enumerate(buttons):
        y = by - i * spacing
        rect_w, rect_h = 350, 60
        ogl_y = WIN_H - my
        if bx <= mx <= bx+rect_w and y <= ogl_y <= y+rect_h:
            current_level_index = i
            start_level(key)
            return True
    return False

def check_level_complete_click(mx, my):
    global state
    ogl_y = WIN_H - my
  
    if current_level_index + 1 < len(level_sequence):
        next_rect = pygame.Rect((WIN_W - 250)//2, WIN_H//2, 250, 60)
        if next_rect.collidepoint(mx, ogl_y):
            start_next_level()
            return True
    
    menu_y = WIN_H//2 + 80 if current_level_index + 1 < len(level_sequence) else WIN_H//2
    menu_rect = pygame.Rect((WIN_W - 250)//2, menu_y, 250, 60)
    if menu_rect.collidepoint(mx, ogl_y):
        set_state_menu()
        return True
    
    return False

def check_game_over_click(mx, my):
    global state
    ogl_y = WIN_H - my
    
    retry_rect = pygame.Rect((WIN_W - 300)//2, WIN_H//2, 300, 60)
    if retry_rect.collidepoint(mx, ogl_y):
        start_level(level_sequence[current_level_index])
        return True
 
    menu_rect = pygame.Rect((WIN_W - 300)//2, WIN_H//2 + 80, 300, 60)
    if menu_rect.collidepoint(mx, ogl_y):
        set_state_menu()
        return True
    
    return False

def check_final_celebration_click(mx, my):
    global state
    ogl_y = WIN_H - my
    
    menu_rect = pygame.Rect((WIN_W - 300)//2, WIN_H//2, 300, 60)
    if menu_rect.collidepoint(mx, ogl_y):
        set_state_menu()
        return True
    
    return False

def set_state_menu():
    global state, current_level_index
    state = 'menu'
    current_level_index = 0

last_time = time.time()
def update_global(dt):
    global earth_rotation
    if not paused:
        for name in orbit_speeds:
            angles[name] = (angles.get(name,0.0) + orbit_speeds[name] * dt * 10.0) % 360.0
        for name in spin_speeds:
            spins[name] = (spins.get(name,0.0) + spin_speeds[name] * dt * 50.0) % 360.0
        angles['moon'] = (angles.get('moon',0.0) + 0.6 * dt * 60.0) % 360.0
        
        # Atualizar rotação da Terra na celebração final
        if state == 'final_celebration':
            earth_rotation += dt * 30.0  

def main():
    global last_time, fps, frames, fps_time, state

    running = True
    while running:
        now = time.time()
        dt = now - last_time
        last_time = now

        handle_events()
        if state == 'playing' and not paused:
            keys = pygame.key.get_pressed()
            move_dx = 0.0; move_dz = 0.0
            speed = player.move_speed * dt
        
            if keys[K_a] or keys[K_LEFT]:
                move_dx -= speed
            if keys[K_d] or keys[K_RIGHT]:
                move_dx += speed
            
            if keys[K_w] or keys[K_UP]:
                move_dz += speed  # W/Up move para frente (Z negativo)
            if keys[K_s] or keys[K_DOWN]:
                move_dz -= speed  # S/Down move para trás (Z positivo)
            
            if move_dx != 0.0 or move_dz != 0.0:
                player.move_by(move_dx, move_dz)

        update_global(dt)
        update_game(dt)
        
        if state == 'final_celebration':
            update_confetti(dt)

        # Modo wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)

        # Renderiza cena 3D
        render_scene()

        # Overlay 2D conforme o estado do jogo
        if state == 'menu':
            draw_menu()
        elif state == 'playing':
            draw_hud()
        elif state == 'level_complete':
            draw_level_complete()
        elif state == 'gameover':
            draw_game_over()
        elif state == 'final_celebration':
            draw_final_celebration()

        frames += 1
        if time.time() - fps_time >= 1.0:
            fps = frames
            frames = 0
            fps_time = time.time()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()