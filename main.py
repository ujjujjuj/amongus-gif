import cv2
import numpy as np
import imageio
import sys

N_COLORS = 8
N_TILES = 42
TILE_WIDTH = 20 
DELAY = 0.08

frames = []
imgs = []
cache = {}
# prepare images and masks
for i in range(5):
    im = cv2.cvtColor(cv2.imread(f"res/{i}.png"),cv2.COLOR_BGR2RGB)
    mask_col = cv2.inRange(im,np.array([209,220,236]),np.array([219,230,246]))
    mask_shadow = cv2.inRange(im,np.array([126,143,186]),np.array([136,153,196]))
    imgs.append([im, mask_col, mask_shadow])

# apply mask and resize tiles
def colorConvert(i,col):
    shadow = [max(i-42,32) for i in col] 
    temp_img = imgs[i][0].copy()
    temp_img[imgs[i][1] > 0] = col
    temp_img[imgs[i][2] > 0] = shadow
    return cv2.resize(cv2.cvtColor(temp_img,cv2.COLOR_BGR2RGB),(TILE_WIDTH,TILE_WIDTH))

# get normalized color
def getColors(col):
    interval = 256/N_COLORS
    return tuple([min(int(interval*(i//interval + 1)),255) for i in col])

# resize image
if len(sys.argv) < 2:
    print("provide the image name as the first argument!")
    exit()

img = cv2.imread(sys.argv[1])
ratio = float(img.shape[0]) / float(img.shape[1])
if ratio > 1:
    new_h = N_TILES
    new_w = int(N_TILES / ratio)
else:
    new_w = N_TILES
    new_h = int(N_TILES * ratio)
img = cv2.resize(img, (new_w,new_h))

# create cache
print("creating cache")
l = [int(i*(255/N_COLORS)) + 2 for i in range(N_COLORS)]
for r in l:
    for g in l:
        for b in l:
            col = getColors((r,g,b))
            col_imgs = []
            for i in range(5):
                col_imgs.append(colorConvert(i,col))
            cache[col] = col_imgs

# create frames
print("creating frames")
for frameno in range(5):
    im = []
    for j in range(len(img)):
        row = []
        for i in range(len(img[j])):
            offset = 4 - ((i + j + frameno) % 5) 
            col = getColors(img[j][i])
            row.append(cache[col][offset])
        im.append(row)
    frame = cv2.vconcat([cv2.hconcat(h_images) for h_images in im])
    frames.append(frame)

# save gif
print("saving gif")
with imageio.get_writer("out.gif", mode="I",duration=0.08) as writer:
    for frame in frames:
        writer.append_data(frame)
