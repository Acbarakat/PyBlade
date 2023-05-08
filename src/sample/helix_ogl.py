import sys
import os
import ctypes
from math import cos, sin, pi

import numpy as np
from OpenGL.GL import GL_TRIANGLE_STRIP, GL_MODELVIEW, GL_PROJECTION,\
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_TEXTURE_2D, GL_TEXTURE_ENV,\
    GL_TEXTURE_ENV_MODE, GL_MODULATE, GL_TEXTURE_WRAP_S, GL_REPEAT, GL_RGB,\
    GL_TEXTURE_WRAP_T, GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_RGBA, GL_BLEND,\
    GL_SRC_ALPHA, GL_ONE, GL_TEXTURE_MIN_FILTER, GL_UNSIGNED_SHORT_5_6_5
from OpenGL.GL import glBegin, glEnd, glClear, glClearColor, glGenTextures,\
    glMatrixMode, glLoadIdentity, glBindTexture, glTexEnvf, glTexParameterf,\
    glTexParameteri, glTexImage2Df, glEnable, glBlendFunc, glTexCoord2f,\
    glVertex3f, glFlush, glDeleteTextures, glReadPixels
from OpenGL.GLU import gluPerspective, gluLookAt
import pygame

# WA: Relative import not workign correctly
sys.path.append(os.path.dirname(__file__) + os.sep + "..")

from switchblade import BufferObj, SwitchBladeApp  # noqa: E402
from switchblade.dynamics import TouchPadImage  # noqa: E402


def spiral(r=15.0, d=5, x=200, pulse2=1.0, **kwargs) -> None:
    """Build the Spiral's vertex and texture data."""
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(0, x):
        if i % 2 == 0:
            glTexCoord2f(0, i)
            # glVertex3f(cos(i/r), -2.5+i*0.05, sin(i/r))
            glVertex3f(cos(i / r) * pulse2, -2.5 + i * 0.05,
                       sin(i / r) * pulse2)
        else:
            glTexCoord2f(1, i)
            # glVertex3f(cos(i/r+3.14), -2.5+i*0.05+d, sin(i/r+3.14))
            glVertex3f(cos(i / r + pi) * pulse2, -2.5 + i * 0.05 + d + pulse2,
                       sin(i / r + pi) * pulse2)
    glEnd()


def prerender() -> int:
    """Create OpenGL prerender commands."""
    glClearColor(0.0, 0.0, 0.0, 1.0)

    return glGenTextures(1)


def render(texture, texdata, t) -> bytes:
    """Create OpenGL render commands."""
    # Get a perspective at the helix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1, 0.01, 1000)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    gluLookAt(sin(t / 200.0) * 3,
              sin(t / 500.0) * 3,
              cos(t / 200.0) * 3,
              0, 0, 0, 0, 1, 0)

    # Draw the helix (this ought to be a display list call)

    glMatrixMode(GL_MODELVIEW)

    glBindTexture(GL_TEXTURE_2D, texture)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    # set sane defaults for a plethora of potentially uninitialized
    # variables

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,
                    GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,
                    GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    # a texture

    pulse = sin(t / 30) * 0.5 + 0.5

    glTexImage2Df(GL_TEXTURE_2D, 0, 4, 0, GL_RGBA,
                  texdata)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    # glEnable(GL_DEPTH_TEST)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)

    spiral(pulse=pulse)

    glFlush()

    glDeleteTextures(1, [texture])

    pygame.display.flip()

    buffer = glReadPixels(0, 0, *screen.get_size(),
                          GL_RGB, GL_UNSIGNED_SHORT_5_6_5)
    buffer.shape = (480, 800)

    return np.flipud(buffer)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(TouchPadImage.SIZE,
                                     pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE)  # noqa: E501
    print(pygame.display.Info())

    t = 0
    # texdata=[[[0.0,0,1,1],
    #           [0.0,0,0,0],
    #           [0.0,1,0,1],
    #           [0.0,0,0,0]],
    #          [[0.0,0,0,0],
    #           [pulse,pulse,pulse,1],
    #           [pulse,pulse,pulse,1],
    #           [0.0,0,0,0]],
    #          [[0.0,1,0,1],
    #           [1,pulse,pulse,1],
    #           [pulse,pulse,0,1],
    #           [0.0,0,0,0]],
    #          [[0.0,0,0,0],
    #           [0.0,0,0,0],
    #           [0.0,0,0,0],
    #           [0.0,0,0,0]]]

    texdata = np.zeros((4, 4, 4))
    texdata.itemset((0, 0, 2), 1)
    texdata.itemset((0, 0, 3), 1)
    texdata.itemset((0, 2, 1), 1)
    texdata.itemset((0, 2, 3), 1)
    texdata.itemset((1, 0, 3), 1)
    texdata.itemset((1, 1, 3), 1)
    texdata.itemset((1, 3, 1), 1)
    texdata.itemset((1, 3, 3), 1)

    TP = TouchPadImage()
    TP_BFO = BufferObj(0, TP.IMAGEDATA_SIZE, TP.toRGB565())

    with SwitchBladeApp() as sba:
        clock = pygame.time.Clock()
        texture = prerender()
        while True:
            TP._buffer = render(texture, texdata, (t := t + 1))

            TP_BFO.pData = TP._buffer.tobytes()
            sba._SwitchBladeDLL.RzSBRenderBuffer(sba.TOUCHPAD,
                                                 ctypes.byref(TP_BFO))
            clock.tick()
            FPS = clock.get_fps()
            pygame.display.set_caption("fps: " + str(clock.get_fps()))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
