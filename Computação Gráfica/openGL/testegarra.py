from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

ang = 0.0
mouse_down = False
x0 = 0

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0,0,6, 0,0,0, 0,1,0)
    glRotatef(ang, 0,1,0)

    # cubo simples no centro
    glColor3f(0.2, 0.6, 0.9)
    glutSolidCube(1.5)

    glutSwapBuffers()

def mouse(button, state, x, y):
    global mouse_down, x0
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_down = True
            x0 = x
        elif state == GLUT_UP:
            mouse_down = False

def motion(x, y):
    global ang, x0
    if not mouse_down:
        return
    dx = x - x0
    x0 = x
    ang += dx * 0.5   # sensibilidade; ajuste se necessário
    # opcional: normalizar para evitar números muito grandes
    if ang > 360 or ang < -360:
        ang = ang % 360
    # DEBUG: imprime para ver se o callback foi chamado
    print(f"motion: dx={dx:.1f} ang={ang:.2f}")
    glutPostRedisplay()

def init():
    glClearColor(0.8, 0.9, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 800/600.0, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(800,600)
glutCreateWindow(b"Teste Rotacao Mouse")
init()
glutDisplayFunc(display)
glutMouseFunc(mouse)
glutMotionFunc(motion)
glutMainLoop()
