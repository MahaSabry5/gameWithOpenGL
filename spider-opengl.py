from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from math import sin, cos
import time
import numpy
# screen resolution
import ctypes

user32 = ctypes.windll.user32                                      #######
res = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]     #######
rr=res[0]/res[1]

#frames
FPS = 15
previousTime = 0
dt = 0
frame, timebase=0,0


#spiderman
lastFrameUp=False
oldpos=[0,0]
runpos=0
smi=0
spider = []
spiderIndex = []
si=[0,0,0,0]
collisions=False
color=[1,1,1]

#zombie
zcollisions=False
zrunpos=0
zz=-10
zdone=1
zombieForward=True
zombie=[]
zombieIndex=[]
zi=[0]
zmi=0
zdir=1



# Used to rotate the world
mouse_x = 0
mouse_y = 0
hmx=int(res[0]/2)
hmy=int(res[1]/2)

#zoom
zoom=1

#menu
Move_Y = 0
MainMenuPointer=0
MainMenuChoose=[1,1,1,1]
OptionsChoose=[1,1]

#camera
yrot = 0.0
xpos = 0.0
zpos = 0.0
piover180 = 0.0174532925

#lists..
dis=[] #display
obj=[] #3D model
line=[] #input

aflags={
    "MainMenu": True,
    "Game": False,
    "Options": False,
    "Credits": False,
    "Exit": False,
    "Enter": False,
    "Escape": False,
    "Up": False,
    "Down": False,
    "Right": False,
    "Left": False,
    "O": False,
    "P": False,
    "A": False
}

def import_movment(path,folders,mov,index):
    movment_type=0
    for folder in folders:
        mov.append([])
        movment_index = 0
        if folder != '':
            p = os.path.join(path, folder)
        else:
            p = path
        for filename in os.listdir(p):
            if filename.partition('.')[2] == 'obj':
                print(p + '\\' + filename)
                mov[movment_type].append(OBJ(filename, path=p + '\\'))
                movment_index += 1
        index.append(movment_index)
        movment_type+=1

def MTL(filename,path=''):
    contents = {}
    mtl = None
    with open(path + filename, "r") as openedfile:
        for line in openedfile:
            if line.startswith('#') or line.startswith('map_Bump'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'newmtl':
                mtl = contents[values[1]] = {}
            elif mtl is None:
                raise ValueError("mtl file doesn't start with newmtl stmt")
            elif values[0] == 'map_Kd':
                # load the texture referred to by this declaration

                vvi = 0
                vw = str()
                for vv in values:
                    if vvi:
                        vw += vv + ' '
                    vvi += 1
                mtl[values[0]] = path+vw
                surf = pygame.image.load(mtl['map_Kd'])
                image = pygame.image.tostring(surf, 'RGBA', 1)
                ix, iy = surf.get_rect().size
                texid = mtl['texture_Kd'] = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, texid)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                    GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                    GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA,
                    GL_UNSIGNED_BYTE, image)
    return contents

class OBJ:
    def __init__(self, filename, swapyz=False,path=''):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        material = None
        with open(path + filename, "r") as openedfile:
            for line in openedfile:
                if line.startswith('#'): continue
                values = line.split()
                if not values: continue
                if values[0] == 'v':
                    v = list(map(float, values[1:4]))
                    if swapyz:
                        v = v[0], v[2], v[1]
                    self.vertices.append(v)
                elif values[0] == 'vn':
                    v = list(map(float, values[1:4]))
                    if swapyz:
                        v = v[0], v[2], v[1]
                    self.normals.append(v)
                elif values[0] == 'vt':
                    self.texcoords.append(list(map(float, values[1:3])))
                elif values[0] in ('usemtl', 'usemat'):
                    material = values[1]
                elif values[0] == 'mtllib':
                    self.mtl = MTL(values[1],path)
                elif values[0] == 'f':
                    face = []
                    texcoords = []
                    norms = []
                    for v in values[1:]:
                        w = v.split('/')
                        face.append(int(w[0]))
                        if len(w) >= 2 and len(w[1]) > 0:
                            texcoords.append(int(w[1]))
                        else:
                            texcoords.append(0)
                        if len(w) >= 3 and len(w[2]) > 0:
                            norms.append(int(w[2]))
                        else:
                            norms.append(0)
                    self.faces.append((face, norms, texcoords, material))

        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)
        for face in self.faces:
            vertices, normals, texture_coords, material = face

            mtl = self.mtl[material]
            if 'texture_Kd' in mtl:
                # use diffuse texmap
                glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                # just use diffuse colour
                glColor(*mtl['Kd'])

            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()
        glDisable(GL_TEXTURE_2D)
        glEndList()

