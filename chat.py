import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from tkinter import filedialog
import subprocess
import requests
import json
import os
import time
import re

def open_chat_frame(parent_frame):
    # Variables
    conversation = []
    conversation_filename = None

    # Load the clear icon for the buttons
    clear_icon = tk.PhotoImage(file="./icons/clear.png")
    clear_icon_small = tk.PhotoImage(file="./icons/clear_small.png")
    # Keep a reference to prevent garbage collection
    parent_frame.clear_icon = clear_icon
    parent_frame.clear_icon_small = clear_icon_small

    # Load the play icon
    play_icon = tk.PhotoImage(file="./icons/play.png")
    parent_frame.play_icon = play_icon

    # Load the attach icon
    attach_icon = tk.PhotoImage(file="./icons/attach.png")
    parent_frame.attach_icon = attach_icon

    def get_installed_models():
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if not lines:
                return []

            # Skip the header line
            lines = lines[1:]

            models = []
            for line in lines:
                if not line.strip():
                    continue
                parts = line.split()
                if parts:
                    model_name = parts[0]
                    model_name = model_name.replace(':latest', '')
                    models.append(model_name)
            return models
        except Exception as e:
            print(f"Error al obtener los modelos instalados: {e}")
            return []

    def send_message():
        nonlocal conversation_filename
        user_input = entry.get("1.0", tk.END).strip()
        if user_input == "":
            return
        chat_history.configure(state='normal')
        chat_history.insert(tk.END, "Tú: " + user_input + "\n\n")
        chat_history.configure(state='disabled')
        entry.delete("1.0", tk.END)

        # Obtener el modelo seleccionado
        selected_model = model_var.get()
        print("Modelo seleccionado:", selected_model)

        # Obtener las últimas cuatro entradas del usuario
        last_user_messages = [msg['content'] for msg in conversation if msg['role'] == 'user'][-4:]

        # Construir el contexto
        if last_user_messages:
            context = "Context: " + ", ".join(last_user_messages) + " Current question -> " + user_input
        else:
            context = user_input

        # Obtener respuesta del modelo de Ollama con el contexto
        response = get_ollama_response(context, selected_model)

        chat_history.configure(state='normal')
        chat_history.insert(tk.END, f"{selected_model}: " + response + "\n\n")
        chat_history.configure(state='disabled')
        chat_history.see(tk.END)

        # Añadir mensajes a la conversación
        conversation.append({'role': 'user', 'content': user_input})
        conversation.append({'role': 'assistant', 'content': response})

        # Guardar la conversación antes de renombrar para asegurar que el archivo existe
        save_conversation()

        # Si es el primer mensaje, actualizar el nombre del archivo y el custom list
        if len(conversation) == 2:
            # Obtener las primeras 20 letras del mensaje del usuario
            display_name = sanitize_filename(user_input[:20])
            filename_base = display_name

            # Asegurar unicidad del nombre de archivo
            counter = 1
            new_conversation_filename = f'history/{filename_base}.json'
            while os.path.exists(new_conversation_filename):
                new_conversation_filename = f'history/{filename_base}_{counter}.json'
                counter += 1

            # Renombrar el archivo
            os.rename(conversation_filename, new_conversation_filename)
            old_filepath = conversation_filename
            conversation_filename = new_conversation_filename

            # Actualizar el item en el custom list
            # Remove old entry
            for widget in chat_history_frame.winfo_children():
                if hasattr(widget, 'filepath') and widget.filepath == old_filepath:
                    widget.destroy()
                    break
            # Add new entry
            add_conversation_to_history(display_name, conversation_filename)
            # Load the conversation
            load_conversation(conversation_filename)

            # Re-guardar la conversación con el nuevo nombre de archivo
            save_conversation()
        else:
            # Guardar la conversación
            save_conversation()

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
        start_new_conversation()

    def sanitize_filename(name):
        # Remover caracteres inválidos para nombres de archivo
        return re.sub(r'[\\/*?:"<>|]', "", name)

    def start_new_conversation():
        nonlocal conversation, conversation_filename
        conversation = []
        # Crear un nombre de archivo temporal
        conversation_filename = 'history/temp_conversation.json'

        # Guardar la conversación vacía para crear el archivo
        save_conversation()

        # Añadir un placeholder al custom list
        display_name = 'Nueva Conversación'
        add_conversation_to_history(display_name, conversation_filename)
        # Seleccionar la nueva conversación
        load_conversation(conversation_filename)

    def save_conversation():
        with open(conversation_filename, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=4)

    def load_conversation_history():
        # Limpiar los items existentes en el custom list
        for widget in chat_history_frame.winfo_children():
            widget.destroy()
        # Listar todos los archivos JSON en la carpeta 'history'
        if not os.path.exists('history'):
            os.makedirs('history')
        files = [f for f in os.listdir('history') if f.endswith('.json')]
        # Ordenar los archivos por fecha de modificación (más recientes primero)
        files.sort(key=lambda x: os.path.getmtime(os.path.join('history', x)), reverse=True)
        for filename in files:
            filepath = os.path.join('history', filename)
            # Obtener el nombre para mostrar (sin la extensión .json)
            display_name = os.path.splitext(filename)[0]
            # Añadir a la lista personalizada
            add_conversation_to_history(display_name, filepath)

    def load_conversation(filepath):
        nonlocal conversation, conversation_filename
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                conversation = json.load(f)
            # Actualizar conversation_filename
            conversation_filename = filepath
            # Limpiar el widget chat_history
            chat_history.configure(state='normal')
            chat_history.delete(1.0, tk.END)
            # Mostrar la conversación
            for message in conversation:
                role = message['role']
                content = message['content']
                if role == 'user':
                    chat_history.insert(tk.END, f"Tú: {content}\n\n")
                elif role == 'assistant':
                    chat_history.insert(tk.END, f"{model_var.get()}: {content}\n\n")
            chat_history.configure(state='disabled')

    def delete_conversation(filepath, row_frame):
        nonlocal conversation, conversation_filename
        # Remove from UI
        row_frame.destroy()
        # Delete the JSON file
        if os.path.exists(filepath):
            os.remove(filepath)
        # If the deleted conversation is the current one, start a new conversation
        if conversation_filename == filepath:
            conversation = []
            conversation_filename = None
            clear_chat()
            start_new_conversation()

    def add_conversation_to_history(display_name, filepath):
        row_frame = tk.Frame(chat_history_frame, bg='#2e2e2e')
        row_frame.pack(fill=tk.X, pady=1)

        # Conversation label
        label = tk.Label(row_frame, text=display_name, bg='#2e2e2e', fg='white', anchor='w')
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        label.bind("<Button-1>", lambda e, fp=filepath: load_conversation(fp))

        # Clear button
        clear_button = tk.Button(row_frame, image=clear_icon_small, command=lambda fp=filepath, rf=row_frame: delete_conversation(fp, rf), bg='#2e2e2e', borderwidth=0, activebackground='#3e3e3e')
        clear_button.pack(side=tk.RIGHT)
        # Keep references
        clear_button.image = clear_icon_small
        label.row_frame = row_frame
        label.filepath = filepath
        row_frame.filepath = filepath

    def attach_file():
        # Open file dialog to select a file
        file_path = filedialog.askopenfilename()

        if not file_path:
            return  # User cancelled the dialog or didn't select any file

        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return

        # Store the file content as a string
        global attached_file_text
        attached_file_text = file_content

        # Insert the file content into the entry widget
        entry.config(state='normal')
        entry.insert(tk.END, f"Archivo adjunto:\n{attached_file_text}\n")

    # Crear el main_frame que contendrá left_frame y right_frame
    main_frame = tk.Frame(parent_frame, bg='#2e2e2e')
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Obtener dimensiones del parent_frame
    parent_frame.update_idletasks()
    screen_width = parent_frame.winfo_width()
    screen_height = parent_frame.winfo_height()

    # Calcular dimensiones
    left_frame_width = screen_width // 5

    # Crear el left_frame para el historial de chats
    left_frame = tk.Frame(main_frame, width=left_frame_width, bg='#2e2e2e')
    left_frame.pack(side=tk.LEFT, fill=tk.Y)
    left_frame.pack_propagate(False)  # Mantener el ancho fijo

    # Crear el canvas para la lista personalizada
    canvas = tk.Canvas(left_frame, bg='#2e2e2e', highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Añadir una scrollbar al canvas
    scrollbar = tk.Scrollbar(left_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Crear un frame dentro del canvas para contener los items
    chat_history_frame = tk.Frame(canvas, bg='#2e2e2e')
    canvas.create_window((0, 0), window=chat_history_frame, anchor='nw')

    # Ajustar el scrollregion del canvas
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    chat_history_frame.bind("<Configure>", on_frame_configure)

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

    # Botón "Enviar"
    send_button = tk.Button(
        button_frame, image=play_icon, command=send_message,
        bg='#2e2e2e', activebackground='#3e3e3e', borderwidth=0
    )
    send_button.pack(side=tk.TOP, padx=5, pady=5)
    send_button.image = play_icon  # Mantener referencia

    # Botón "Limpiar"
    clear_button = tk.Button(
        button_frame, image=clear_icon, command=clear_chat,
        bg='#2e2e2e', activebackground='#3e3e3e', borderwidth=0
    )
    clear_button.pack(side=tk.TOP, padx=5, pady=5)
    clear_button.image = clear_icon  # Mantener referencia

    # Botón "Adjuntar"
    attach_button = tk.Button(
        button_frame, image=attach_icon, command=attach_file,
        bg='#2e2e2e', activebackground='#3e3e3e', borderwidth=0
    )
    attach_button.pack(side=tk.TOP, padx=5, pady=5)
    attach_button.image = attach_icon  # Mantener referencia

    # Calcular el ancho del campo de entrada (ajustado al right_frame)
    entry_width = (screen_width * 4) // 5  # 4/5 del ancho de pantalla

    # Frame para la entrada de texto y su scrollbar
    entry_frame = tk.Frame(input_frame, width=entry_width, height=100, bg='#2e2e2e')
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

    # Cargar el historial de conversaciones existentes
    load_conversation_history()

    # Iniciar la primera conversación
    start_new_conversation()

# Ejemplo de uso:
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry('800x600')
    open_chat_frame(root)
    root.mainloop()
