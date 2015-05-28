from string import *
from math import *
import os
import sys
import re
import fbpy.fb as fb
import time

HUGE = 10000

class Point(object):
     
    def __init__(self,x ,y ,z):
         self.x = x
         self.y = y
         self.z = z

class Geom(object):
    pass

class Line(object):

    def __init__(self, point1, point2, speed, no):
        self.point1 = point1
        self.point2 = point2
        self.speed = speed
        self.no = no
        self.type = "line"

class Arc(object):
    
    def __init__(self, point1, point2, center, speed, no):
        self.point1 = point1
        self.point2 = point2
        self.center = point3
        self.speed = speed
        self.no = no
        self.type = "arc"

class Geometries(object):

    def __init__(self):
        self.geometries = []
        self.maxx = 0
        self.maxy = 0
        self.minx = HUGE
        self.miny = HUGE
        self.lines = 0
        self.arcs = 0
        self.xtent = 0
        self.ytent = 0

    def add(self, geometry):
        self.geometries.append(geometry)

    def statistics(self):
        for i in self.geometries:
            x1=i.point1.x
            y1=i.point1.y
            x2=i.point2.x  
            y2=i.point2.y
            if (x1 > self.maxx):
                self.maxx = x1
            if (x2 > self.maxx):
                self.maxx = x2
            if (y1 > self.maxy):
                self.maxy = y1
            if (y2 > self.maxy):
                self.maxy = y2

            if (x1 < self.minx):
                self.minx = x1
            if (x2 < self.minx):
                self.minx = x2
            if (y1 < self.miny):
                self.miny = y1
            if (y2 < self.miny):
                self.miny = y2
            
            if isinstance(i, Line):
                self.lines +=1
            if isinstance(i, Arc):
                self.arcs +=1

            self.xtent = self.maxx - self.minx
            self.ytent = self.maxy - self.miny
            #print self.xtent
            #print self.ytent

class Simulator(object):
     
    def __init__(self, geometries):
        self.geometries = geometries 
        self.msurf = fb.Surface()
        self.surf = fb.Surface((800,800),(200,200))

        self.liftcallback = self.dummycallback
        self.lowercallback = self.dummycallback 

    def redraw(self):
        self.surf.clear()
        self.surf.rect((0.0, 0.0),(1.0,1.0))
        self.surf.pixelstyle.color = fb.Color(140,140,140,200)
        self.surf.pixelstyle.blur=0
        self.surf.pixelstyle.blurradius=7
        self.surf.pixelstyle.sigma=2

    def dummycallback(self):
        pass

    def trafo(self, point):
        
        return (point.x/self.geometries.xtent+0.5, point.y/self.geometries.ytent+0.5)

    def draw(self):
          
        for geometry in self.geometries.geometries :
            if isinstance(geometry, Line):
                self.surf.line(self.trafo(geometry.point1), self.trafo(geometry.point2))
        self.surf.update()     

    def sim(self):
        oldz=0
        for geometry in self.geometries.geometries :
            if isinstance(geometry, Line):
                #self.surf.line(self.trafo(geometry.point1), self.trafo(geometry.point2))
                X0 = geometry.point1
                X1 = geometry.point2
                x0 = int(X0.x*100)
                x1 = int(X1.x*100)
                y0 = int(X0.y*100)
                y1 = int(X1.y*100)
                if (X1.z > oldz):
                    self.liftcallback()
                    oldz = X1.z
                if (X1.z < oldz):
                    self.lowercallback()
                    oldz = X1.z
                #bressenham's
                dx = abs(x1-x0)
                if (x0<x1): 
                    sx = 1
                else: 
                    sx = -1
                dy = abs(y1-y0)
                if (y0<y1): 
                    sy = 1
                else: 
                    sy = -1
                if (dx>dy): 
                    err = int(dx/2)
                else: 
                    err = int(-dy/2)

                go=1
                while(go):
                    self.redraw()
                    self.surf.point(
                                    (x0/100.0/self.geometries.xtent+0.5, 
                                     y0/100.0/self.geometries.ytent+0.5)
                                   )
                    #go=0
                    if (x0==x1 and y1==y0): 
                        go=0
                    e2 = err
                    if (e2 > -dx):
                        err -= dy
                        x0 += sx
                    if (e2 < dy):
                        err += dx
                        y0 += sy

                    self.surf.update()
                    time.sleep(0.001)