def drawText(string):
    glLineWidth(2)
    wc=0
    string = string.encode()  # conversion from Unicode string to byte string
    for c in string:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, c)#to render the character 
        wc+=1
    glTranslate(-wc*75,0,0)



def MouseMotion(x, y):
    global mouse_x
    global mouse_y
    mouse_x, mouse_y =x,y


def mainMenu():
    glColor(0, 1, 0)
    wr = (res[0] / 1366)
    hr = (res[1] / 768)
    step = 170 * hr

    startdrawHUD()

    glTranslate(wr * 200, 0, 0)
    glTranslate(0, hr * 586, 0)

    glColor(1, 1, MainMenuChoose[0])
    string = "START"
    drawText(string)

    glColor(1, 1, MainMenuChoose[1])
    glTranslate(0, -step, 0)
    string = "OPTIONS"
    drawText(string)

    glColor(1, 1, MainMenuChoose[2])
    glTranslate(0, -step, 0)
    string = "CREDITS"
    drawText(string)

    glColor(1, 1, MainMenuChoose[3])
    glTranslate(20, -step, 0)
    string = "EXIT"
    drawText(string)

    enddrawHUD()


def drawBarrier():
    global collisions
    global xpos, zpos, yrot

    collisions=False

    # the camera settings
    xtrans = -xpos
    ytrans=-zpos
    sceneroty = 360-yrot

    h=1
    w=3.5
    p=[[-w,-10.5],
       [-w,1],
       [w,1],
       [w,-10.5]]
    '''
    glColor(color[0],color[1],color[2])
    glBegin(GL_POLYGON)
    glVertex(p[0][0], h, p[0][1])
    glVertex(p[1][0], h, p[1][1])
    glVertex(p[2][0], h, p[2][1])
    glVertex(p[3][0], h, p[3][1])
    glEnd()
    '''

    for i in numpy.arange(p[0][0],p[3][0],0.1):
        if collisions:
            break
        xs = i + xtrans
        ys = p[0][1] + ytrans
        ys2 = p[1][1] + ytrans
        xss = (xs * cos(sceneroty)) - (ys * sin(sceneroty))
        yss = (ys * cos(sceneroty)) + (xs * sin(sceneroty))
        xss2 = (xs * cos(sceneroty)) - (ys2 * sin(sceneroty))
        yss2 = (ys2 * cos(sceneroty)) + (xs * sin(sceneroty))

        collisions = detectCollisions(0, 0, 0.2, xss, yss, 0)
        if not collisions:
            collisions = detectCollisions(0, 0, 0.2, xss2, yss2, 0)


    for i in numpy.arange(p[0][1],p[1][1],0.1):
        if collisions:
            break

        ys = i + ytrans
        xs = p[1][0] + xtrans
        xs2 = p[2][0] + xtrans
        xss = (xs * cos(sceneroty)) - (ys * sin(sceneroty))
        yss = (ys * cos(sceneroty)) + (xs * sin(sceneroty))
        xss2 = (xs2 * cos(sceneroty)) - (ys * sin(sceneroty))
        yss2 = (ys * cos(sceneroty)) + (xs2 * sin(sceneroty))

        collisions = detectCollisions(0, 0, 0.2, xss, yss, 0)
        if not collisions:
            collisions = detectCollisions(0, 0, 0.2, xss2, yss2, 0)



