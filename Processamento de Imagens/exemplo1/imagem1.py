import cv2
import numpy as np

img = cv2.imread("exemplo1\imagem1.jpg")
cv2.imshow('Titulo',img)
cv2.waitKey(0)
cv2.destroyAllWindows()

img1 = cv2.imread('exemplo1\imagem1.jpg', cv2.IMREAD_GRAYSCALE)
cv2.imshow('Niveis de Cinza',img1)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('exemplo1\cinza.jpg',img1)

print(img.shape)
print(img.size)
print(img.dtype)
print('[B G R]:{}'.format(img[60,70]))
# Quadrados coloridos
img[100:200, 150:250] = [40, 100, 200]   
img[200:400, 100:250] = [90, 100, 40]    
img[50:150, 300:400]  = [200, 50, 50]    
img[300:350, 350:450] = [0, 255, 255]    
img[400:500, 50:150]  = [255, 0, 255]    
# Pixel isolado
img[150, 200] = [40, 40, 40]
cv2.imshow('Pixels',img)
cv2.waitKey(0)
cv2.destroyAllWindows()

recorte = img[600:800,600:800]
img[0:200,0:200] = recorte
cv2.imshow('Recorte',img)
cv2.waitKey(0)
cv2.destroyAllWindows()

img2 = cv2.imread('exemplo1\imagem1.jpg')
img3 = cv2.imread('exemplo1\cinza.jpg')
print('Imagem 1:{}{}'.format(img2.shape,img2.dtype))
print('Imagem 2:{}{}'.format(img3.shape,img3.dtype))
img4=img2+img3
print('Imagem 3:{}{}'.format(img4.shape,img4.dtype))
cv2.imshow('Soma',img4)
cv2.waitKey(0)
cv2.destroyAllWindows()

img4 = img2*0.5 + img3*0.5
img4 = img4.astype(np.uint8)
print('Imagem 3: {}{}'.format(img3.shape, img3.dtype))
cv2.imshow('Soma', img4)
cv2.waitKey(0)
cv2.destroyAllWindows()