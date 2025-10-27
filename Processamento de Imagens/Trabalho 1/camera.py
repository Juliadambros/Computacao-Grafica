import cv2
import numpy as np
import tkinter as tk
from threading import Thread
from filtros import (
    converter_cinza,
    converter_negativo,
    binarizar_otsu
)

running = False
current_filter = "none"
ultimo_frame = None
foto_contador = 0

gray_intensity = 1.0
neg_intensity = 1.0
mean_kernel = 3
median_kernel = 3
canny_threshold1 = 100
canny_threshold2 = 200
color_intensity = 1.0  
cor_selecionada = None

FILTERS = {
    "Original": "none",
    "Cinza": "gray",
    "Negativo": "negative",
    "Otsu": "otsu",
    "Média": "mean_blur",
    "Mediana": "median_blur",
    "Canny": "canny",
    "Cores": "cor" 
}

CASCADE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

def filtro_cor(frame, cor, intensidade):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if cor == "vermelho":
        lower1 = np.array([0, 120, 70])
        upper1 = np.array([10, 255, 255])
        lower2 = np.array([170, 120, 70])
        upper2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = mask1 + mask2
    elif cor == "verde":
        lower = np.array([35, 50, 50])
        upper = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
    elif cor == "azul":
        lower = np.array([90, 60, 50])   
        upper = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
    else:
        return frame

    result = cv2.bitwise_and(frame, frame, mask=mask)

    blended = cv2.addWeighted(frame, 1 - intensidade, result, intensidade, 0)
    return blended


def apply_filter(frame, filt):
    global gray_intensity, neg_intensity, mean_kernel, median_kernel
    global canny_threshold1, canny_threshold2, color_intensity, cor_selecionada

    if filt == "none":
        return frame

    elif filt == "gray":
        gray = converter_cinza(frame)
        frame = cv2.addWeighted(frame, 1 - gray_intensity, cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), gray_intensity, 0)

    elif filt == "negative":
        neg = converter_negativo(frame)
        frame = cv2.addWeighted(frame, 1 - neg_intensity, neg, neg_intensity, 0)

    elif filt == "otsu":
        otsu = binarizar_otsu(frame)
        frame = cv2.cvtColor(otsu, cv2.COLOR_GRAY2BGR)

    elif filt == "mean_blur":
        k = max(1, int(mean_kernel))
        kernel = np.ones((k, k), np.float32) / (k * k)
        frame = cv2.filter2D(frame, -1, kernel)

    elif filt == "median_blur":
        k = max(1, int(median_kernel))
        if k % 2 == 0:
            k += 1
        frame = cv2.medianBlur(frame, k)

    elif filt == "canny":
        frame_gray = converter_cinza(frame)
        canny = cv2.Canny(frame_gray, canny_threshold1, canny_threshold2)
        frame = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)

    elif filt == "cor" and cor_selecionada:
        frame = filtro_cor(frame, cor_selecionada, color_intensity)

    return frame