def game():
    global xpos, zpos, yrot, piover180
    global mouse_x,mouse_y,hmx,hmy
    global zoom
    global runpos,smi
    global zrunpos,zmi,zz,zdir
    global zcollisions
    # the camera settings
    xtrans = -xpos
    ztrans = -zpos
    sceneroty = 360.0 - yrot

    # reseting transformations
    glLoadIdentity()

    glTranslate(0, 0, 3 * zoom)
    # Rotate around the x and y axes to create a mouse-look camera
    glRotatef(mouse_y - hmy, 1, 0, 0)
    glRotatef(mouse_x - hmx, 0, 1, 0)

    glScale(zoom, zoom, zoom)

    # drawing spiderman
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColor(color[0],color[1],color[2])
    glTranslate(0, 0, runpos)
    glCallList(spider[smi][si[smi]].gl_list)
    glTranslate(0, 0, -runpos)

    # updating the camera
    glRotatef(sceneroty, 0.0, 1.0, 0.0)
    glTranslatef(xtrans, 0, ztrans)

    #this FN used to draw the area and calculate collesion
    drawBarrier()

    # draw the skybox
    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)
    glDisable(GL_COLOR_MATERIAL)
    glLight(GL_LIGHT0, GL_POSITION, (1, 1, 0))
    glColor(1, 1, 1)
    sbf = 1000
    glScale(sbf, sbf, -sbf)
    glCallList(obj[0].gl_list)
    glScale(1 / sbf, 1 / sbf, -1 / sbf)

    # draw the world
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

    glColor(1, 1, 1)
    sbf = 50
    glScale(1 / sbf, 1 / sbf, -1 / sbf)
    glTranslate(0,140,0)
    glTranslate(1250,0, 500)
    glCallList(obj[1].gl_list)
    glTranslate(-1250, 0, -500)
    glTranslate(0, -140, 0)
    glScale(sbf, sbf, -sbf)

    zp=zz+zrunpos
    glColor(1,1,1)
    glTranslate(0, 0, zp)
    glScale(1,1,zdir)
    glCallList(zombie[zmi][zi[zmi]].gl_list)
    glScale(1, 1, -zdir)
    glTranslate(0, 0, -zp)
    #zombie2
    zp=zz+zrunpos

    glColor(1,1,1)
    glTranslate(1, 0, zp)
    glTranslate(0,0,-10)
    glScale(1,1,zdir)
    glCallList(zombie[zmi][zi[zmi]].gl_list)
    glScale(1, 1, -zdir)
    glTranslate(0,0,10)
    glTranslate(-1, 0, -zp)

    ys = zz + ztrans
    xs = xtrans
    xss = (xs * cos(yrot*piover180)) - (ys * sin(yrot*piover180))
    yss = (ys * cos(yrot*piover180)) + (xs * sin(yrot*piover180))
    zcollisions = detectCollisions(0.0, 0.0, 0.2, xss, yss, 0.2)

    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)
    glDisable(GL_COLOR_MATERIAL)

def options():
    global zoom
    wr = (res[0] / 1366)
    hr = (res[1] / 768)
    step = 170 * hr
    factor=0.9

    glColor(1, 1, 1)
    startdrawHUD()

    glTranslate(wr * 200, 0, 0)
    glTranslate(0, hr * 586, 0)
    glScale(factor, factor, 1)
    string = "ZOOM : "
    drawText(string)
    glColor(0,0, 1)
    glTranslate(1.5*step,-step, 0)
    string = str(int(1000*zoom)/1000)
    drawText(string)
    glLoadIdentity()
    glTranslate(wr * (200), 0, 0)
    glTranslate(0, hr * (586-150), 0)
    glScale(factor, factor, 1)
    glTranslate(step, 0, 0)
    glColor(1, 1, OptionsChoose[0])
    string = "<"
    drawText(string)
    glColor(1, 1, OptionsChoose[1])
    glTranslate(3*step, 0, 0)
    string = ">"
    drawText(string)
    glColor(1, 1, 0)
    glTranslate(-4*step, -step, 0)
    string = "BACK"
    drawText(string)
    enddrawHUD()


