import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import subprocess
import requests

def get_installed_models():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if not lines:
            return []

        # Saltar la línea de encabezado
        lines = lines[1:]

        models = []
        for line in lines:
            if not line.strip():
                continue
            # Dividir la línea en columnas
            parts = line.split()
            if parts:
                model_name = parts[0]
                # Remover ':latest' si está presente
                model_name = model_name.replace(':latest', '')
                models.append(model_name)
        return models
    except Exception as e:
        print(f"Error al obtener los modelos instalados: {e}")
        return []

def send_message():
    user_input = entry.get("1.0", tk.END).strip()
    if user_input == "":
        return
    chat_history.configure(state='normal')
    chat_history.insert(tk.END, "Tú: " + user_input + "\n")
    chat_history.configure(state='disabled')
    entry.delete("1.0", tk.END)

    # Obtener el modelo seleccionado
    selected_model = model_var.get()
    print("Modelo seleccionado:", selected_model)

    # Obtener respuesta del modelo de Ollama
    response = get_ollama_response(user_input, selected_model)

    chat_history.configure(state='normal')
    chat_history.insert(tk.END, f"{selected_model}: " + response + "\n")
    chat_history.configure(state='disabled')
    chat_history.see(tk.END)

    # Agregar el mensaje al historial de chats en el left_frame
    add_chat_history_item(user_input)

def add_chat_history_item(message):
    # Agregar el mensaje al Treeview del historial de chats
    chat_history_tree.insert('', 'end', text='', values=(message,))

def get_ollama_response(prompt, model):
    data = {
        "prompt": prompt,
        "model": model,
        "stream": False,
        "options": {"temperature": 0.1, "top_p": 0.99, "top_k": 100},
    }
    try:
        response = requests.post("http://127.0.0.1:11434/api/generate", json=data)
        response.raise_for_status()
        api_response = response.json()
        return api_response['response']
    except requests.exceptions.RequestException as e:
        return f"Error en la solicitud a la API: {e}"
    except (ValueError, KeyError) as e:
        return f"Error procesando la respuesta de la API: {e}"

def clear_chat():
    chat_history.configure(state='normal')
    chat_history.delete(1.0, tk.END)
    chat_history.configure(state='disabled')

# Crear la ventana principal
window = tk.Tk()
window.title("Chat with Ollama")

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Ajustar el tamaño de la ventana al tamaño de la pantalla
window.geometry(f"{screen_width}x{screen_height}+0+0")

# Mostrar los controles de la ventana
window.overrideredirect(False)

# Establecer el color de fondo de la ventana principal
window.configure(bg='#2e2e2e')  # Color gris oscuro para el fondo del window

# Crear el marco principal que contendrá el left_frame y el right_frame
main_frame = tk.Frame(window, bg='#2e2e2e')
main_frame.pack(fill=tk.BOTH, expand=True)

# Calcular el ancho del left_frame (1/5 del ancho de pantalla)
left_frame_width = screen_width // 5

# Crear el left_frame para el historial de chats
left_frame = tk.Frame(main_frame, width=left_frame_width, bg='#2e2e2e')
left_frame.pack(side=tk.LEFT, fill=tk.Y)
left_frame.pack_propagate(False)  # Mantener el ancho fijo

# Crear el Treeview para el historial de chats
chat_history_tree = ttk.Treeview(left_frame)
chat_history_tree['columns'] = ('conversation',)
chat_history_tree.column('#0', width=0, stretch=tk.NO)  # Ocultar la primera columna
chat_history_tree.column('conversation', anchor='w', width=left_frame_width)

chat_history_tree.heading('conversation', text='History', anchor='w')

# Scrollbars para el Treeview
chat_history_v_scrollbar = tk.Scrollbar(left_frame, orient=tk.VERTICAL, command=chat_history_tree.yview)
chat_history_h_scrollbar = tk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=chat_history_tree.xview)

# Configurar el Treeview para usar las scrollbars
chat_history_tree.configure(yscrollcommand=chat_history_v_scrollbar.set, xscrollcommand=chat_history_h_scrollbar.set)

# Empaquetar el Treeview y las scrollbars
chat_history_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
chat_history_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chat_history_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

