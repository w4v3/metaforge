import fontforge as ff
import numpy as np
import re
from collections import namedtuple


## the main functions

# provides an interface for editing the font specific parameter dictionary
def viewParameters(junk,fontOrGlyph) :
    font = getFont(fontOrGlyph)
    paramdict = getDict("paramdict",font)

    answ = ff.askString("View parameters",
            printTbl("Parameter : value",
                paramdict,
                "Supported commands:\n[i]nsert [r]emove removeall [u]pdate [q]uit"))

    if answ == "insert" or answ == "i" :
        pname = ff.askString("New parameter","Parameter name:")
        if pname :
            if pname in paramdict :
                ff.postError("Insertion error",
                        "A parameter with this name already exists. Choose a different name or update instead")
            else :
                pval = ff.askString("New parameter","Parameter value:")
                if pval :
                    paramdict[pname] = pval
    elif answ == "remove" or answ == "r" :
        toremove = ff.askString("Remove parameter","Name of parameter to remove:")
        if toremove :
            del paramdict[toremove]
    elif answ == "removeall" :
        paramdict = {}
    elif answ == "update" or answ == "u" :
        pname = ff.askString("Update parameter","Parameter name:")
        if pname :
            if not pname in paramdict :
                ff.postError("Update error",
                        "A parameter with this name does not exist. Choose an existing parameter or insert instead")
            else :
                pval = ff.askString("Update parameter","Parameter value:")
                if pval :
                    paramdict[pname] = pval
    elif answ == "quit" or answ == "q" or not answ :
        return

    font.persistent['paramdict'] = paramdict
    updateAllGlyphs(junk,font)

    viewParameters(junk,font)
    
# provides an interface for editing the glyph specific parametrization dictionary
def viewPoints(junk,glyph) :
    pointdict = getDict("pointdict",glyph)

    answ = ff.askString("View parametrized points",
            printTbl("Coordinate : value",
                pointdict,
                "Supported commands:\n[i]nsert [r]emove removeall [u]pdate [q]uit"))

    if answ == "insert" or answ == "i" :
        pname = ff.askString("New parametrization","Name of coordinate to be parameterized:")
        if pname :
            if pname in pointdict :
                ff.postError("Insertion error",
                        "A coordinate with this name already exists. Choose a different name or update instead")
            else :
                pval = ff.askString("New parametrization","Coordinate value:")
                if pval :
                    pointdict[pname] = pval
    elif answ == "remove" or answ == "r" :
        toremove = ff.askString("Remove point parametrization",
                "Name of coordinate to be deparameterized (the point will not be removed):")
        if toremove :
            del pointdict[toremove]
    elif answ == "removeall" :
        pointdict = {}
    elif answ == "update" or answ == "u" :
        pname = ff.askString("Update point parametrization","Name of coordinate to update:")
        if pname :
            if not pname in pointdict :
                ff.postError("Update error",
                        "A coordinate with this name does not exist. Choose an existing coordinate or parametrize existing points.")
            else :
                pval = ff.askString("Update coordinate","New coordinate value:")
                if pval :
                    pointdict[pname] = pval
    elif answ == "quit" or answ == "q" or not answ :
        return

    glyph.persistent['pointdict'] = pointdict
    updatePoints(glyph)

    viewPoints(junk,glyph)
    
# iterates through the selected points and applies user defined parametrizations to them
def parametrizePoints(junk,glyph) : 
    pointdict = getDict("pointdict",glyph)

    name    = ff.askString("Parametrize points","Name points (do not change afterwards):")
    if not name : # canceled by user
        return
    newx    = ff.askString("Parametrize points","Set x coordinate (empty=skip):")
    newy    = ff.askString("Parametrize points","Set y coordinate (empty=skip):")
    newri   = ff.askString("Parametrize points","Set incoming radius (empty=skip):")
    newphii = ff.askString("Parametrize points","Set incoming angle (degrees, empty=skip):")
    newro   = ff.askString("Parametrize points","Set outgoing radius (empty=skip):")
    newphio = ff.askString("Parametrize points","Set outgoing angle (degrees, empty=skip):")

    glyph.preserveLayerAsUndo() # to make renaming undoable
    layercopy = glyph.layers[ff.activeLayer()]

    for contour in layercopy :
        for idx,point in enumerate(contour) :
            if point.selected :
                point.name = name
                if idx > 0 and not contour[idx-1].on_curve :
                    contour[idx-1].name = name
                if idx < len(contour) - 1 and not contour[idx+1].on_curve :
                    contour[idx+1].name = name
                if newx :
                    pointdict[name+"_x"] = newx
                if newy :
                    pointdict[name+"_y"] = newy
                if newri :
                    pointdict[name+"_ri"] = newri
                if newphii :
                    pointdict[name+"_phii"] = newphii
                if newro :
                    pointdict[name+"_ro"] = newro
                if newphio :
                    pointdict[name+"_phio"] = newphio

    glyph.layers[ff.activeLayer()] = layercopy

    glyph.persistent['pointdict'] = pointdict
    updatePoints(glyph)

