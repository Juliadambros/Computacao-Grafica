import cv2

def mostrar_img(img, titulo="Imagem"):
    cv2.imshow(titulo, img)
    altura, largura = img.shape[:2]
    screen_width = cv2.getWindowImageRect(titulo)[2]
    screen_height = cv2.getWindowImageRect(titulo)[3]
    window_x = (1920 // 2) - (largura // 2)
    window_y = (1080 // 2) - (altura // 2)

    try:
        cv2.moveWindow(titulo, window_x, window_y)
    except:
        pass 

    cv2.waitKey(0)
    cv2.destroyAllWindows()
