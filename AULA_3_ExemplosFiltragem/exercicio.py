import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
import math

def image_convolution(f, w, debug=False):
    N,M = f.shape
    n,m = w.shape
    
    a = int((n-1)/2)
    b = int((m-1)/2)

    # obtem filtro invertido
    w_flip = np.flip( np.flip(w, 0) , 1)

    g = np.zeros(f.shape, dtype=np.uint8)

    # para cada pixel:
    for x in range(a,N-a):
        for y in range(b,M-b):
            # obtem submatriz a ser usada na convolucao
            sub_f = f[ x-a : x+a+1 , y-b:y+b+1 ]
            if (debug==True):
                print(str(x)+","+str(y)+" - subimage:\n"+str(sub_f))
            # calcula g em x,y
            g[x,y] = np.sum( np.multiply(sub_f, w_flip)).astype(np.uint8)

    return g

img1 = cv2.imread("AULA_3_ExemplosFiltragem/lena.png")
img2 = cv2.imread("AULA_3_ExemplosFiltragem/img_aluno.jpeg")
img1_pb = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) 
img2_pb = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) 

w_med = np.matrix([[1, 1, 1], [1, 1, 1], [1, 1, 1]])/9.0
print(w_med)

img1_media = image_convolution(img1_pb, w_med)
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(cv2.cvtColor(img1_pb, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("imagem original, ruidosa")
plt.axis('off')
plt.subplot(122)
plt.imshow(cv2.cvtColor(img1_media, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("imagem convoluída com filtro de media")
plt.axis('off')
plt.show()

img2_media = image_convolution(img2_pb, w_med)
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(cv2.cvtColor(img2_pb, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("imagem original, ruidosa")
plt.axis('off')
plt.subplot(122)
plt.imshow(cv2.cvtColor(img2_media, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("imagem convoluída com filtro de media")
plt.axis('off')
plt.show()

w_diff = np.matrix([[ 0, -1,  0], 
                    [-1,  4, -1], 
                    [ 0, -1,  0]])
print(w_diff)

img1_diff = image_convolution(img1_pb, w_diff)

plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(cv2.cvtColor(img1_pb, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("original image")
plt.axis('off')
plt.subplot(122)
plt.imshow(cv2.cvtColor(img1_diff, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("image filtered with differential filter")
plt.axis('off')
plt.show()

img2_diff = image_convolution(img2_pb, w_diff)
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(cv2.cvtColor(img2_pb, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("original image")
plt.axis('off')
plt.subplot(122)
plt.imshow(cv2.cvtColor(img2_diff, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("image filtered with differential filter")
plt.axis('off')
plt.show()

w_vert = np.matrix([[-1, 0, 1], 
                    [-1, 0, 1], 
                    [-1, 0, 1]])
print(w_vert)

img1_vert = image_convolution(img1_pb, w_vert)
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(img1_pb, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 1")
plt.axis('off')
plt.subplot(122)
plt.imshow(img1_vert, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 1 convoluída com filtro diferencial vertical")
plt.axis('off')
plt.show()

img2_vert = image_convolution(img2_pb, w_vert)
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(img2_pb, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 2")
plt.axis('off')
plt.subplot(122)
plt.imshow(img2_vert, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 2 convoluída com filtro diferencial vertical")
plt.axis('off')
plt.show()

#Filtro passa alta de Laplace.
laplacian = cv2.Laplacian(img1_pb,cv2.CV_64F)
plt.figure(figsize=(12,12)) 
plt.subplot(131)
plt.imshow(img1_pb, cmap="gray", vmin=0, vmax=255)
plt.title("Original")
plt.subplot(132)
plt.imshow(laplacian, cmap="gray", vmin=0, vmax=255)
plt.title("Laplace")
plt.axis('off')
plt.show()

laplacian = cv2.Laplacian(img2_pb,cv2.CV_64F)
plt.figure(figsize=(12,12)) 
plt.subplot(131)
plt.imshow(img2_pb, cmap="gray", vmin=0, vmax=255)
plt.title("Original")
plt.subplot(132)
plt.imshow(laplacian, cmap="gray", vmin=0, vmax=255)
plt.title("Laplace")
plt.axis('off')
plt.show()

#sobel
img_sobelx = cv2.Sobel(img1_pb,cv2.CV_8U,1,0,ksize=5)
img_sobely = cv2.Sobel(img1_pb,cv2.CV_8U,0,1,ksize=5)
sobel = img_sobelx + img_sobely
plt.figure(figsize=(12,12)) 
plt.subplot(122)
plt.imshow(sobel, cmap="gray", vmin=0, vmax=255)
plt.title("Sobel")
plt.axis('off')
plt.subplot(121)
plt.imshow(img1_pb, cmap="gray", vmin=0, vmax=255)
plt.title("Original")
plt.show()

img_sobelx = cv2.Sobel(img2_pb,cv2.CV_8U,1,0,ksize=5)
img_sobely = cv2.Sobel(img2_pb,cv2.CV_8U,0,1,ksize=5)
sobel = img_sobelx + img_sobely
plt.figure(figsize=(12,12)) 
plt.subplot(122)
plt.imshow(sobel, cmap="gray", vmin=0, vmax=255)
plt.title("Sobel")
plt.axis('off')
plt.subplot(121)
plt.imshow(img2_pb, cmap="gray", vmin=0, vmax=255)
plt.title("Original")
plt.show()

#Prewitt
kernelx = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
kernely = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
img_prewittx = cv2.filter2D(img1_pb, -1, kernelx)
img_prewitty = cv2.filter2D(img1_pb, -1, kernely)
img_prewitt = img_prewittx + img_prewitty
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(img1_pb, cmap="gray", vmin=0, vmax=255)
plt.title("Original")
plt.axis('off')
plt.subplot(122)
plt.imshow(img_prewitt, cmap="gray", vmin=0, vmax=255)
plt.title("Prewitt")
plt.show()

kernelx = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
kernely = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
img_prewittx = cv2.filter2D(img2_pb, -1, kernelx)
img_prewitty = cv2.filter2D(img2_pb, -1, kernely)
img_prewitt = img_prewittx + img_prewitty
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(img2_pb, cmap="gray", vmin=0, vmax=255)
plt.title("Original")
plt.axis('off')
plt.subplot(122)
plt.imshow(img_prewitt, cmap="gray", vmin=0, vmax=255)
plt.title("Prewitt")
plt.show()

def roberts_edge_detection(img_gray):
    kernelx = np.array([[1, 0],
                        [0, -1]], dtype=np.float32)
    kernely = np.array([[0, 1],
                        [-1, 0]], dtype=np.float32)

    gx = cv2.filter2D(img_gray, -1, kernelx)
    gy = cv2.filter2D(img_gray, -1, kernely)
    grad = np.sqrt(np.square(gx.astype(np.float32)) + np.square(gy.astype(np.float32)))
    grad = np.clip(grad, 0, 255).astype(np.uint8)

    return grad

img1_roberts = roberts_edge_detection(img1)
img2_roberts = roberts_edge_detection(img2)
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(img1, cmap="gray")
plt.title("Imagem Original")
plt.axis('off')
plt.subplot(122)
plt.imshow(img1_roberts, cmap="gray")
plt.title("Detector de Roberts")
plt.axis('off')
plt.show()

plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(img2, cmap="gray")
plt.title("Imagem Original")
plt.axis('off')
plt.subplot(122)
plt.imshow(img2_roberts, cmap="gray")
plt.title("Detector de Roberts")
plt.axis('off')
plt.show()