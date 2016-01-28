#! /usr/bin/env python
'''
Generates Inkscape SVG file containing box components needed to 
laser cut a tabbed construction box taking kerf and clearance into account

Copyright (C) 2011 elliot white   elliot@twot.eu
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
__version__ = "0.8" ### please report bugs, suggestions etc to bugs@twot.eu ###

import sys,inkex,simplestyle,gettext
_ = gettext.gettext

def drawS(XYstring):         # Draw lines from a list
  name='part'
  style = { 'stroke': '#000000', 'fill': 'none' }
  drw = {'style':simplestyle.formatStyle(style),inkex.addNS('label','inkscape'):name,'d':XYstring}
  inkex.etree.SubElement(parent, inkex.addNS('path','svg'), drw )
  return

def hole((root_x,root_y),(width,height)):
  return 'M '+str(root_x)+','+str(root_y)+' '+'L '+str(root_x)+','+str(root_y+height)+' '+'L '+str(root_x+width)+','+str(root_y+height)+' '+'L '+str(root_x+width)+','+str(root_y)+' '+'L '+str(root_x)+','+str(root_y)+' '

def holes((root_x,root_y),(drawer_width,drawer_heights,drawer_depth),length,drawer_count):
  isTab=1
  divs=int(length/nomTab)  # divisions
  if not divs%2: divs-=1   # make divs odd
  divs=float(divs)
  tabs=(divs-1)/2          # tabs for side
  
  if equalTabs:
    gapWidth=tabWidth=length/divs
  else:
    tabWidth=nomTab
    gapWidth=(length-tabs*nomTab)/(divs-tabs)
    
  if isTab:                 # kerf correction
    gapWidth-=correction
    tabWidth+=correction
    first=correction/2
  else:
    gapWidth+=correction
    tabWidth-=correction
    first=-correction/2
    
  s=""
  for j in range(drawer_count-1):
    for i in range(int(tabs)):
      s+=hole((root_x+(j+1)*thickness+sum(drawer_heights[:j+1]),root_y+i*(gapWidth+tabWidth)+gapWidth),(thickness-2*kerf,tabWidth-2*kerf))
  return s
  
  
def side((rx,ry),(sox,soy),(eox,eoy),tabVec,length,(dirx,diry),isTab):
  #       root startOffset endOffset tabVec length  direction  isTab

  divs=int(length/nomTab)  # divisions
  if not divs%2: divs-=1   # make divs odd
  divs=float(divs)
  tabs=(divs-1)/2          # tabs for side
  
  if equalTabs:
    gapWidth=tabWidth=length/divs
  else:
    tabWidth=nomTab
    gapWidth=(length-tabs*nomTab)/(divs-tabs)
    
  if isTab:                 # kerf correction
    gapWidth-=correction
    tabWidth+=correction
    first=correction/2
  else:
    gapWidth+=correction
    tabWidth-=correction
    first=-correction/2
    
  s=[]
  firstVec=0; secondVec=tabVec
  dirxN=0 if dirx else 1 # used to select operation on x or y_root
  diryN=0 if diry else 1
  (Vx,Vy)=(rx+sox*thickness,ry+soy*thickness)
  s='M '+str(Vx)+','+str(Vy)+' '

  if dirxN: Vy=ry # set correct line start
  if diryN: Vx=rx

  # generate line as tab or hole using:
  #   last co-ord:Vx,Vy ; tab dir:tabVec  ; direction:dirx,diry ; thickness:thickness
  #   divisions:divs ; gap width:gapWidth ; tab width:tabWidth

  for n in range(1,int(divs)):
    if n%2:
      Vx=Vx+dirx*gapWidth+dirxN*firstVec+first*dirx
      Vy=Vy+diry*gapWidth+diryN*firstVec+first*diry
      s+='L '+str(Vx)+','+str(Vy)+' '
      Vx=Vx+dirxN*secondVec
      Vy=Vy+diryN*secondVec
      s+='L '+str(Vx)+','+str(Vy)+' '
    else:
      Vx=Vx+dirx*tabWidth+dirxN*firstVec
      Vy=Vy+diry*tabWidth+diryN*firstVec
      s+='L '+str(Vx)+','+str(Vy)+' '
      Vx=Vx+dirxN*secondVec
      Vy=Vy+diryN*secondVec
      s+='L '+str(Vx)+','+str(Vy)+' '
    (secondVec,firstVec)=(-secondVec,-firstVec) # swap tab direction
    first=0
  s+='L '+str(rx+eox*thickness+dirx*length)+','+str(ry+eoy*thickness+diry*length)+' '
  return s

  
class DrawerCabinetMaker(inkex.Effect):
  def __init__(self):
      # Call the base class constructor.
      inkex.Effect.__init__(self)
      # Define options
      self.OptionParser.add_option('--unit',action='store',type='string',
        dest='unit',default='mm',help='Measure Units')
        
      self.OptionParser.add_option('--drawer_length',action='store',type='float',
        dest='drawer_depth',default=100,help='Length of Box')
      self.OptionParser.add_option('--drawer_width',action='store',type='float',
        dest='drawer_width',default=100,help='Width of Box')
      self.OptionParser.add_option('--drawer_heights',action='store',type='string',
        dest='drawer_heights',default="1.0;",help='Height of Box')
        
      self.OptionParser.add_option('--drawer_count',action='store',type='int',
        dest='drawer_count',default=0,help='number of drawer')
      self.OptionParser.add_option('--drawer_clearance',action='store',type='float',
        dest='drawer_clearance',default=1,help='Drawer clearance')
        
      self.OptionParser.add_option('--tab_width',action='store',type='float',
        dest='tab_width',default=25,help='Nominal Tab Width')
      self.OptionParser.add_option('--equal',action='store',type='int',
        dest='equal',default=0,help='Equal/Prop Tabs')
      self.OptionParser.add_option('--thickness',action='store',type='float',
        dest='thickness',default=10,help='Thickness of Material')
      self.OptionParser.add_option('--kerf',action='store',type='float',
        dest='kerf',default=0.5,help='Kerf (width) of cut')
      self.OptionParser.add_option('--clearance',action='store',type='float',
        dest='clearance',default=0.01,help='Clearance of joints')
      self.OptionParser.add_option('--layout',action='store',type='int',
        dest='layout',default=1,help='Layout/Style')
      self.OptionParser.add_option('--spacing',action='store',type='float',
        dest='spacing',default=25,help='Part Spacing')
  
  def effect(self):
    global parent,nomTab,equalTabs,thickness,kerf,correction
    
        # Get access to main SVG document element and get its dimensions.
    svg = self.document.getroot()
    
        # Get the attibutes:
    widthDoc  = self.unittouu(svg.get('width'))
    heightDoc = self.unittouu(svg.get('height'))

        # Create a new layer.
    layer = inkex.etree.SubElement(svg, 'g')
    layer.set(inkex.addNS('label', 'inkscape'), 'newlayer')
    layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
    
    parent=self.current_layer
    
        # Get script's option values.
    unit=self.options.unit
    
    
    drawer_depth = self.unittouu( str(self.options.drawer_depth)  + unit )
    drawer_width = self.unittouu( str(self.options.drawer_width) + unit )
    
    
    drawer_count=self.options.drawer_count
    drawer_clearance=self.unittouu(str(self.options.drawer_clearance)+unit)
    thickness = self.unittouu( str(self.options.thickness)  + unit )
    drawer_heights=self.options.drawer_heights
   
    if drawer_heights[len(drawer_heights)-1]==['.']:
      drawer_heights+="0;"
    if drawer_heights[len(drawer_heights)-1]!=';':
      drawer_heights+=";"
    
    drawer_heights=drawer_heights.split(";")
    drawer_heights=drawer_heights[0:len(drawer_heights)-1]
    
    
      #drawer_heights=drawer_heights[0:drawer_count]
    for i in range(len(drawer_heights)):
      drawer_heights[i]=self.unittouu(str(float(drawer_heights[i])) + unit)
    
    if drawer_count>len(drawer_heights):
      counter=0
      len_puffer=len(drawer_heights)
      while len(drawer_heights)<drawer_count:
        drawer_heights+=[drawer_heights[counter%len(drawer_heights)]]
        counter+=1
   
    nomTab = self.unittouu( str(self.options.tab_width) + unit )
    equalTabs=self.options.equal
    kerf = self.unittouu( str(self.options.kerf)  + unit )
    clearance = self.unittouu( str(self.options.clearance)  + unit )
    layout=self.options.layout
    spacing = self.unittouu( str(self.options.spacing)  + unit )
    

    correction=kerf-clearance
    
    drawer_width+=2*drawer_clearance#full space for a drawer
    
    cabinet_width=drawer_width+2*thickness
    cabinet_height=sum(drawer_heights)+thickness*drawer_count+2*thickness
    cabinet_depth=drawer_depth+thickness
    
    text = inkex.etree.Element(inkex.addNS('text','svg'))
    text.text = "Outside:"+str(self.uutounit(cabinet_width,unit))+"x"+str(self.uutounit(cabinet_depth,unit))+"x"+str(self.uutounit(cabinet_height,unit))+"  "
    layer.append(text)
    
    # check input values mainly to avoid python errors
    # TODO restrict values to *correct* solutions
    error=0
    
    if min(drawer_depth,drawer_width)<=0:
      inkex.errormsg(_('Error: Dimensions must be non zero'))
      error=1
    if max(drawer_depth,drawer_width)>max(widthDoc,heightDoc)*10: # crude test
      inkex.errormsg(_('Error: Dimensions Too Large'))
      error=1
    if min(drawer_depth,drawer_width,drawer_heights)<3*nomTab:
      inkex.errormsg(_('Error: Tab size too large'))
      error=1
    if nomTab<thickness:
      inkex.errormsg(_('Error: Tab size too small'))
      error=1
    if thickness==0:
      inkex.errormsg(_('Error: Thickness is zero'))
      error=1
    if thickness>min(drawer_depth,drawer_width,drawer_heights)/3: # crude test
      inkex.errormsg(_('Error: Material too thick'))
      error=1
    if correction>min(drawer_depth,drawer_width,drawer_heights)/3: # crude test
      inkex.errormsg(_('Error: Kerf/Clearence too large'))
      error=1
    if spacing>max(drawer_depth,drawer_width)*10: # crude test
      inkex.errormsg(_('Error: Spacing too large'))
      error=1
    if spacing<kerf:
      inkex.errormsg(_('Error: Spacing too small'))
      error=1

    if error: exit()
   
    # layout format:(rootx),(rooty),Xlength,Ylength,tabInfo,side to be flat,holes(vertical,horicontal,non)
    
    # tabInfo= <abcd> 0=holes 1=tabs
    if   layout==1: # Diagramatic Layout
        pieces=[[spacing,spacing,cabinet_height,cabinet_width,0b0000,4,1],#backplate
        [spacing,2*spacing+cabinet_width,cabinet_height,cabinet_depth,0b1111,2,1],#top/bottom
        [spacing,-thickness+3*spacing+cabinet_width+cabinet_depth,cabinet_height,cabinet_depth,0b1111,2,1],#top/bottom
        [spacing,-2*thickness+4*spacing+cabinet_width+2*cabinet_depth,cabinet_width,cabinet_depth,0b1010,2,0],#sides
        [2*spacing+cabinet_width,-2*thickness+4*spacing+cabinet_width+2*cabinet_depth,cabinet_width,cabinet_depth,0b1010,2,0]]
        for i in range(2,drawer_count+1):
          pieces+=[[(1+i)*spacing+i*cabinet_width,-2*thickness+4*spacing+cabinet_width+2*cabinet_depth,cabinet_width,cabinet_depth,0b1111,2,0]]#tenner
    if   layout==2: # Diagramatic Layout
        pieces=[[spacing,spacing,cabinet_height,cabinet_width,0b0000,4,1],#backplate
        [spacing,2*spacing+cabinet_width,cabinet_height,cabinet_depth,0b1111,2,1],#top/bottom
        [spacing,-thickness+3*spacing+cabinet_width+cabinet_depth,cabinet_height,cabinet_depth,0b1111,2,1],#top/bottom
        [spacing,-2*thickness+4*spacing+cabinet_width+2*cabinet_depth,cabinet_width,cabinet_depth,0b1010,2,0],#sides
        [spacing,-2*thickness+4*spacing+cabinet_width+3*cabinet_depth,cabinet_width,cabinet_depth,0b1010,2,0]]
        for i in range(2,drawer_count+1):
          pieces+=[[spacing,-2*thickness+4*spacing+cabinet_width+(i+2)*cabinet_depth,cabinet_width,cabinet_depth,0b1111,2,0]]#tenner
            
    for piece in pieces: # generate and draw each piece of the box
      
      x_root=piece[0]
      y_root=piece[1]
      x_size=piece[2]
      y_size=piece[3]
      tabs  =piece[4]
      a=tabs>>3&1;b=tabs>>2&1;c=tabs>>1&1;d=tabs&1; # extract tab status for each side
      if piece[5]==0:#top 
        s=side((x_root,y_root),(d,a),(-b,a),0,x_size,(1,0),a)
      else:
        s=side((x_root,y_root),(d,a),(-b,a),-thickness if a else thickness,x_size,(1,0),a)
      type(s)
      if piece[5]==1:#right
        s+=side((x_root+x_size,y_root),(-b,a),(-b,-c),0,y_size,(0,1),b)
      else:
        s+=side((x_root+x_size,y_root),(-b,a),(-b,-c),thickness if b else -thickness,y_size,(0,1),b)
      if piece[5]==2:#bottom
        s+=side((x_root+x_size,y_root+y_size),(-b,-c),(d,-c),0,x_size,(-1,0),c)
      else:
        s+=side((x_root+x_size,y_root+y_size),(-b,-c),(d,-c),thickness if c else -thickness,x_size,(-1,0),c)
      if piece[5]==3:#left
        s+=side((x_root,y_root+y_size),(d,-c),(d,a),0,y_size,(0,-1),d)
      else:
        s+=side((x_root,y_root+y_size),(d,-c),(d,a),-thickness if d else thickness,y_size,(0,-1),d)
      if piece[6]:  
        s+=holes((x_root,y_root),(drawer_width,drawer_heights,drawer_depth),y_size,drawer_count)
      drawS(s)

# Create effect instance and apply it.
effect = DrawerCabinetMaker()
effect.affect()