def camera_loop():
    global running, current_filter, ultimo_frame

    face_cascade = cv2.CascadeClassifier(CASCADE)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro ao acessar a câmera.")
        running = False
        return

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (740, 580))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        processed = apply_filter(frame.copy(), current_filter)

        for (x, y, w, h) in faces:
            cv2.rectangle(processed, (x, y), (x + w, y + h), (180, 0, 255), 3)
            cv2.putText(processed, "Pessoa", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 0, 255), 2)

        cv2.putText(processed, f"Pessoas: {len(faces)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(processed, f"Filtro: {current_filter}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        cv2.imshow("Deteccao", processed)
        ultimo_frame = processed.copy()

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    running = False


def tirar_foto():
    global ultimo_frame, foto_contador
    if ultimo_frame is not None:
        foto_contador += 1
        nome_arquivo = f"foto_{foto_contador}.png"
        cv2.imwrite(nome_arquivo, ultimo_frame)
        print(f"Foto salva: {nome_arquivo}")
    else:
        print("Nenhum frame disponível para salvar!")


def start_camera_mode(menu_principal_callback=None):
    global running, current_filter, cor_selecionada, color_intensity

    def start_cam():
        global running
        if not running:
            running = True
            Thread(target=camera_loop, daemon=True).start()

    def stop_cam():
        global running
        running = False

    # sliders
    def set_gray_intensity(v):  
        global gray_intensity
        gray_intensity = float(v)

    def set_neg_intensity(v):
        global neg_intensity
        neg_intensity = float(v)

    def set_mean_kernel(v):
        global mean_kernel
        mean_kernel = float(v)

    def set_median_kernel(v):
        global median_kernel
        median_kernel = float(v)

    def set_canny_threshold1(v):
        global canny_threshold1
        canny_threshold1 = float(v)

    def set_canny_threshold2(v):
        global canny_threshold2
        canny_threshold2 = float(v)

    def set_color_intensity(v):
        global color_intensity
        color_intensity = float(v)

    win = tk.Toplevel()
    win.title("Camera com Filtros")
    win.geometry("700x850")
    win.configure(bg="#ffffff")

    tk.Label(win, text="Detecção com Filtros",
             font=("Arial", 20, "bold"), fg="#5e2b97", bg="#ffffff").pack(pady=10)

    filtros_frame = tk.Frame(win, bg="#ffffff")
    filtros_frame.pack(pady=10)

    sliders_frame = tk.Frame(win, bg="#f8f8f8")
    sliders_frame.pack(pady=10, fill="x")

    def limpar_sliders():
        for widget in sliders_frame.winfo_children():
            widget.destroy()

    def selecionar_cor():
        global cor_selecionada

        janela = tk.Toplevel(win)
        janela.title("Selecionar Cor")
        janela.geometry("220x200")
        janela.configure(bg="#ffffff")

        tk.Label(janela, text="Escolha uma cor para o filtro:",
                 font=("Arial", 12, "bold"), bg="#ffffff").pack(pady=10)

        def escolher(cor):
            global cor_selecionada
            cor_selecionada = cor
            janela.destroy()

        tk.Button(janela, text="Vermelho", bg="#e74c3c", fg="white", width=15,
                  command=lambda: escolher("vermelho")).pack(pady=5)
        tk.Button(janela, text="Verde", bg="#27ae60", fg="white", width=15,
                  command=lambda: escolher("verde")).pack(pady=5)
        tk.Button(janela, text="Azul", bg="#2980b9", fg="white", width=15,
                  command=lambda: escolher("azul")).pack(pady=5)

    def mostrar_sliders(filtro):
        limpar_sliders()
        if filtro == "gray":
            tk.Label(sliders_frame, text="Intensidade (Cinza)").pack()
            tk.Scale(sliders_frame, from_=0, to=1, resolution=0.1, orient="horizontal",
                     command=set_gray_intensity).pack()
        elif filtro == "negative":
            tk.Label(sliders_frame, text="Intensidade (Negativo)").pack()
            tk.Scale(sliders_frame, from_=0, to=1, resolution=0.1, orient="horizontal",
                     command=set_neg_intensity).pack()
        elif filtro == "mean_blur":
            tk.Label(sliders_frame, text="Kernel Média").pack()
            tk.Scale(sliders_frame, from_=1, to=15, orient="horizontal",
                     command=set_mean_kernel).pack()
        elif filtro == "median_blur":
            tk.Label(sliders_frame, text="Kernel Mediana").pack()
            tk.Scale(sliders_frame, from_=1, to=15, orient="horizontal",
                     command=set_median_kernel).pack()
        elif filtro == "canny":
            tk.Label(sliders_frame, text="Canny Threshold1").pack()
            tk.Scale(sliders_frame, from_=0, to=500, orient="horizontal",
                     command=set_canny_threshold1).pack()
            tk.Label(sliders_frame, text="Canny Threshold2").pack()
            tk.Scale(sliders_frame, from_=0, to=500, orient="horizontal",
                     command=set_canny_threshold2).pack()
        elif filtro == "cor":
            selecionar_cor()
            tk.Label(sliders_frame, text="Intensidade da Cor").pack()
            tk.Scale(sliders_frame, from_=0, to=1, resolution=0.1, orient="horizontal",
                     command=set_color_intensity).pack()

    def set_filter(name):
        global current_filter
        current_filter = FILTERS[name]
        mostrar_sliders(current_filter)

    for name in FILTERS.keys():
        tk.Button(filtros_frame, text=name, bg="#8e44ad", fg="white", width=28, height=2,
                  font=("Arial", 11, "bold"), command=lambda n=name: set_filter(n)).pack(pady=4)

    tk.Button(win, text="Iniciar Câmera", bg="#27ae60", fg="white", width=35, height=2,
              font=("Arial", 12, "bold"), command=start_cam).pack(pady=8)

    tk.Button(win, text="Parar Câmera", bg="#c0392b", fg="white", width=35, height=2,
              font=("Arial", 12, "bold"), command=stop_cam).pack(pady=8)

    tk.Button(win, text="Tirar Foto", bg="#2980b9", fg="white", width=35, height=2,
              font=("Arial", 12, "bold"), command=tirar_foto).pack(pady=8)

    def voltar_menu():
        stop_cam()
        win.destroy()
        if menu_principal_callback:
            menu_principal_callback()

    tk.Button(win, text="Voltar ao Menu Principal", bg="#7f8c8d", fg="white",
              width=35, height=2, font=("Arial", 12, "bold"),
              command=voltar_menu).pack(pady=15)

    win.mainloop()