def deparametrizePoints(junk,glyph) :
    pointdict = getDict("pointdict",glyph)

    for contour in glyph.layers[ff.activeLayer()] :
        for point in contour :
            if point.selected and point.name :
                pointdict.pop(point.name+"_x",None)
                pointdict.pop(point.name+"_y",None)
                pointdict.pop(point.name+"_ri",None)
                pointdict.pop(point.name+"_phii",None)
                pointdict.pop(point.name+"_ro",None)
                pointdict.pop(point.name+"_phio",None)

    glyph.persistent['pointdict'] = pointd_ct

def askImport(junk,fontOrGlyph) :
    filename = ff.openFilename("Import parametrizations from:","file.mfg","*.mfg")
    if filename is None :
        return
    importParameters(junk,fontOrGlyph,filename,junk)

def askExport(junk,fontOrGlyph) :
    filename = ff.saveFilename("Export parametrizations to:","file.mfg","*.mfg")
    if filename is None :
        return
    exportParameters(junk,fontOrGlyph,filename)

def exportParameters(junk,fontOrGlyph,filename):
    f = open(filename,"w")

    f.write("Parameters\n")
    writeParameters(getFont(fontOrGlyph),f)

    glyphs = fontOrGlyph.glyphs() if isinstance(fontOrGlyph,ff.font) else [fontOrGlyph]
    for glyph in glyphs :
        writePoints(glyph,f)

    f.close()


## some recurring subtasks

def updatePoints(glyph) :
    glyph.preserveLayerAsUndo()

    # evaluate the dictionaries with the current values
    # inefficient as the parameter dictionary is evaluated for every glyph
    # includes globals() for numpy access, as well as some fontforge parameters
    evaledparamdict = evalDict(globals(),
                              { "em"   : glyph.font.em,
                                "desc" : glyph.font.descent, 
                                "asc"  : glyph.font.ascent },
                                "paramdict",
                                glyph.font)
    evaledpointdict = evalDict(evaledparamdict,
                              { "wd"  : glyph.width,
                                "lft" : glyph.left_side_bearing,
                                "rt"  : glyph.right_side_bearing },
                                "pointdict",
                                glyph)

    # the font and glyph attributes are influenced by the special parameters
    glyph.font.ascent = int(evaledparamdict['asc'])
    glyph.font.descent = int(evaledparamdict['desc'])
    glyph.font.em = int(evaledparamdict['em'])
    # glyph.left_side_bearing = int(evaledpointdict['lft']) # do not set this one
    glyph.right_side_bearing = int(evaledpointdict['rt'])
    # glyph.width = int(evaledpointdict['wd'])

    # we may only obtain a copy so we take it and set the layer to the result later
    layercopy = glyph.foreground

    for contour in layercopy :
        for idx,point in enumerate(contour) :
            if point.name and point.on_curve :
                # need to determine off-curve parameters first as radius and angle will be different
                # after the on-curve points were manipulated (their absolute coordinates stay constant)
                if not contour[idx-1].on_curve :
                    if point.name+"_ri" in evaledpointdict :
                        ri = evaledpointdict[point.name+"_ri"]
                    else :
                        ri = getR(point,contour[idx-1])
                    if point.name+"_phii" in evaledpointdict :
                        phii = evaledpointdict[point.name+"_phii"] / 360 * 2*np.pi
                    else :
                        phii = getPhi(point,contour[idx-1])
                if not contour[idx+1].on_curve :
                    if point.name+"_ro" in evaledpointdict :
                        ro = evaledpointdict[point.name+"_ro"]
                    else :
                        ro = getR(point,contour[idx+1])
                    if point.name+"_phio" in evaledpointdict :
                        phio = evaledpointdict[point.name+"_phio"] / 360 * 2*np.pi
                    else :
                        phio = getPhi(point,contour[idx+1])

                if point.name+"_x" in evaledpointdict :
                    point.x = evaledpointdict[point.name+"_x"]
                if point.name+"_y" in evaledpointdict :
                    point.y = evaledpointdict[point.name+"_y"]
                if not contour[idx-1].on_curve :
                    contour[idx-1].x,contour[idx-1].y = getXY(point,ri,phii)
                if not contour[idx+1].on_curve :
                    contour[idx+1].x,contour[idx+1].y = getXY(point,ro,phio)

    glyph.foreground = layercopy

