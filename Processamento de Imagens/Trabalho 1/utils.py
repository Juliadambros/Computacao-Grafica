import cv2

janela_atual = None 

MAX_WIDTH = 1280
MAX_HEIGHT = 720

def mostrar_img(img, titulo="Imagem"):
    global janela_atual

    if janela_atual is not None:
        try:
            cv2.destroyWindow(janela_atual)
        except cv2.error:
            pass

    altura, largura = img.shape[:2]
    scale = min(MAX_WIDTH / largura, MAX_HEIGHT / altura, 1.0)  
    if scale < 1.0:
        nova_largura = int(largura * scale)
        nova_altura = int(altura * scale)
        img = cv2.resize(img, (nova_largura, nova_altura), interpolation=cv2.INTER_AREA)
        altura, largura = img.shape[:2]

    janela_atual = titulo
    cv2.imshow(titulo, img)
    try:
        screen_width = 1920  
        screen_height = 1080
        cv2.moveWindow(titulo, (screen_width - largura) // 2, (screen_height - altura) // 2)
    except:
        pass


