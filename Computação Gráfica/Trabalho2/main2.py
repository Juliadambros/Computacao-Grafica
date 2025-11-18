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

GRID_COLS = 8
GRID_ROWS = 5
GRID_CELL_WIDTH = 6.0
GRID_CELL_DEPTH = 6.0

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
show_grid = False   #aqui para vizulizar o grid

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
        self.grid_x = 3
        self.grid_z = 2
        self.y = -8.0
        self.width = 4.0
        self.radius = 3.5 
        self.score = 0
        self.lives = 3
        self.move_cooldown = 0.0
        
        self.min_x = -((GRID_COLS * GRID_CELL_WIDTH) / 2)
        self.max_x = ((GRID_COLS * GRID_CELL_WIDTH) / 2)
        self.min_z = -((GRID_ROWS * GRID_CELL_DEPTH) / 2) - 5.0
        self.max_z = ((GRID_ROWS * GRID_CELL_DEPTH) / 2) - 5.0
        
        self.update_position_from_grid()
    
    def update_position_from_grid(self):
        self.x = (self.grid_x - (GRID_COLS-1)/2) * GRID_CELL_WIDTH
        self.z = (self.grid_z - (GRID_ROWS-1)/2) * GRID_CELL_DEPTH - 10.0
    
    def move_grid(self, dx, dz):
        new_x = max(0, min(GRID_COLS-1, self.grid_x + dx))
        new_z = max(0, min(GRID_ROWS-1, self.grid_z + dz))
        
        if new_x != self.grid_x or new_z != self.grid_z:
            self.grid_x = new_x
            self.grid_z = new_z
            self.update_position_from_grid()
            return True
        return False
    
    def get_grid_position(self):
        return (self.grid_x, self.grid_z)

player = Player()

state = 'menu'  
current_planet = None
objects = []
spawn_timer = 0.0

completed_levels = []
current_level_index = 0
level_sequence = ['mars', 'jupiter', 'neptune']

confetti_particles = []
earth_rotation = 0.0

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
    
    player.grid_x = 3
    player.grid_z = 2
    player.update_position_from_grid()
    
    state = 'level_intro'

def end_level(won):
    global state, completed_levels, current_level_index, confetti_particles, earth_rotation
    if won:
        if current_planet not in completed_levels:
            completed_levels.append(current_planet)
        state = 'level_complete'
    else:
        state = 'gameover'

def debug_state():
    print(f"DEBUG - Estado: {state}, Fase Atual: {current_level_index}, Total Fases: {len(level_sequence)}")
    print(f"DEBUG - Fase atual na sequência: {level_sequence[current_level_index] if current_level_index < len(level_sequence) else 'NONE'}")

def start_next_level():
    global current_level_index, confetti_particles, earth_rotation, state

    print(f"DEBUG: start_next_level() chamado. current_level_index antes: {current_level_index}")
    
    current_level_index += 1

    if current_level_index < len(level_sequence):
        print(f"DEBUG: Iniciando próxima fase: {level_sequence[current_level_index]}")
        start_level(level_sequence[current_level_index])
    else:
        print("DEBUG: ERRO - Tentou iniciar fase além do limite!")
        state = 'final_celebration'
        earth_rotation = 0.0
        create_confetti()

def create_confetti():
    global confetti_particles
    confetti_particles = []
    for _ in range(300):  
        confetti_particles.append({
            'x': random.uniform(-50, 50),
            'y': random.uniform(-30, 60),
            'z': random.uniform(-50, 50),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-1, -5),
            'vz': random.uniform(-2, 2),
            'color': random.choice([
                (1.0, 0.0, 0.0),   
                (0.0, 1.0, 0.0),    
                (0.0, 0.0, 1.0),    
                (1.0, 1.0, 0.0),    
                (1.0, 0.0, 1.0),    
                (0.0, 1.0, 1.0),  
                (1.0, 0.5, 0.0), 
                (0.5, 0.0, 1.0),    
                (1.0, 1.0, 1.0),   
                (1.0, 0.8, 0.0)     
            ]),
            'size': random.uniform(0.1, 0.4),
            'rotation': random.uniform(0, 360),
            'rotation_speed': random.uniform(-8, 8),
            'shape': random.choice(['square', 'circle', 'star'])
        })

