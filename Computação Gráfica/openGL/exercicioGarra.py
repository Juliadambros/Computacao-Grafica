from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

angulo_braco = 0
angulo_garra = 30

def solidBox(dx, dy, dz, r, g, b):
    glPushMatrix()
    glColor3f(r, g, b)
    glTranslatef(dx / 2, 0, 0)
    glScalef(dx, dy, dz)
    glutSolidCube(1)
    glPopMatrix()

def desenhaGarra():
    global angulo_garra

    glPushMatrix()

    # base da garra
    solidBox(2.0, 0.4, 1.0, 1.0, 0.4, 0.7) 

    # superior
    glPushMatrix()
    glTranslatef(2.0, 0.0, 0.0)
    glRotatef(angulo_garra, 0.0, 0.0, 1.0)
    solidBox(2.0, 0.4, 1.0, 0.0, 1.0, 0.8)
    glPopMatrix()

    #inferior
    glPushMatrix()
    glTranslatef(2.0, 0.0, 0.0)
    glRotatef(-angulo_garra, 0.0, 0.0, 1.0)
    solidBox(2.0, 0.4, 1.0, 0.6, 0.0, 0.8) 
    glPopMatrix()

    glPopMatrix()

def desenhaBraco():
    glPushMatrix()

    glTranslatef(0.0, 0.1, 0.0)
    glRotatef(angulo_braco, 0.0, 1.0, 0.0)

    glTranslatef(0.0, 0.0, 0.0)
    desenhaGarra()

    glPopMatrix()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(0, 3, 10, 0, 0, 0, 0, 1, 0)

    desenhaBraco()

    glutSwapBuffers()

def keyboard(key, x, y):
    global angulo_braco, angulo_garra

    if key == b'a':  # abre
        angulo_garra += 2
        if angulo_garra > 60:
            angulo_garra = 60
    elif key == b's':  # fecha
        angulo_garra -= 2
        if angulo_garra < 0:
            angulo_garra = 0

    elif key == b'j':  #esquerda
        angulo_braco += 5
    elif key == b'l':  #direita
        angulo_braco -= 5

    elif key == b'\x1b':
        sys.exit(0)

    glutPostRedisplay()

def init():
    glClearColor(0.4, 0.7, 1.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60.0, 1.0, 1.0, 20.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [10, 10, 10, 1])

glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(800, 600)
glutCreateWindow(b"Garra")

init()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMainLoop()
