from PIL import Image
import random, colorsys




def getPrimaryColor(im):
    "Takes an image and returns its primary color. Destroys the image in the process."
    im.thumbnail((1,1)) #Changes size in place
    color = im.getcolors()[0][1]
    if len(color) == 1: #no rgb for grayscale images since r=g=b
        color = (color, color, color)
    del im #Reuse of the pic will raise error -> No confusion about inplace size change
    return color

def getColorName(RGB):
    "Takes an RGB color and returns its lowercase name. Returns 'unidentified' if the color is unidentified."
    color = (RGB[0]/255, RGB[1]/255, RGB[2]/255)
    hsv = colorsys.rgb_to_hsv(*color)
    hue, sat, val = (hsv[0]*360, hsv[1]*100, hsv[2]*100)

    darkVal = 25
    brightVal = 75
    greySat = 15
    if (hue > 300 or hue <= 10) and sat > greySat and val > darkVal:    return "red"
    if sat < greySat and val > brightVal:                               return "white"
    if val < darkVal:                                                   return "black"
    if val > darkVal and val < brightVal and sat < greySat:             return "grey"
    if (hue > 10 and hue <= 60) and sat > greySat and val > darkVal:    return "yellow"
    if (hue > 60 and hue <= 150) and sat > greySat and val > darkVal:   return "green"
    if (hue > 150 and hue <= 260) and sat > greySat and val > darkVal:  return "blue"

    return "unidentified"


def classifyByColor(images):
    "Takes an image generator and returns them sorted in a dictionary of colors."
    colors = {"red":[],
              "white":[],
              "black":[],
              "yellow":[],
              "grey":[],
              "green":[],
              "blue":[],
              "unidentified":[]}

    for im, index in images:
        try:
            color = getPrimaryColor(im)
        except OSError:
            continue
        
        name = getColorName(color)
        colors[name].append(index)   

    return colors

def getImageNameFunc(path):
    def getImageName(index):
        "Takes an index and returns the formatted corresponding image name."
        return path+str(index)+".jpg"
    return getImageName

def imageGenerator(fileRange):
    "Takes an index range and yields all images in that range."
    generated = 0
    for i in range(*fileRange):
        try:
            name = getImageName(i)
            im = Image.open(name)
            yield (im, i)
            generated += 1
        except FileNotFoundError:
            continue
    assert generated > 0, "Generator was unable to yield a single image."
        



def genMosaic(origIm, pixelSize, imSize,  colors, used):
    X, Y = origIm.size
    
    rangeX = int(X / pixelSize)
    rangeY = int(Y / pixelSize)
    px = pixelSize

    #Create mosaic canvas
    mosaicSize = (int(X*imSize/px),int(Y*imSize/px))
    mosaic = Image.new("RGB", mosaicSize)
    
    for x in range(rangeX):
        for y in range(rangeY):
            #Get color of part to replicate
            cropBox = (x*px, y*px, (x+1)*px, (y+1)*px)
            cropped = origIm.crop(cropBox)
            color = getPrimaryColor(cropped)
            colorName = getColorName(color)

            #Pick random image of that color
            index = random.choice(colors[colorName]) #Images c
            if index not in used[colorName]:
                used[colorName].append(index)

            #Paste on mosaic
            toPaste = Image.open(getImageName(index)) #We'll catch that higher, we don't want to generate partial mosaic anyway
            mosaic.paste(toPaste, (x*imSize, y*imSize))
    return mosaic
            


if __name__ == "__main__":
    PATH = "Images\\"
    origIm = Image.open("phi.png")
    fileRange = (1001, 1272)
    pixelSize = 1
    imSize = 50
##    
    getImageName = getImageNameFunc(PATH)
    images = imageGenerator(fileRange)
    colors = classifyByColor(images)
##
    for i in colors: print(i, len(colors[i]))
    input()
##    mosaic = genMosaic(origIm, pixelSize, imSize, colors)
##
##    mosaic.save("big.jpg")
    #input()
    zoom = 6
    from tiler import crop
    crop("phi.png", zoom)


    
    #Check we used everything
    used = colors.copy()
    for i in used:
        used[i] = []

    Is = [2]
    Js = [3]
    #Gen
    for i in range(2**zoom):
        for j in range(2**zoom):
            #if i != 2 or j != 3: continue
            #if i not in Is or j not in Js: continue
            name =  str(2**zoom)+"_"+str(i)+"_"+str(j)+".jpg"
            origIm = Image.open(name)
            #print(origIm.size)
            #input()
            mosaic = genMosaic(origIm, pixelSize, imSize, colors, used)
            #mosaic.save("mosaic_"+name)
            mosaic.thumbnail((800,600))
            mosaic.save(name)
            
    for i in used:
        print(i, len(used[i]))
            




    
