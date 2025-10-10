from OpenGL.GL import *
from OpenGL.GLUT import *

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    glBegin(GL_POLYGON)
    glVertex3f(0.45, 0.25, 0.00)
    glVertex3f(0.95, 0.25, 0.00)
    glVertex3f(0.75, 0.75, 0.00)
    glVertex3f(0.25, 0.95, 0.00)
    glEnd()

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB)
    glutInitWindowSize(350,250)
    glutInitWindowPosition(300,200)
    glutCreateWindow(b"Hello Word!")
    init()
    glutDisplayFunc(display)
    glutMainLoop()
    reshape(150, 150)

def init():
    glClearColor(6.0, 0.0,0.0,9.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.1,1.0,0.0,1.0,-7.0,2.0)
    glMatrixMode(GL_MODELVIEW)

#def reshape(width, height):
 #   glViewport(0,0,width, height)

def reshape(width, height):
    size = width if width < height else height
    glViewport(0,0,size,size)

if __name__=="__main__":
    main()