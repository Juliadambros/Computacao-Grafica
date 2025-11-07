from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys, math

angulo_braco = 0
angulo_garra = 30

distance = 22.0
azimuth = 40.0
incidence = 25.0
twist = 0.0

target_distance = distance
target_azimuth = azimuth
target_incidence = incidence
target_twist = twist

mouse_last_x = 0
mouse_last_y = 0
mouse_left = False
mouse_right = False

pan_x = 0
pan_y = 0
pan_target_x = 0
pan_target_y = 0

projecao_ortografica = False
rotacao_grade = 0 

def suavizar(valor, alvo, fator=0.15):
    return valor + (alvo - valor) * fator

def desenhaCeu():
    glDisable(GL_LIGHTING)
    glBegin(GL_QUADS)

    glColor3f(0.1, 0.3, 0.9)
    glVertex3f(-100, -10, -80)
    glVertex3f(100, -10, -80)

    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(100, 80, -120)
    glVertex3f(-100, 80, -120)

    glEnd()
    glEnable(GL_LIGHTING)

def desenhaChao():
    glPushMatrix()

    glRotatef(rotacao_grade, 1, 0, 0)

    glBegin(GL_LINES)

    tamanho = 40
    for i in range(-tamanho, tamanho+1):
        glColor3f(0.7, 0.7, 0.7)

        glVertex3f(i, 0, -tamanho)
        glVertex3f(i, 0, tamanho)

        glVertex3f(-tamanho, 0, i)
        glVertex3f(tamanho, 0, i)

    glEnd()

    glPopMatrix()


def caixa(dx, dy, dz, r, g, b):
    glPushMatrix()
    glColor3f(r, g, b)
    glTranslatef(dx/2, 0, 0)
    glScalef(dx, dy, dz)
    glutSolidCube(1)
    glPopMatrix()


def desenhaGarra():
    global angulo_garra

    glPushMatrix()

    caixa(2, 0.4, 1, 0.8, 0.3, 0.3)

    glPushMatrix()
    glTranslatef(2, 0, 0)
    glRotatef(angulo_garra, 0, 0, 1)
    caixa(2, 0.4, 1, 0.3, 0.9, 0.9)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(2, 0, 0)
    glRotatef(-angulo_garra, 0, 0, 1)
    caixa(2, 0.4, 1, 0.9, 0.3, 0.9)
    glPopMatrix()

    glPopMatrix()


def desenhaBraco():
    glPushMatrix()

    glColor3f(0.5, 0.5, 0.5)
    glutSolidCube(1)

    glTranslatef(0.5, 0, 0)
    glRotatef(angulo_braco, 0, 1, 0)

    caixa(3, 0.3, 0.3, 1, 0.3, 0.3)

    glTranslatef(3, 0, 0)
    desenhaGarra()

    glPopMatrix()


def aplicarCamera():

    global distance, azimuth, incidence, twist
    global pan_x, pan_y

    distance = suavizar(distance, target_distance)
    azimuth = suavizar(azimuth, target_azimuth)
    incidence = suavizar(incidence, target_incidence)
    twist = suavizar(twist, target_twist)
    pan_x = suavizar(pan_x, pan_target_x)
    pan_y = suavizar(pan_y, pan_target_y)

    az = math.radians(azimuth)
    inc = math.radians(incidence)

    eye_x = distance * math.cos(inc) * math.sin(az) + pan_x
    eye_y = distance * math.sin(inc) + pan_y
    eye_z = distance * math.cos(inc) * math.cos(az)

    glRotatef(twist, 0, 0, 1)

    gluLookAt(
        eye_x, eye_y, eye_z,
        pan_x, pan_y, 0,
        0, 1, 0
    )

def escreverTexto(x, y, texto):
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for c in texto:
        glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(c)) # type: ignore

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    aplicarCamera()

    desenhaCeu()
    desenhaChao()
    desenhaBraco()

    escreverTexto(10, 570, f"distance = {distance:.1f}")
    escreverTexto(10, 550, f"azimuth = {azimuth:.1f}")
    escreverTexto(10, 530, f"incidence = {incidence:.1f}")
    escreverTexto(10, 510, f"twist = {twist:.1f}")

    glutSwapBuffers()
    glutPostRedisplay()


def keyboard(key, x, y):
    global angulo_garra, angulo_braco, projecao_ortografica
    global rotacao_grade

    if key == b'a':
        angulo_garra = min(60, angulo_garra + 2)
    elif key == b's':
        angulo_garra = max(0, angulo_garra - 2)
    elif key == b'j':
        angulo_braco += 5
    elif key == b'l':
        angulo_braco -= 5
    elif key == b'p':  
        projecao_ortografica = not projecao_ortografica
        aplicarProjecao()
    elif key == b'x':  
        rotacao_grade += 5
    elif key == b'\x1b':
        sys.exit(0)


def aplicarProjecao():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if projecao_ortografica:
        glOrtho(-20, 20, -20, 20, 1, 200)
    else:
        gluPerspective(60, 1, 1, 200)
    glMatrixMode(GL_MODELVIEW)


def mouse(button, state, x, y):
    global mouse_left, mouse_right, mouse_last_x, mouse_last_y

    mouse_left = (button == GLUT_LEFT_BUTTON and state == GLUT_DOWN)
    mouse_right = (button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN)

    mouse_last_x = x
    mouse_last_y = y


def motion(x, y):
    global mouse_last_x, mouse_last_y
    global target_azimuth, target_incidence
    global target_twist, pan_target_x, pan_target_y

    dx = x - mouse_last_x
    dy = y - mouse_last_y

    mods = glutGetModifiers()

    if mouse_left:
        if mods == GLUT_ACTIVE_SHIFT:
            target_twist += dx * 0.3
        else:
            target_azimuth += dx * 0.4
            target_incidence -= dy * 0.4

    if mouse_right:
        if mods == GLUT_ACTIVE_SHIFT:
            pan_target_x += dx * 0.05
            pan_target_y += dy * 0.05

    mouse_last_x = x
    mouse_last_y = y


def mouseWheel(button, dir, x, y):
    global target_distance
    target_distance -= dir * 1.5
    target_distance = max(5, min(80, target_distance))


def init():
    glClearColor(0.4, 0.7, 1, 1)
    aplicarProjecao()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [10, 20, 10, 1])


glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(800, 600)
glutCreateWindow(b"Garra")

init()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
glutMotionFunc(motion)
glutMouseWheelFunc(mouseWheel)

glutMainLoop()