class Parse(object):

     def __init__(self, filename):
          self.filename = filename
          self.geometries = Geometries()
          self.no_points = 0

     def parse(self):

          try:
               f = open(self.filename,'r')
          except IOError, (errno, strerror):
               error_dialog("Unable to open the file" + gcodes.name + "\n",1)
          else:
               pre_x = 0.0
               pre_y = 0.0
               pre_z = 0.0
               x = pre_x
               y = pre_y
               z = pre_z
               s = 0
               l = 1
               style = 0

               while 1:
                    gcode = f.readline()
                    if not gcode:
                         break
                    flag = 0
                    #parse g code
                    gg = re.search("[gG]([\d]+)\D",gcode)
                    xx = re.search("[xX]([\d\.\-]+)\D",gcode)
                    yy = re.search("[yY]([\d\.\-]+)\D",gcode)
                    zz = re.search("[zZ]([\d\.\-]+)\D",gcode)
                    ss = re.search("[fF]([\d\.\-]+)\D",gcode)
                    if (gg):
                         style = int(gg.group(1))
                    if (xx):
                         x = float(xx.group(1))
                         flag = 1
                    if (yy):
                         y = float(yy.group(1))
                         flag = 1
                    if (zz):
                         z = float(zz.group(1))
                         flag = 1
                    if (ss):
                         s = float(ss.group(1))
                         #print "s: {0}".format(s)
                    if(style == 1 or style == 0):
                         #lines
                         if(flag):
                              point1 = Point(pre_x,pre_y,pre_z)
                              point2 = Point(x,y,z)
                              self.geometries.add(Line(point1, point2, s, l))
                              self.no_points+=1
                              #print "{0:<6} {1:<6}".format(x,y)
                    elif(style == 2 or style == 3):
                         #arcs
                              i=0
                              j=0
                              k=0
                              ii = re.search("[iI]([\d\.\-]+)\D",gcode)
                              jj = re.search("[jJ]([\d\.\-]+)\D",gcode)
                              kk = re.search("[kK]([\d\.\-]+)\D",gcode)
                              rr = re.search("[rR]([\d\.\-]+)\D",gcode)
                              if(ii):
                                   i = float(rr.group(1))
                              if(jj):
                                   j = float(rr.group(1))
                              if(kk):
                                   k = float(rr.group(1))
                              center = Point(i,j,k)
                              point1 = Point(pre_x,pre_y,pre_z)
                              point2 = Point(x,y,z)
                              if(style == 3):
                                   #swap
                                   tmp_point = point2
                                   point2 = point1
                                   point1 = point2
                              if(rr):
                                   r = float(rr.group(1))
                                   #c1,c2 = calc_center(point1,point2,r,plain)
                                   #center = c1
                                   #if(r < 0):
                                   #     center = c2
                                   pass
                              #patterns.append(ARC(style,l,s,plain,point1,point2,center))
                              self.no_points+=1
                              print "arc"
                    elif(style == 17):
                              plain = 0
                    elif(style == 18):
                              plain = 1
                    elif(style == 19):
                              plain = 2

                    pre_x = x
                    pre_y = y
                    pre_z = z					
                    l += 1
               f.close()
               self.geometries.statistics()

if __name__ == "__main__":
    def liftcallback():
        print "Please raise mill. Press enter to continue"
        s=raw_input()
        
    def lowercallback():
        print "Please lower mill. Press enter to continue"
        s=raw_input()

    parser = Parse('./spacer.ngc')
    parser.parse()
    sim = Simulator(parser.geometries)
    sim.liftcallback = liftcallback
    sim.lowercallback = lowercallback 
    #sim.draw()
    sim.sim()

