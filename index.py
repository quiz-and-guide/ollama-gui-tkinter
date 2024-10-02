# main.py
import tkinter as tk
from tkinter import messagebox
import chat  # Asegúrate de que chat.py esté en el mismo directorio o en el PYTHONPATH

def open_chat():
    for widget in main_content_frame.winfo_children():
        widget.destroy()
    # Llamar a la función que crea la interfaz del chat en el marco principal
    chat.main(main_content_frame)

def main():
    global root, main_content_frame
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Aplicación Principal")

    # Obtener el tamaño de la pantalla
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Establecer el tamaño de la ventana para que coincida con el tamaño de la pantalla
    root.geometry(f"{screen_width}x{screen_height}+0+0")

    # Mostrar los controles de la ventana
    root.overrideredirect(False)

    # Crear la barra de menús
    menu_bar = tk.Menu(root)

    # Menú File
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Salir", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Menú Edit
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    # Aquí puedes agregar comandos al menú Edit
    menu_bar.add_cascade(label="Edit", menu=edit_menu)

    # Menú Artificial Intelligence
    ai_menu = tk.Menu(menu_bar, tearoff=0)
    ai_menu.add_command(label="Chat", command=open_chat)
    menu_bar.add_cascade(label="Artificial Intelligence", menu=ai_menu)

    # Configurar la barra de menús
    root.config(menu=menu_bar)

    # Crear el marco principal donde se mostrará el chat u otros contenidos
    main_content_frame = tk.Frame(root, bg='#2e2e2e')
    main_content_frame.pack(fill=tk.BOTH, expand=True)

    # Iniciar el bucle principal
    root.mainloop()

if __name__ == "__main__":
    main()