def credits():
    wr = (res[0] / 1366)
    hr = (res[1] / 768)
    step = 170 * hr
    space=wr*1100
    factor=1/2
    glColor(1,1,1)
    startdrawHUD()
    glTranslate(wr * 150, 0, 0)
    glTranslate(0, hr * 586, 0)
    glScale(factor, factor, 1)
    string = "CREDITS :-"
    drawText(string)
    glTranslate(0, -step, 0)
    string = "Hager Naser"
    drawText(string)
    glTranslate(0, -step, 0)
    string = "Heba Hamed"
    drawText(string)
    glTranslate(0, -step, 0)
    string = "Maha Sabry"
    drawText(string)
    glTranslate(0, -step, 0)
    string = "Mona Mahmoud"
    drawText(string)
    glTranslate(0, -step, 0)
    string = "Nada El-Gendy"
    drawText(string)
    glTranslate(space, 4*step, 0)
    string = "Noran Farag"
    drawText(string)
    glTranslate(0, -step, 0)
    string = "Sameh Etman"
    drawText(string)
    glTranslate(0, -step, 0)
    string = "Shady Gamal"
    drawText(string)
    glTranslate(0, -step, 0)
    string = "Shady Noor"
    drawText(string)
    glTranslate(0, -step, 0)
    string = "Zyad Mackawy"
    drawText(string)
    glColor(1, 1, 0)
    glTranslate(-space, -step, 0)
    string = "Back"
    drawText(string)
    enddrawHUD()


class dp:

    def __init__(self):

        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)

        mainMenu()

        glEndList()

        self.gl_list1 = glGenLists(1)
        glNewList(self.gl_list1, GL_COMPILE)

        # draw game
        game()

        glEndList()

        self.gl_list2 = glGenLists(1)
        glNewList(self.gl_list2, GL_COMPILE)

        options()

        glEndList()


        self.gl_list3 = glGenLists(1)


        glNewList(self.gl_list3, GL_COMPILE)

        credits()

        glEndList()

def myInit():
    global rr
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50,rr, 1, 1000000)                    ########
    gluLookAt(0, 4, 6,
              0,0,0,
              0, 1, 0)

    glClearColor(1, 1, 1, 1)

    # Enable light 1 and set position
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glLight(GL_LIGHT0, GL_POSITION, (0.5, 0.5, 0))



def draw():
    global dis
    global frame, timebase, rot

    frame = frame + 1
    time = glutGet(GLUT_ELAPSED_TIME) / 1000 #Number of milliseconds since glutInit called

    if (time - timebase > 1):
        FPS_r = frame * (time - timebase)
        #print("FPS = ", FPS_r, "   Frame = ", frame, )
        #print("Time = ", time, "    TimeE = ", time - timebase)
        timebase = time
        frame = 0

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    glClearColor(0,0,0,1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)
    glDisable(GL_COLOR_MATERIAL)


    glCallList(dis[0])


    glutSwapBuffers()

    glColor(1,1,1) #so we don't affect the 3D models



def startdrawHUD():
    global rr
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, res[0], 0, res[1], 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