# Aplicar estilo al Treeview para colores oscuros
# Aplicar estilo al Treeview para colores oscuros
style = ttk.Style()
style.theme_use('default')

# Estilo para las filas del Treeview
style.configure('Treeview', 
                background='#1e1e1e',
                foreground='white',
                fieldbackground='#1e1e1e',
                rowheight=25)
style.map('Treeview', background=[('selected', '#3e3e3e')])

# Estilo para el encabezado del Treeview
style.configure('Treeview.Heading',
                background='#2e2e2e',
                foreground='white',
                relief='flat')
style.map('Treeview.Heading',
          background=[('active', '#3e3e3e')])


# Crear el right_frame para el resto de la interfaz
right_frame = tk.Frame(main_frame, bg='#2e2e2e')
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Obtener la lista de modelos instalados
models = get_installed_models()
if not models:
    models = ["default"]  # En caso de que no se puedan obtener los modelos

# Variable para el modelo seleccionado
model_var = tk.StringVar(right_frame)
model_var.set(models[0])  # Modelo por defecto

# Menú desplegable para seleccionar el modelo
model_menu = tk.OptionMenu(right_frame, model_var, *models)
model_menu.configure(
    bg='#2e2e2e',
    fg='white',
    activebackground='#3e3e3e',
    activeforeground='white',
    highlightthickness=0,
)
model_menu['menu'].configure(bg='#2e2e2e', fg='white')
model_menu.pack(pady=5, fill=tk.X)

# Área de texto para mostrar el historial del chat
chat_history = scrolledtext.ScrolledText(
    right_frame, state='disabled', width=80, height=20,
    bg='#1e1e1e', fg='white', insertbackground='white',
    highlightbackground='#2e2e2e', highlightcolor='#2e2e2e'
)
chat_history.pack(pady=10, fill=tk.BOTH, expand=True)

# Frame para la entrada y el botón
input_frame = tk.Frame(right_frame, bg='#2e2e2e')
input_frame.pack(pady=5, fill=tk.X)

# Frame para los botones
button_frame = tk.Frame(input_frame, bg='#2e2e2e')
button_frame.pack(side=tk.RIGHT, padx=5, pady=5)

# Cargar el icono para el botón "Enviar"
play_icon = tk.PhotoImage(file="./icons/play.png")
clear_icon = tk.PhotoImage(file="./icons/clear.png")
# Botón "Enviar" con icono
send_button = tk.Button(
    button_frame, image=play_icon, command=send_message,
    bg='#2e2e2e', activebackground='#3e3e3e', borderwidth=0
)
send_button.image = play_icon  # Mantener referencia al icono
send_button.pack(side=tk.TOP, padx=5, pady=5)

# Botón "Limpiar Chat" debajo del botón "Enviar"
clear_button = tk.Button(
    button_frame, image=clear_icon, command=clear_chat,
    bg='#2e2e2e', activebackground='#3e3e3e', borderwidth=0
)
clear_button.image = clear_icon
clear_button.pack(side=tk.TOP, padx=5, pady=5)

# Calcular el ancho del campo de entrada (ajustado al right_frame)
entry_width = (screen_width * 4) // 5  # 4/5 del ancho de pantalla

# Frame para la entrada de texto y su scrollbar
entry_frame = tk.Frame(input_frame, width=entry_width, bg='#2e2e2e')
entry_frame.pack(side=tk.RIGHT, padx=5, fill=tk.BOTH, expand=True)
entry_frame.pack_propagate(False)

# Campo de entrada para el mensaje del usuario
entry = tk.Text(
    entry_frame, wrap=tk.WORD, height=5,
    bg='#1e1e1e', fg='white', insertbackground='white',
    highlightbackground='#2e2e2e', highlightcolor='#2e2e2e'
)
entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Barra de scroll vertical para el campo de entrada
entry_scrollbar = tk.Scrollbar(
    entry_frame, orient=tk.VERTICAL, command=entry.yview, bg='#2e2e2e'
)
entry_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
entry.configure(yscrollcommand=entry_scrollbar.set)

# Iniciar el bucle principal de la interfaz
window.mainloop()