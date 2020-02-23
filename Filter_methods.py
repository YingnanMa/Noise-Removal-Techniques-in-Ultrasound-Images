# -*- coding: utf-8 -*-
"""803 code version 1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1m7RpMezoJKr5hvwRjPyz6r1ghEHgGPuz
"""

# importing necessary libraries
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from google.colab.patches import cv2_imshow
from google.colab import drive
drive.mount('/content/drive')

# Load Data
img = cv2.imread('/content/drive/Shared drives/MM803 project team/USX_blood_vessel/capture_12.jpeg' , 0) # Read grayscale image

# Median Filter
median_img1 = cv2.medianBlur(img,11)
resized_img1 = cv2.resize(img, (480,360))
resized_img2 = cv2.resize(median_img1, (480,360))
cv2_imshow(resized_img1)
cv2_imshow(resized_img2)

# Fuzzy image filter


import numpy
from scipy import ndimage
from PIL import Image
# import pymorph

def median(image):
  return ndimage.filters.median_filter(image, size=11)


# A Fuzzy Filter for Images Corrupted by Impulse Noise

def memoize(function):
  memo = {}
  def wrapper(*args):
    if args in memo:
      return memo[args]
    else:
      rv = function(*args)
      memo[args] = rv
      return rv
  return wrapper
  
def fuzzy_filter(image):
  image = numpy.copy(image)
  height, width = image.shape

  conn = {
          0 : ( 0, 0),
          1 : (-1,-1),
          2 : ( 0,-1),
          3 : (+1,-1),
          4 : (-1, 0),
          5 : (+1, 0),
          6 : (-1,+1),
          7 : ( 0,+1),
          8 : (+1,+1)
         }

  # Rule Base
  rules = (
            (2, 5, 7),
            (5, 7, 4),
            (7, 4, 2),
            (4, 2, 5),
            (1,3,8,6),
            (1,2,3,5),
            (2,3,5,8),
            (3,5,8,7),
            (5,8,7,6),
            (8,7,6,4),
            (7,6,4,1),
            (6,4,1,2),
            (4,1,2,3)
          )

  L = 256
  C_PO =  L-1
  C_NE = -L+1
  W = 2*(L-1)

  @memoize  
  def m(u, c, w):
    if u <= c-w:
      return 0.0
    elif c-w < u < c+w:
      return float(w-abs(u-c))/w
    else:
      return 0.0
  
  @memoize
  def m_sm(u, a=40, b=32):
    if u <= a:
      return 1.0
    elif a < u <= a+b:
      return (a+b-u)/b
    else:
      return 0.0

  for y in range(height):
    print("%4.2f%%" % (100.0*float(y)/height))
    for x in range(width):
      l_1 = []
      l_2 = []
      for r in rules:
        l_po = [1.0,] # 1 is min invariant
        l_ne = [1.0,]
        for i in r:
          (dx,dy) = conn[i]
          vy = y+dy
          vx = x+dx
          if 0 <= vy < height and 0 <= vx < width:
            x_j = int(image[vy,vx])-int(image[y,x])
            l_po += (m(x_j, C_PO, W),)
            l_ne += (m(x_j, C_NE, W),)
        l_1 += (min(l_po),)
        l_2 += (min(l_ne),)
      lambda_1 = max(l_1)
      lambda_2 = max(l_2)
      lambda_0 = max(0.0, 1.0-lambda_1-lambda_2)
      v = (L-1)*((lambda_1-lambda_2)/(lambda_0+lambda_1+lambda_2))
      v_small = v*(1.0-m_sm(abs(v)))
      image[y,x] += v_small
  return image

I = numpy.asarray(Image.open('/content/drive/Shared drives/MM803 project team/USX_blood_vessel/capture_12.jpeg').convert("L")).astype(numpy.uint8)

# #impulsive noise
# N = 30
# #salt
# noise = numpy.random.random_integers(0, 100, size=I.shape) > (100-(N/2))
# noise = (noise*255).astype(numpy.uint8)
# I = I | noise
# #pepper
# noise = ~(numpy.random.random_integers(0, 100, size=I.shape) > (100-(N/2)))
# noise = (noise*255).astype(numpy.uint8)
# I = I & noise

# Image.fromarray(I).save("noise.png")

T = median(I)
Image.fromarray(T).save("median.png")
T = fuzzy_filter(I)
Image.fromarray(T).save("fuzzy.png")

# Adaptive gaussian filter


import math
import tools
import numpy as np

from filterCutoff import midPass
import filterLines
import filter1




def gaussianBlur(img, sigma=5):
    print("")
    print("Running Gaussian blur...")
    fImgRed = np.fft.rfft2(img[:,:,0], axes=(0,1))
    fImgBlue = np.fft.rfft2(img[:,:,1], axes=(0,1))
    fImgGreen = np.fft.rfft2(img[:,:,2], axes=(0,1))
    
    gShape = img.shape
    muX = int((gShape[0]) / 2)
    muY = int((gShape[1]) / 2)

    gaussian = [[(1.0/(2*math.pi*sigma**2))*math.exp((-1.0)*((i-muY)**2+(j-muX)**2)/(2*sigma**2)) for i in range(gShape[1])] for j in range(gShape[0])]
    gaussian = np.array(gaussian)
    fGaussian = np.fft.rfft2(gaussian, axes=(0,1))

    blurredImg = np.zeros(img.shape)
    blurredImg[:, :, 0] = np.fft.irfft2(fImgRed * fGaussian)
    blurredImg[:, :, 1] = np.fft.irfft2(fImgBlue * fGaussian)
    blurredImg[:, :, 2] = np.fft.irfft2(fImgGreen * fGaussian)
    blurredImg = np.fft.fftshift(blurredImg, axes=(0,1))

    gaussian3 = np.zeros(img.shape)
    gaussian3[:, :, 0] = gaussian
    gaussian3[:, :, 1] = gaussian
    gaussian3[:, :, 2] = gaussian

    blurredImg = 255.0 * blurredImg / blurredImg.max()
    return blurredImg




# 这个read 的图片不能是grayscale
img = cv2.imread('/content/drive/Shared drives/MM803 project team/USX_blood_vessel/capture_16.jpeg') # Read grayscale imag



splits=20
cutoff=30
sigma=5

print ("Running Selective blur...")
interval = int(1.0 * 255/splits)
rangesCeiling = [interval * x for x in range(1,splits)]
imgLayers = []
originalLayers = []
# for i, upperBound in enumerate(rangesCeiling):
#     newImg = midPass(img, upperBound-interval, upperBound)
#     originalLayers.append(newImg)

#     newImg = gaussianBlur(newImg, sigma=(5-i))
#     imgLayers.append(newImg)

# finalImg = np.zeros(img.shape)                                                                            
# for image in imgLayers:
#     finalImg

truth1 = midPass(img, 0, cutoff-1)
truth2 = midPass(img, cutoff, 256)
img1 = np.array(img)
img2 = np.array(img)
img1[truth1 == False] = 0

img1 = filterLines.linify(img1, separateColours=False, lineFactor=2, lean=1, allowLineMerging=False)
img1 = filter1.affectOnLineContrast(img1, contrast=2, span=5, vertical=True, randomise=False, ifContrastLessThan=True)
img1 = gaussianBlur(img1, sigma=sigma)



finalImg = np.array(img1)
finalImg[truth1 == False] = img2[truth1 == False]

resized_img1 = cv2.resize(img, (480,360))
resized_img2 = cv2.resize(finalImg, (480,360))
cv2_imshow(resized_img1)
cv2_imshow(resized_img2)