def enddrawHUD():
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def timerz(value):
    global mouse_x, mouse_y, hmx, hmy

    global zoom

    global xpos, zpos, yrot, piover180

    global OptionsChoose, MainMenuPointer, MainMenuChoose

    global line

    global collisions, color

    global runpos, si, smi

    global lastFrameUp

    global zmi, zz, zombieForward, zdir, zdone, zrunpos

    global previousTime, dt

    dis.clear()

    # calculate time to use it in motion according the time of calling display()
    # dt = the new calling - past calling
    currentTime = glutGet(GLUT_ELAPSED_TIME)
    dt = (currentTime - previousTime) / 1000  # 1000 converts from msec to sec
    previousTime = currentTime  # storing the last time to use it in new calculation
    glutTimerFunc(1000 // FPS, timerz, 1)

    if line == []:
        aflags["Up"] = False
        aflags["Down"] = False
        aflags["Right"] = False
        aflags["Left"] = False
        aflags["Escape"] = False
        aflags["Enter"] = False
        aflags["O"] = False
        aflags["P"] = False
        aflags["A"] = False
    else:
        for code in line:
            if code == 72:
                aflags["Up"]=True
            elif code == 80:
                aflags["Down"]=True
            elif code == 77:
                aflags["Right"]=True
            elif code == 75:
                aflags["Left"]=True
            elif code == 1:
                aflags["Escape"]=True
            elif code == 28:
                aflags["Enter"]=True
            elif code == 24:
                aflags["O"]=True
            elif code == 25:
                aflags["P"]=True
            elif code == 30:
                aflags["A"]=True

    if aflags['Exit']:
        dis.clear()
        quit()

    elif aflags['Escape']:
        aflags['MainMenu'] = True
        aflags['Game'] = False
        aflags['Credits'] = False
        aflags['Options'] = False
        aflags['Exit'] = False


        dis.append(dp().gl_list)  # MainMenu

    elif aflags['MainMenu']:# and not aflags['Game'] and not aflags['Opening'] and not aflags['Options'] and not aflags['Exit']:

        if aflags['Up'] and MainMenuPointer < 0:
            MainMenuPointer+= .5

        elif aflags['Down'] and MainMenuPointer > -1.1:
            MainMenuPointer -= .5

        if MainMenuPointer ==0:
            MainMenuChoose = [0, 1, 1, 1]
            if aflags['Enter']:
                aflags['MainMenu'] = False
                aflags['Game'] = True
                aflags['Credits'] = False
                aflags['Options'] = False
                aflags['Exit'] = False
                user32.SetCursorPos(hmx, hmy)

        elif MainMenuPointer == -0.5:
            MainMenuChoose = [1, 0, 1, 1]
            if aflags['Enter']:
                aflags['MainMenu'] = False
                aflags['Options'] = True
                aflags['Game'] = False
                aflags['Credits'] = False
                aflags['Exit'] = False

        elif MainMenuPointer == -1:
            MainMenuChoose = [1, 1, 0, 1]
            if aflags['Enter']:
                aflags['MainMenu'] = False
                aflags['Options'] = False
                aflags['Game'] = False
                aflags['Credits'] = True
                aflags['Exit'] = False


        elif MainMenuPointer == -1.5:
            MainMenuChoose = [1, 1, 1, 0]
            if aflags['Enter']:
                aflags['MainMenu'] = False
                aflags['Options'] = False
                aflags['Game'] = False
                aflags['Credits'] = False
                aflags['Exit'] = True


        dis.append(dp().gl_list)  # MainMenu

    elif aflags['Game']:

        zi[0] += 1
        zi[0] = zi[0] % zombieIndex[0]
        zrunpos = - zi[0]
        si[2]+=1
        si[2]=si[2]%spiderIndex[2]

        if zombieForward:
            zdir = 1
            zz += 0.1
            if zz > 1:
                zombieForward = False
        else:
            zdir = -1
            zz -= 0.1
            if zz < -10:
                zombieForward = True

        if collisions:
            color = [1, 0, 0]
            xpos=oldpos[0]
            zpos=oldpos[1]
        else:
            color = [1, 1, 1]
            oldpos.clear()
            oldpos.append(xpos)
            oldpos.append(zpos)

        # zoom in
        if aflags['P'] and zoom <= 1.56:
            zoom += 0.001

        # zoom out
        if aflags['O'] and zoom >= 0.45:
            zoom -= 0.001

        else:
            if zcollisions and (aflags["A"] or si[3]):
                si[3]=0
                aflags['Credits'] = True
                aflags['Game'] = False

            elif zcollisions or si[1]:
                color = [1, 0, 0]
                smi = 1
                si[1] += 1
                si[1] = si[1] % spiderIndex[1]
            else:

                if aflags["A"] or si[3]:
                    smi = 3
                    si[3] += 1
                    si[3] = si[3] % spiderIndex[3]
                else:
                    si[3]=0
                    smi = 2
                    si[2] += 1
                    si[2] = si[2] % spiderIndex[2]

                    if aflags['Right']:
                        yrot -= 1.5
                    if aflags['Up']:
                        xpos -= sin(yrot * piover180) * 0.05
                        zpos -= cos(yrot * piover180) * 0.05

                        smi=0
                        si[0] += 1
                        si[0] = si[0] % spiderIndex[0]
                        runpos = 4 * si[0] / 3.5

                        lastFrameUp = True
                    elif lastFrameUp:
                        xpos -= sin(yrot * piover180) * 0.05
                        zpos -= cos(yrot * piover180) * 0.05

                        smi = 0
                        si[0] += 1
                        si[0] = si[0] % spiderIndex[0]
                        runpos = 4 * si[0] / 3.5
                        lastFrameUp = False
                    else:
                        runpos = 0
                        si[0]=0
                        smi=2

                    if aflags['Left']:
                        yrot += 1.5


        dis.append(dp().gl_list1)  # Game




    elif aflags['Options']:

        # zoom in
        if aflags['Right'] and zoom <= 1.56:
            zoom += 0.001
            OptionsChoose = [1, 0]

        # zoom out
        if aflags['Left'] and zoom >= 0.45:
            zoom -= 0.001
            OptionsChoose = [0, 1]


        if not (aflags['Right'] or aflags['Left']):
            OptionsChoose = [1,1]

        if aflags['Escape'] or aflags['Enter']:
            aflags['MainMenu'] = True
            aflags['Game'] = False
            aflags['Opening'] = False
            aflags['Options'] = False
            aflags['Exit'] = False

        dis.append(dp().gl_list2)  # Options


    elif aflags['Credits']:


        if aflags['Escape'] or aflags['Enter']:
            aflags['MainMenu'] = True
            aflags['Game'] = False
            aflags['Credits'] = False
            aflags['Options'] = False
            aflags['Exit'] = False

        dis.append(dp().gl_list3)  # credits

    draw()
    line.clear()
    glutPostRedisplay()


def specialKeyHandler(key, x, y):
    if key == GLUT_KEY_UP:
        line.append(72)

    if key == GLUT_KEY_DOWN:
        line.append(80)

    if key == GLUT_KEY_RIGHT:
        line.append(77)

    if key == GLUT_KEY_LEFT:
        line.append(75)

    if key == GLUT_KEY_PAGE_UP: #enter
        line.append(28)
        print('enter')

    if key == GLUT_KEY_PAGE_DOWN: # escape key
        line.append(1)

    if key == GLUT_KEY_HOME: #a
        line.append(30)

    if key == GLUT_KEY_END: #o
        line.append(24)

    if key == GLUT_KEY_DELETE: #p
        line.append(25)


def keyboard(key, x, y):
    kk = ord(key)
    if kk == 13: #enter
        line.append(28)

    if kk==27: # escape key
        line.append(1)

    if key == b'a':
        line.append(30)

    if key == b'o':
        line.append(24)

    if key == b'p':
        line.append(25)


def detectCollisions(x1,y1,r1,x2,y2,r2):
    r=(((x1-x2)**2)+((y1-y2)**2))**(1/2)
    if r < (r1 + r2):

        return True

    else:

        return False


def load_data():
    load_model()
def load_model():
    start = time.time()

    obj.append(OBJ("skybox.obj", path='skybox\\'))
    obj.append(OBJ("cs_havana.obj", path='cs_havana\\'))

    path = 'spiderman\\'
    folders = ['Sprint','hit','Idle','punch']

    import_movment(path, folders, spider, spiderIndex)

    path = 'zombie\\'

    folders = ['walk']
    import_movment(path, folders, zombie, zombieIndex)

    end = time.time()
    print('load_model time = ',end - start)

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(res[0], res[1])
glutCreateWindow(b"spiderman")
glutFullScreen()
myInit()
glutDisplayFunc(draw)
glutTimerFunc(1000 // FPS, timerz, 1)
glutPassiveMotionFunc(MouseMotion)
glutSpecialFunc(specialKeyHandler)
glutKeyboardFunc(keyboard)
load_data()
glutMainLoop()