def update_confetti(dt):
    global confetti_particles
    for confetti in confetti_particles:
        confetti['x'] += confetti['vx'] * dt
        confetti['y'] += confetti['vy'] * dt
        confetti['z'] += confetti['vz'] * dt
        confetti['rotation'] += confetti['rotation_speed'] * dt
        
        confetti['vy'] -= 5.0 * dt
        
        if confetti['y'] < -40:
            confetti['y'] = 60
            confetti['x'] = random.uniform(-50, 50)
            confetti['z'] = random.uniform(-50, 50)
            confetti['vy'] = random.uniform(-1, -5)
            confetti['vx'] = random.uniform(-2, 2)
            confetti['vz'] = random.uniform(-2, 2)

def spawn_present(fall_speed):
    grid_x = random.randint(0, GRID_COLS-1)

    x = (grid_x - (GRID_COLS-1)/2) * GRID_CELL_WIDTH
    
    grid_z = random.randint(0, GRID_ROWS-1)
    z = (grid_z - (GRID_ROWS-1)/2) * GRID_CELL_DEPTH - 10.0
    
    y = random.uniform(25.0, 40.0)
    
    vx = random.uniform(-0.5, 0.5)
    vy = fall_speed
    vz = random.uniform(-0.3, 0.3)
    
    o = FallingObject((x,y,z),(vx,vy,vz),'present')
    objects.append(o)

def spawn_meteor(fall_speed):
    grid_x = random.randint(0, GRID_COLS-1)
    
    x = (grid_x - (GRID_COLS-1)/2) * GRID_CELL_WIDTH
    grid_z = random.randint(0, GRID_ROWS-1)
    z = (grid_z - (GRID_ROWS-1)/2) * GRID_CELL_DEPTH - 10.0
    y = random.uniform(35.0, 50.0)
    
    vx = random.uniform(-1.0, 1.0)
    vy = fall_speed * 1.3
    vz = random.uniform(-0.8, 0.8)
    
    o = FallingObject((x,y,z),(vx,vy,vz),'meteor')
    objects.append(o)

def spawn_meteor(fall_speed):
    grid_x = random.randint(0, GRID_COLS-1)
    
    x = (grid_x - (GRID_COLS-1)/2) * GRID_CELL_WIDTH
    z = -((GRID_ROWS * GRID_CELL_DEPTH) / 2) - 5.0  
    y = random.uniform(35.0, 50.0)
    
    vx, vy, vz = 0, fall_speed*1.3, 0
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
        
        dist_3d = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        obj_grid_x = int(round((o.x / GRID_CELL_WIDTH) + (GRID_COLS-1)/2))
        obj_grid_z = int(round((o.z / GRID_CELL_DEPTH) + (GRID_ROWS-1)/2))
        
        collision_by_grid = (obj_grid_x == player.grid_x and 
                           obj_grid_z == player.grid_z and 
                           abs(o.y - player.y) < 10.0)  
        
        collision_by_distance = (dist_3d < (o.radius + player.radius + 2.0)) 
        
        if collision_by_grid or collision_by_distance:
            if o.kind == 'present' and not o.collected:
                level_collected += 1
                player.score += 10
                o.collected = True
                to_remove.append(o)
                print(f"Presente coletado! Total: {level_collected}/{level_goal}")  
            elif o.kind == 'meteor' and not o.collected:
                player.lives -= 1
                o.collected = True
                to_remove.append(o)
                print(f"Meteoro! Vidas: {player.lives}")  

    for o in to_remove:
        if o in objects:
            objects.remove(o)

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
    draw_text_2d(400, WIN_H-30, f"Position: ({player.grid_x}, {player.grid_z})")
    draw_text_2d(550, WIN_H-30, f"Objects: {len(objects)}") 
    
    if len(objects) > 0:
        first_obj = objects[0]
        draw_text_2d(10, WIN_H-60, f"Obj0: ({first_obj.x:.1f}, {first_obj.y:.1f}, {first_obj.z:.1f})")
        obj_grid_x = int(round((first_obj.x / GRID_CELL_WIDTH) + (GRID_COLS-1)/2))
        obj_grid_z = int(round((first_obj.z / GRID_CELL_DEPTH) + (GRID_ROWS-1)/2))
        draw_text_2d(10, WIN_H-90, f"Obj0 Grid: ({obj_grid_x}, {obj_grid_z})")

    if planet_configs[current_planet]['time_limit'] > 0:
        draw_text_2d(750, WIN_H-30, f"Time left: {int(level_time_left)}s")
    
    if current_planet != 'mars':
        draw_text_2d(900, WIN_H-30, f"Lives: {player.lives}")

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
        
        if confetti['shape'] == 'circle':
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0, 0)
            for i in range(13):
                angle = 2 * math.pi * i / 12
                glVertex3f(math.cos(angle) * size, math.sin(angle) * size, 0)
            glEnd()
        elif confetti['shape'] == 'star':
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0, 0)
            for i in range(11):
                angle = 2 * math.pi * i / 10
                radius = size if i % 2 == 0 else size * 0.4
                glVertex3f(math.cos(angle) * radius, math.sin(angle) * radius, 0)
            glEnd()
        else:
            glBegin(GL_QUADS)
            glVertex3f(-size, -size, 0)
            glVertex3f(size, -size, 0)
            glVertex3f(size, size, 0)
            glVertex3f(-size, size, 0)
            glEnd()
        
        glPopMatrix()
    glEnable(GL_LIGHTING)