def updateAllGlyphs(junk,font) :
    for glyph in font.glyphs() :
        updatePoints(glyph)

# the following functions implement the *.mfg file syntax, parsing and writing
def importParameters(junk,fontOrGlyph,filename,morejunk):
    font = getFont(fontOrGlyph)
    paramdict = getDict("paramdict",font) 

    f = open(filename,"r")

    for line in f.readlines() :
      if len(line) > 0 :
          if line[0] == "*" :
              match = re.match(r"^\*\s*(\S*)\s*:\s*(.*)\s*$",line)
              if match is not None :
                  paramdict[match.group(1)] = match.group(2)
                  font.persistent['paramdict'] = paramdict
          elif line[0] == "/" :
              match = re.match(r"^/(.*)$",line)
              if match is not None :
                  glyph = font[match.group(1)]
                  pointdict = getDict("pointdict",glyph)
          elif line[0] == "+" :
              match = re.match(r"^\+\s*(\S*)\s*:\s*(.*)\s*$",line)
              if match is not None and pointdict is not None :
                  pointdict[match.group(1)] = match.group(2)
                  glyph.persistent['pointdict'] = pointdict

    f.close()
    updateAllGlyphs(junk,font)

def writeParameters(font,f) :
    paramdict = getDict("paramdict",font)
    for k,v in paramdict.items() :
        f.write("*" + k + ":" + v + "\n")

def writePoints(glyph,f) :
    f.write("/" + glyph.glyphname + "\n")
    pointdict = getDict("pointdict",glyph)
    for k,v in pointdict.items() :
        f.write("+" + k + ":" + v + "\n")

# retrieves the dictionary <name> saved in the persistent dictionary of <where>
# or creates one, if persistent is empty
def getDict(name,where) :
    if where.persistent is None :
        where.persistent = {}
    if not name in where.persistent :
        where.persistent[name] = {}
    return where.persistent[name]

# iteratively evaluates the contents of dictionary <name>,
# with initial global dictionary <init> + <constant>
def evalDict(init,constant,name,fontOrGlyph) :
    font = getFont(fontOrGlyph)
    glyph = fontOrGlyph if isinstance(fontOrGlyph,glyph) else None

    evaleddict = init
    evaleddict.update(constant)
    for k,v in getDict(name,fontOrGlyph).items() :
        # adding locals() for font and glyph attribute access
        evaleddict[k] = eval(v,evaleddict,locals())
    return evaleddict

# for functions that can be called with either a font or a glyph, this returns the font
def getFont(fontOrGlyph) :
    return fontOrGlyph if isinstance(fontOrGlyph,ff.font) else fontOrGlyph.font


## registering the menu items

ff.registerMenuItem(viewParameters,None,None,("Font","Glyph"),None,"MetaForge","View/edit parameters...")
ff.registerMenuItem(updateAllGlyphs,None,None,"Font",None,"MetaForge","Update all glyph parametrizations")
ff.registerMenuItem(viewPoints,None,None,"Glyph",None,"MetaForge","View/edit parametrized points...")
ff.registerMenuItem(parametrizePoints,None,None,"Glyph",None,"MetaForge","Parametrize selected points...")
ff.registerMenuItem(deparametrizePoints,None,None,"Glyph",None,"MetaForge","Deparametrize selected points")
ff.registerMenuItem(askImport,None,None,("Font","Glyph"),None,"MetaForge","Import parametrizations...")
ff.registerMenuItem(askExport,None,None,("Font","Glyph"),None,"MetaForge","Export parametrizations...")
ff.registerImportExport(importParameters,exportParameters,None,"MetaForge Parametrization","mfg")


## utility functions

# ugly print for dictionary, multiple columns to account for max dialog window height in fontforge
def printTbl(pretext,dictionary,posttext) :
    header = "" 
    body = "" 
    n = int(np.ceil(len(dictionary) / 15))

    for i in range(0,n) :
        header = header + pretext + "\t\t"

    i = 0
    for k,v in dictionary.items() :
        body = body + k + " : " + v + "\t\t"
        i = i+1
        if i == n :
            body = body + "\n"
            i = 0

    string = header + "\n" + body + "\n" + posttext
    return string

# conversion between polar and cartesian coordinates
def getR(anchor,tip) :
    return np.sqrt((anchor.x - tip.x)**2 + (anchor.y - tip.y)**2)

def getPhi(anchor,tip) :
    return np.arctan2(tip.y-anchor.y,tip.x-anchor.x)

def getXY(anchor,radius,angle) :
    return anchor.x+np.cos(angle)*radius,anchor.y+np.sin(angle)*radius

# for use in mfg files:
Point = namedtuple('Point', 'x y')
