#Ana Júlia e Júlia

import os, math, random, time
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

pygame.init()
WIN_W, WIN_H = 1200, 800
screen = pygame.display.set_mode((WIN_W, WIN_H), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Sistema Solar")
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

camera_distance = 70.0
camera_az = 25.0
camera_el = -25.0
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

def display():
    global frames, fps, fps_time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glTranslatef(-camera_pan_x, -camera_pan_y, -camera_distance)
    glRotatef(camera_az,1,0,0)
    glRotatef(camera_el,0,1,0)

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
            segs = 120
            for i in range(segs):
                theta = 2.0*math.pi*i/segs
                glVertex3f(math.cos(theta)*r, 0.0, math.sin(theta)*r)
            glEnd()
        glEnable(GL_LIGHTING)

    if wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    order = ['mercury','venus','earth','mars','jupiter','saturn','uranus','neptune']
    for name in order:
        glPushMatrix()
        glRotatef(angles.get(name, 0.0), 0, 1, 0)
        r = orbit_radii.get(name, 0.0)
        glTranslatef(r, 0, 0)
        glRotatef(spins.get(name, 0.0), 0, 1, 0)
        glRotatef(90, 0, 1, 0)
        draw_sphere(planet_scales[name], textures.get(name,0), slices=48, stacks=48)
        if name == 'saturn':
            glPushMatrix()
            glRotatef(25,1,0,0)
            # o anel usa textura com alpha (se tiver)
            draw_ring(planet_scales['saturn']*1.05, planet_scales['saturn']*2.8, textures.get('saturn_ring'), segments=120)
            glPopMatrix()
        glPopMatrix()

    glPushMatrix()
    glRotatef(angles['earth'],0,1,0)
    glTranslatef(orbit_radii['earth'],0,0)
    glRotatef(spins['earth'],0,1,0)
    glRotatef(90,0,1,0)
    glPushMatrix()
    glRotatef((angles.get('moon',0.0)*12.0)%360, 0,1,0)
    glTranslatef(1.6 + planet_scales['earth'], 0, 0)
    glRotatef(spins.get('moon',0.0), 0,1,0)
    draw_sphere(planet_scales['moon'], textures.get('moon',0), slices=24, stacks=24)
    glPopMatrix()
    glPopMatrix()

    pygame.display.flip()

    # FPS
    frames += 1
    if time.time() - fps_time >= 1.0:
        global fps
        fps = frames / max(0.0001, time.time() - fps_time)
        frames = 0
        globals()['fps_time'] = time.time()

last_time = time.time()
def update(dt):
    if not paused:
        for name in orbit_speeds:
            angles[name] = (angles.get(name,0.0) + orbit_speeds[name] * dt * 10.0) % 360.0
        for name in spin_speeds:
            spins[name] = (spins.get(name,0.0) + spin_speeds[name] * dt * 50.0) % 360.0
        angles['moon'] = (angles.get('moon',0.0) + 0.6 * dt * 60.0) % 360.0

mouse_left = False
mouse_right = False
last_mouse = (0,0)

def handle_events():
    global mouse_left, mouse_right, last_mouse
    global camera_el, camera_az, camera_distance, camera_pan_x, camera_pan_y, paused, show_orbits, wireframe, show_starfield
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit(); raise SystemExit()
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                pygame.quit(); raise SystemExit()
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
            elif e.button == 3:
                mouse_right = False
        if e.type == MOUSEMOTION:
            x,y = e.pos
            dx = x - last_mouse[0]; dy = y - last_mouse[1]
            last_mouse = e.pos
            if mouse_left:
                camera_el += dx * 0.3
                camera_az += dy * 0.3
                camera_az = max(-89.0, min(89.0, camera_az))
            if mouse_right:
                camera_pan_x += dx * 0.02
                camera_pan_y -= dy * 0.02

try:
    while True:
        dt = clock.tick(60) / 1000.0
        handle_events()
        update(dt)
        display()
except SystemExit:
    pass