def draw_grid():
    if not show_grid:
        return
        
    glDisable(GL_LIGHTING)
    glColor3f(0.3, 0.3, 0.3)
    glLineWidth(1.0)
    
    for col in range(GRID_COLS + 1):
        x = (col - GRID_COLS/2) * GRID_CELL_WIDTH
        glBegin(GL_LINES)
        glVertex3f(x, -12, player.min_z)
        glVertex3f(x, -12, player.max_z)
        glEnd()
    
    for row in range(GRID_ROWS + 1):
        z = (row - GRID_ROWS/2) * GRID_CELL_DEPTH - 10.0
        glBegin(GL_LINES)
        glVertex3f(player.min_x, -12, z)
        glVertex3f(player.max_x, -12, z)
        glEnd()
    
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
        draw_grid() 
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


def draw_beautiful_button(x, y, width, height, text, color=(0.2,0.6,0.8), hover=False):
    base = 0.45 if not hover else 0.65
    glBegin(GL_QUADS)
    glColor3f(base, base, base)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glColor3f(0.85, 0.85, 0.85)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

    btn_font = pygame.font.SysFont("Arial", 24, bold=True)
    text_surf = btn_font.render(text, True, (255,255,255))
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

    glColor4f(0.03, 0.03, 0.06, 0.9)
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

    instruction_font = pygame.font.SysFont("Arial", 18)
    instructions = [
        "PRECISAMOS DE SUA AJUDA PARA RECUPERAR OS PRESENTES QUE CAÍRAM DA NAVE!",
        "Utilize as setas ou WASD para movimentar o trenó e passe as fases.",
        "Evite meteoros e colete o número de presentes necessários em cada fase.",
    ]
    for i, instruction in enumerate(instructions):
        inst_surf = instruction_font.render(instruction, True, (255, 255, 200))
        inst_data = pygame.image.tostring(inst_surf, "RGBA", True)
        glWindowPos2d((WIN_W - inst_surf.get_width()) // 2, WIN_H - 240 - i * 26)
        glDrawPixels(inst_surf.get_width(), inst_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, inst_data)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    ogl_y = WIN_H - mouse_y

    bx = (WIN_W - 350) // 2
    by = WIN_H // 2 - 30  
    
    hover = (bx <= mouse_x <= bx + 350 and by <= ogl_y <= by + 60)
    draw_beautiful_button(bx, by, 350, 60, "COMEÇAR MISSÃO", hover=hover)

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_level_intro():
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

    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    planet_names = {'mars': 'MARTE', 'jupiter': 'JÚPITER', 'neptune': 'NETUNO'}
    title_text = f"FASE {current_level_index + 1} - {planet_names[current_planet]}"
    title_surf = title_font.render(title_text, True, (255, 255, 150))
    glWindowPos2d((WIN_W - title_surf.get_width()) // 2, WIN_H - 120)
    glDrawPixels(title_surf.get_width(), title_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, 
                pygame.image.tostring(title_surf, "RGBA", True))

    instruction_font = pygame.font.SysFont("Arial", 24)
    instructions = []
    
    if current_planet == 'mars':
        instructions = [
            "OBJETIVO: Colete 3 presentes!",
            "Esta é sua primeira missão. Aprenda a controlar o trenó:",
            "- Use WASD ou SETAS para se mover no grid 8x5",
            "- Mouse para rotacionar a câmera", 
            "- Cuidado: Você tem apenas 30 segundos!",
            "Foco na velocidade e precisão!"
        ]
    elif current_planet == 'jupiter':
        instructions = [
            "OBJETIVO: Colete 5 presentes!",
            "ALERTA: Meteoros apareceram!",
            "- Meteoros reduzem sua vida em 1 ponto",
            "- Movimente-se rapidamente para evitá-los",
            "- Fique atento aos padrões de queda",
            "Sem tempo limite, mas tome cuidado!"
        ]
    elif current_planet == 'neptune':
        instructions = [
            "OBJETIVO: Colete 6 presentes!",
            "FASE FINAL - Dificuldade máxima!",
            "- Meteoros em maior quantidade", 
            "- Presentes caem mais rápido",
            "- Movimentação mais desafiadora",
            "Mostre que você é o melhor ajudante do Papai Noel!"
        ]

    for i, instruction in enumerate(instructions):
        inst_surf = instruction_font.render(instruction, True, (200, 200, 255))
        glWindowPos2d((WIN_W - inst_surf.get_width()) // 2, WIN_H - 200 - i * 35)
        glDrawPixels(inst_surf.get_width(), inst_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE,
                    pygame.image.tostring(inst_surf, "RGBA", True))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    ogl_y = WIN_H - mouse_y
    start_rect = pygame.Rect((WIN_W - 300)//2, WIN_H//2 - 50, 300, 60)
    hover_start = start_rect.collidepoint(mouse_x, ogl_y)
    
    draw_beautiful_button(start_rect.x, start_rect.y, start_rect.width, start_rect.height,
                         "COMEÇAR MISSÃO", hover=hover_start)

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
    
    is_last_level = (current_level_index == len(level_sequence) - 1)
    
    if is_last_level:
        msg = "TODAS AS FASES CONCLUÍDAS!"
        color = (100, 255, 100)  
    else:
        msg = f"Fase {current_level_index + 1} Concluída!"
        color = (100, 255, 100)
        
    surf = big_font.render(msg, True, color)
    data = pygame.image.tostring(surf, "RGBA", True)
    glWindowPos2d((WIN_W - surf.get_width()) // 2, WIN_H - 150)
    glDrawPixels(surf.get_width(), surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)

    medium_font = pygame.font.SysFont("Arial", 32)
    score_text = f"Pontuação: {player.score}"
    score_surf = medium_font.render(score_text, True, (255, 255, 100))
    data2 = pygame.image.tostring(score_surf, "RGBA", True)
    glWindowPos2d((WIN_W - score_surf.get_width()) // 2, WIN_H - 220)
    glDrawPixels(score_surf.get_width(), score_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data2)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    ogl_y = WIN_H - mouse_y
    
    if not is_last_level:
        next_text = "Próxima Fase"
    else:
        next_text = "Celebração Final!"
    
    if current_level_index + 1 <= len(level_sequence):
        next_rect = pygame.Rect((WIN_W - 250)//2, WIN_H//2, 250, 60)
        hover_next = next_rect.collidepoint(mouse_x, ogl_y)
        draw_beautiful_button(next_rect.x, next_rect.y, next_rect.width, next_rect.height, 
                            next_text, (0.2, 0.7, 0.3), hover_next)
   
    menu_y = WIN_H//2 + 80 if current_level_index + 1 <= len(level_sequence) else WIN_H//2
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

    glColor4f(0, 0, 0, 0.90)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WIN_W, 0)
    glVertex2f(WIN_W, WIN_H)
    glVertex2f(0, WIN_H)
    glEnd()

    mouse_x, mouse_y = pygame.mouse.get_pos()
    ogl_y = WIN_H - mouse_y

    button_w = 320
    button_h = 60
    button_x = (WIN_W - button_w) // 2

    retry_y = WIN_H//2 - 40
    retry_rect = pygame.Rect(button_x, retry_y, button_w, button_h)
    hover_retry = retry_rect.collidepoint(mouse_x, ogl_y)
    draw_beautiful_button(button_x, retry_y, button_w, button_h,
                          "Jogar Novamente", hover_retry)

    menu_y = retry_y - 80
    menu_rect = pygame.Rect(button_x, menu_y, button_w, button_h)
    hover_menu = menu_rect.collidepoint(mouse_x, ogl_y)
    draw_beautiful_button(button_x, menu_y, button_w, button_h,
                          "Voltar ao Menu", hover_menu)

    title_font = pygame.font.SysFont("Arial", 64, bold=True)
    title_surf = title_font.render("Fim de Jogo!", True, (255, 100, 100))
    title_data = pygame.image.tostring(title_surf, "RGBA", True)
    glWindowPos2d((WIN_W - title_surf.get_width()) // 2, WIN_H - 180)
    glDrawPixels(title_surf.get_width(), title_surf.get_height(),
                 GL_RGBA, GL_UNSIGNED_BYTE, title_data)

    medium_font = pygame.font.SysFont("Arial", 28)
    msg_surf = medium_font.render(
        "Não desista! Tente novamente e ajude o Papai Noel!",
        True, (255, 200, 200))
    msg_data = pygame.image.tostring(msg_surf, "RGBA", True)
    glWindowPos2d((WIN_W - msg_surf.get_width()) // 2, WIN_H - 240)
    glDrawPixels(msg_surf.get_width(), msg_surf.get_height(),
                 GL_RGBA, GL_UNSIGNED_BYTE, msg_data)

    # Pontuação
    score_surf = medium_font.render(
        f"Pontuação Final: {player.score}",
        True, (255, 255, 120))
    score_data = pygame.image.tostring(score_surf, "RGBA", True)
    glWindowPos2d((WIN_W - score_surf.get_width()) // 2, WIN_H - 280)
    glDrawPixels(score_surf.get_width(), score_surf.get_height(),
                 GL_RGBA, GL_UNSIGNED_BYTE, score_data)

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

    glColor4f(0.02, 0.02, 0.05, 0.7)  
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WIN_W, 0)
    glVertex2f(WIN_W, WIN_H)
    glVertex2f(0, WIN_H)
    glEnd()

    big_font = pygame.font.SysFont("Arial", 72, bold=True)
    title = "MISSÃO CUMPRIDA!"
    title_surf = big_font.render(title, True, (255, 255, 150))
    data = pygame.image.tostring(title_surf, "RGBA", True)
    glWindowPos2d((WIN_W - title_surf.get_width()) // 2, WIN_H - 140)
    glDrawPixels(title_surf.get_width(), title_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)

    medium_font = pygame.font.SysFont("Arial", 36)
    msg = "O Natal está salvo! Você é um verdadeiro herói!"
    msg_surf = medium_font.render(msg, True, (200, 255, 200))
    data2 = pygame.image.tostring(msg_surf, "RGBA", True)
    glWindowPos2d((WIN_W - msg_surf.get_width()) // 2, WIN_H - 220)
    glDrawPixels(msg_surf.get_width(), msg_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data2)

    score_font = pygame.font.SysFont("Arial", 42, bold=True)
    score_text = f"PONTUAÇÃO FINAL: {player.score} PONTOS"
    score_surf = score_font.render(score_text, True, (255, 255, 100))
    data3 = pygame.image.tostring(score_surf, "RGBA", True)
    glWindowPos2d((WIN_W - score_surf.get_width()) // 2, WIN_H - 290)
    glDrawPixels(score_surf.get_width(), score_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data3)

    thanks_font = pygame.font.SysFont("Arial", 24, italic=True)
    thanks_text = "O Papai Noel e todas as crianças agradecem sua bravura!"
    thanks_surf = thanks_font.render(thanks_text, True, (255, 200, 200))
    data4 = pygame.image.tostring(thanks_surf, "RGBA", True)
    glWindowPos2d((WIN_W - thanks_surf.get_width()) // 2, WIN_H - 340)
    glDrawPixels(thanks_surf.get_width(), thanks_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data4)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    ogl_y = WIN_H - mouse_y
    menu_rect = pygame.Rect((WIN_W - 350)//2, WIN_H//2 - 30, 350, 70)
    hover_menu = menu_rect.collidepoint(mouse_x, ogl_y)
    
    draw_beautiful_button(menu_rect.x, menu_rect.y, menu_rect.width, menu_rect.height,
                         "VOLTAR AO MENU PRINCIPAL", hover=hover_menu)

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

left_drag_mode = None  

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

def handle_events():
    global mouse_left, mouse_right, last_mouse, left_drag_mode
    global camera_el, camera_az, camera_distance, camera_pan_x, camera_pan_y, paused, show_orbits, wireframe, show_starfield, state, show_grid
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
            elif e.key == K_g:  
                show_grid = not show_grid
        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                mouse_left = True
                if state == 'menu':
                    mx,my = e.pos
                    if check_menu_click(mx,my):
                        pass
                elif state == 'level_intro':
                    mx,my = e.pos
                    check_level_intro_click(mx, my)
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
    by = WIN_H // 2 - 30  
    
    ogl_y = WIN_H - my
    
    if bx <= mx <= bx + 350 and by <= ogl_y <= by + 60:
        current_level_index = 0
        start_level('mars')
        return True
    
    return False

def check_level_intro_click(mx, my):
    global state
    ogl_y = WIN_H - my
    
    start_rect = pygame.Rect((WIN_W - 300)//2, WIN_H//2 - 50, 300, 60)
    if start_rect.collidepoint(mx, ogl_y):
        state = 'playing'
        return True
    
    return False

def check_level_complete_click(mx, my):
    global state, current_level_index
    ogl_y = WIN_H - my
    
    print(f"DEBUG: check_level_complete_click - current_level_index: {current_level_index}, level_sequence: {level_sequence}")
    
    is_last_level = (current_level_index == len(level_sequence) - 1)
    print(f"DEBUG: É última fase? {is_last_level}")
    
    if not is_last_level:
        next_rect = pygame.Rect((WIN_W - 250)//2, WIN_H//2, 250, 60)
        if next_rect.collidepoint(mx, ogl_y):
            print("DEBUG: Clique em 'Próxima Fase'")
            start_next_level()
            return True
    else:
        if check_final_celebration_available():
            next_rect = pygame.Rect((WIN_W - 250)//2, WIN_H//2, 250, 60)
            if next_rect.collidepoint(mx, ogl_y):
                print("DEBUG: Todas as fases completadas em sequência! Indo para celebração final")
                state = 'final_celebration'
                earth_rotation = 0.0
                create_confetti()
                return True
    
    menu_y = WIN_H//2 + 80 if not is_last_level else WIN_H//2
    menu_rect = pygame.Rect((WIN_W - 250)//2, menu_y, 250, 60)
    if menu_rect.collidepoint(mx, ogl_y):
        print("DEBUG: Clique em 'Voltar ao Menu'")
        set_state_menu()
        return True
    
    return False

def check_final_celebration_click(mx, my):
    global state
    ogl_y = WIN_H - my
    
    menu_rect = pygame.Rect((WIN_W - 350)//2, WIN_H//2 - 30, 350, 70)
    if menu_rect.collidepoint(mx, ogl_y):
        set_state_menu()
        return True
    
    return False

def set_state_menu():
    global state, current_level_index
    state = 'menu'

def check_final_celebration_available():
    return len(completed_levels) == len(level_sequence)

last_time = time.time()
def update_global(dt):
    global earth_rotation
    if not paused:
        for name in orbit_speeds:
            angles[name] = (angles.get(name,0.0) + orbit_speeds[name] * dt * 10.0) % 360.0
        for name in spin_speeds:
            spins[name] = (spins.get(name,0.0) + spin_speeds[name] * dt * 50.0) % 360.0
        angles['moon'] = (angles.get('moon',0.0) + 0.6 * dt * 60.0) % 360.0
        
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
            
            player.move_cooldown -= dt
            
            if player.move_cooldown <= 0:
                moved = False
                if keys[K_a] or keys[K_LEFT]:
                    if player.move_grid(-1, 0):
                        moved = True
                if keys[K_d] or keys[K_RIGHT]:
                    if player.move_grid(1, 0):
                        moved = True
                if keys[K_w] or keys[K_UP]:
                    if player.move_grid(0, -1):
                        moved = True
                if keys[K_s] or keys[K_DOWN]:
                    if player.move_grid(0, 1):
                        moved = True
                
                if moved:
                    player.move_cooldown = 0.2  

        update_global(dt)
        update_game(dt)
        
        if state == 'final_celebration':
            update_confetti(dt)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)

        render_scene()

        if state == 'menu':
            draw_menu()
        elif state == 'level_intro':
            draw_level_intro()
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