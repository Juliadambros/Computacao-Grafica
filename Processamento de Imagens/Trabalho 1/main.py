# main.py
import tkinter as tk
from camera import start_camera_mode
from imagem import start_image_mode
from video import start_video_mode

BG_COLOR = "#ffffff"
BTN_COLOR = "#8e44ad"
BTN_HOVER = "#732d91"
TEXT_COLOR = "#ffffff"
TITLE_COLOR = "#5e2b97"

def on_enter(e):
    e.widget["background"] = BTN_HOVER

def on_leave(e):
    e.widget["background"] = BTN_COLOR

def create_button(root, text, command):
    btn = tk.Button(
        root,
        text=text,
        command=command,
        width=36,
        height=2,
        bg=BTN_COLOR,
        fg=TEXT_COLOR,
        font=("Arial", 11, "bold"),
        activebackground=BTN_HOVER,
        activeforeground="white",
        relief="flat",
        cursor="hand2"
    )
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    btn.pack(pady=8)
    return btn

def main():
    root = tk.Tk()
    root.title("Trabalho PDI")
    root.geometry("420x400")
    root.configure(bg=BG_COLOR)

    tk.Label(
        root,
        text="Trabalho PDI — Selecionar modo",
        font=("Arial", 16, "bold"),
        fg=TITLE_COLOR,
        bg=BG_COLOR
    ).pack(pady=30)

    create_button(root, "Reconhecimento Câmera", start_camera_mode)
    create_button(root, "Processamento de Imagem", start_image_mode)
    create_button(root, "Processamento de Vídeo (Coca-Cola)", start_video_mode)

    exit_btn = tk.Button(
        root,
        text=" Sair",
        command=root.quit,
        bg="#ffffff",
        fg="#8e44ad",
        width=15,
        height=1,
        font=("Arial", 11, "bold"),
        relief="solid",
        borderwidth=1,
        cursor="hand2"
    )
    exit_btn.pack(pady=25)

    root.mainloop()

if __name__ == "__main__":
    main()
