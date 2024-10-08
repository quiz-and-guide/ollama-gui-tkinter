# chat.py
import tkinter as tk
from tkinter import scrolledtext, filedialog
from tkinter import Canvas
from PIL import Image, ImageTk
import subprocess
import requests
import json
import os
import re

class GUI:
    rows = 50
    columns = 8
    dim_square = 400

    def __init__(self, parent_frame):
        self.conversation = []
        self.conversation_filename = None
        self.parent_frame = parent_frame

        
        # Cargar imágenes y mantener referencias
        self.clear_icon = self.load_image("./icons/clear.png")
        self.clear_icon_small = self.load_image("./icons/clear_small.png")
        self.new_chat_icon = self.load_image("./icons/new_chat.png")
        self.play_icon = self.load_image("./icons/play.png")
        self.attach_icon = self.load_image("./icons/attach.png")
        self.copy_icon = self.load_image("./icons/copy.png")

        # Crear el frame principal que contendrá left_frame y right_frame
        self.main_frame = tk.Frame(parent_frame, bg='#2e2e2e')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar Left Frame (Historial de Chats)
        self.setup_left_frame()

        # Configurar Right Frame (Chat y Controles)
        self.setup_right_frame()

        # Inicializar Conversaciones
        self.add_new_chat()
        self.load_conversation_history()
        self.start_new_conversation()

    def load_image(self, path):
        try:
            image = Image.open(path)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

    def setup_left_frame(self):
        # Obtener el ancho de la pantalla para el left_frame
        screen_width = self.parent_frame.winfo_screenwidth()
        left_frame_width = screen_width // 5

        self.left_frame = tk.Frame(self.main_frame, width=left_frame_width, bg='#2e2e2e')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)  # Evitar que el frame cambie de tamaño

        # Canvas para el historial de chats con scrollbar
        self.canvas_left = tk.Canvas(self.left_frame, bg='#2e2e2e', highlightthickness=0)
        self.canvas_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar_left = tk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.canvas_left.yview)
        self.scrollbar_left.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_left.configure(yscrollcommand=self.scrollbar_left.set)

        self.chat_history_frame = tk.Frame(self.canvas_left, bg='#2e2e2e')
        self.canvas_left.create_window((0, 0), window=self.chat_history_frame, anchor='nw')

        # Configurar el scroll region
        self.chat_history_frame.bind("<Configure>", lambda event: self.canvas_left.configure(scrollregion=self.canvas_left.bbox("all")))

    def setup_right_frame(self):
        self.right_frame = tk.Frame(self.main_frame, bg='#2e2e2e')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        #self.canvas_right = tk.Canvas(self.right_frame, bg='#2e2e2e', highlightthickness=0)
        #self.canvas_right.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
         # Área de texto para mostrar el historial del chat
        # Menu de Selección de Modelo
        self.setup_model_menu()
        
        self.chat_history = scrolledtext.ScrolledText(
            self.right_frame, state='normal', width=50, height=20,
            bg='#1e1e1e', fg='white', insertbackground='white',
            highlightbackground='#2e2e2e', highlightcolor='#2e2e2e'
        )
        self.chat_history.pack(pady=10, fill=tk.BOTH, expand=True)
        

        # Input Frame para escribir mensajes
        self.input_frame = tk.Frame(self.right_frame, bg='#2e2e2e')
        self.input_frame.pack(padx=10, pady=10, fill=tk.X)

        self.entry = tk.Text(
            self.input_frame,
            bg='#1e1e1e',
            fg='white',
            insertbackground='white',
            height=5,
            wrap=tk.WORD
        )
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.scrollbar_entry = tk.Scrollbar(self.input_frame, orient=tk.VERTICAL, command=self.entry.yview)
        self.entry.configure(yscrollcommand=self.scrollbar_entry.set)
        self.scrollbar_entry.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de Enviar y Adjuntar
        self.button_frame = tk.Frame(self.input_frame, bg='#2e2e2e')
        self.button_frame.pack(side=tk.RIGHT)
        
        self.send_button = tk.Button(
            self.button_frame, 
            image=self.play_icon, 
            command=self.send_message, 
            bg='#2e2e2e', 
            activebackground='#3e3e3e', 
            borderwidth=0
        )
        if self.play_icon:
            self.send_button.image = self.play_icon  # Mantener referencia
        self.send_button.pack(side=tk.TOP, padx=2)

        self.attach_button = tk.Button(
            self.button_frame,
            image=self.attach_icon,  
            command=self.attach_file, 
            bg='#2e2e2e', 
            activebackground='#3e3e3e', 
            borderwidth=0
        )
        if self.attach_icon:
            self.attach_button.image = self.attach_icon  # Mantener referencia
        self.attach_button.pack(side=tk.TOP, padx=2)

        self.clear_button = tk.Button(
            self.button_frame,
            image=self.clear_icon,  
            command=self.clear_chat,
            bg='#2e2e2e', 
            activebackground='#3e3e3e', 
            borderwidth=0
        )
        if self.clear_icon:
            self.clear_button.image = self.clear_icon  # Mantener referencia
        self.clear_button.pack(side=tk.RIGHT, padx=2)

    def setup_model_menu(self):
        models = self.get_installed_models()
        if models:
            self.model_var = tk.StringVar(self.right_frame)
            self.model_var.set(models[1])  # Seleccionar el primer modelo por defecto

            model_menu = tk.OptionMenu(self.right_frame, self.model_var, *models)
            model_menu.configure(
                bg='#2e2e2e',
                fg='white',
                activebackground='#3e3e3e',
                activeforeground='white',
                highlightthickness=0,
            )
            model_menu['menu'].configure(bg='#2e2e2e', fg='white')
            model_menu.pack(pady=5)
        else:
            print("No se encontraron modelos instalados.")

    def clear_chat(self):
        self.chat_history.configure(state='normal')
        self.chat_history.delete(1.0, tk.END)
        self.chat_history.configure(state='disabled')

    def attach_file(self):
        file_path = filedialog.askopenfilename()        
        if not file_path:
            return  # Usuario canceló el diálogo o no seleccionó ningún archivo
        try:
            with open(file_path, 'r') as file:
                self.file_content = file.read()
                attached_file_text = self.file_content
                self.entry.config(state='normal')
                self.entry.insert(tk.END, f"Archivo adjunto:\n{attached_file_text}\n")
        except Exception as e:
            print(f"Error leyendo el archivo: {e}")

    def get_installed_models(self):
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if not lines:
                return []
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

    def send_message(self):
        user_input = self.entry.get("1.0", tk.END).strip()
        if user_input == "":
            return
        self.entry.delete("1.0", tk.END)
        self.chat_history.configure(state='normal')
        self.chat_history.insert(tk.END, "\n\nTú: " + user_input + "\n\n")

        selected_model = self.model_var.get()

        last_user_messages = [msg['content'] for msg in self.conversation if msg['role'] == 'user'][-4:]

        if last_user_messages:
            context = "Contexto: " + ", ".join(last_user_messages) + " Pregunta actual -> " + user_input
        else:
            context = user_input

        response = self.get_ollama_response(context, selected_model)

        # Insert assistant's message
        ai_message = f"{selected_model}: {response}\n\n"
        self.chat_history.insert(tk.END, ai_message)
        self.chat_history.configure(state='disabled')
        self.chat_history.see(tk.END)

        self.conversation.append({'role': 'user', 'content': user_input})
        self.conversation.append({'role': 'assistant', 'content': response})

        # Save conversation and handle first message logic
        self.save_conversation()
        if self.conversation_filename == "history/temp_conversation.json":
            display_name = self.sanitize_filename(user_input[:20])
            filename_base = display_name
            new_conversation_filename = f'history/{filename_base}.json'
            os.rename("history/temp_conversation.json", new_conversation_filename)
            conversation_filename = new_conversation_filename
            self.load_conversation(conversation_filename)
            self.save_conversation()
        else:
            self.save_conversation()
        # Now create the copy_button after loading the conversation
        last_ai_message = [msg['content'] for msg in self.conversation if msg['role'] == 'assistant'][-1]
        copy_button = tk.Button(
            self.chat_history,
            image=self.copy_icon,
            command=lambda msg=last_ai_message: self.copy_to_clipboard(msg),
            borderwidth=0,
            bg='#1e1e1e',
            activebackground='#1e1e1e'
        )
        self.chat_history.window_create(tk.END, window=copy_button)
        if not hasattr(self, 'widgets'):
            self.widgets = []
        self.widgets.append(copy_button)
        # Create a new file if this is the first message
        print("conversación: " + self.conversation_filename)
        
            #self.change_conversation_history_name(display_name)
        if len(self.conversation) == 2:
            display_name = self.sanitize_filename(user_input[:20])
            self.change_conversation_history_name(display_name)
            #self.add_conversation_to_history(display_name,self.conversation_filename)
    def change_conversation_history_name(self, display_name):
        self.label.config(text=display_name)
    def get_ollama_response(self, prompt, model):
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
            return api_response.get('response', "No se encontró el campo 'response' en la respuesta de la API.")
        except requests.exceptions.RequestException as e:
            return f"Error en la solicitud a la API: {e}"
        except (ValueError, KeyError) as e:
            return f"Error procesando la respuesta de la API: {e}"

    def sanitize_filename(self, name):
        return re.sub(r'[\\/*?:"<>|]', "", name)

    def start_new_conversation_new_chat(self):
        self.conversation = []
        self.clear_chat()
        display_name = "New chat"
        file_name = ("temp_conversation")
        self.conversation_filename = f'history/{file_name}.json'
        print("Viene de new chat")
        self.add_conversation_to_history(display_name, self.conversation_filename) 
    def start_new_conversation(self):
        self.conversation = []
        #self.save_conversation()
        files = [f for f in os.listdir('history') if f.endswith('.json')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join('history', x)), reverse=True)
        self.conversation_filename = files[0]
        print("files[0]" + self.conversation_filename)
        self.clear_chat()
    def save_conversation(self):
        print("saving conversation")
        os.makedirs('history', exist_ok=True)
        with open(self.conversation_filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation, f, ensure_ascii=False, indent=4)

    def load_conversation_history(self):
        print("Viene de load_conversatio history")
        files = [f for f in os.listdir('history') if f.endswith('.json')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join('history', x)), reverse=True)
        for filename in files:
            filepath = os.path.join('history', filename)
            display_name = os.path.splitext(filename)[0]
            self.add_conversation_to_history(display_name, filepath)
        print("Load conversation history, ¿es correcto?")
    def load_conversation(self, filepath):
        print("Load conversation")
        print(filepath)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.conversation = json.load(f)
            self.conversation_filename = filepath
            self.chat_history.configure(state='normal')
            self.chat_history.delete(1.0, tk.END)
            for message in self.conversation:
                role = message['role']
                content = message['content']
                if role == 'user':
                    self.chat_history.insert(tk.END, f"Tú: {content}\n\n")
                elif role == 'assistant':
                    self.chat_history.insert(tk.END, f"{self.model_var.get()}: {content}\n\n")
            self.chat_history.configure(state='disabled')
            self.chat_history.see(tk.END)

    def delete_conversation(self, filepath, row_frame):
        row_frame.destroy()
        if os.path.exists(filepath):
            os.remove(filepath)
        if self.conversation_filename == filepath:
            self.conversation = []
            self.conversation_filename = None
            self.clear_chat()

    def add_conversation_to_history(self, display_name, filepath):
        print(filepath)
        print("Viene de add_conversation_to_history")
        row_frame = tk.Frame(self.chat_history_frame, bg='#2e2e2e')
        row_frame.pack(fill=tk.X, pady=2)

        # Label con el nombre de la conversación
        self.label = tk.Label(row_frame, text=display_name, bg='#2e2e2e', fg='white')
        self.label.pack(side=tk.LEFT, padx=5)
        self.label.bind("<Button-1>", lambda e, fp=filepath: self.load_conversation(fp))
        
        delete_button = tk.Button(
            row_frame, 
            image=self.clear_icon_small,
            command=lambda fp=filepath, rf=row_frame: self.delete_conversation(fp, rf), 
            bg='#2e2e2e', 
            borderwidth=0, 
            activebackground='#3e3e3e'
        )
        delete_button.image = self.clear_icon_small  # Mantener referencia
        delete_button.pack(side=tk.RIGHT, padx=5)

        # Keep references
        
        #self.label.row_frame = row_frame
        #row_frame.filepath = filepath
        
    def add_new_chat(self):
        row_frame = tk.Frame(self.chat_history_frame, bg='#2e2e2e')
        row_frame.pack(fill=tk.X, pady=2)

        # Label "Nueva conversación"
        label_new = tk.Label(row_frame, text="New chat", bg='#2e2e2e', fg='white', anchor='w')
        label_new.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        label_new.bind("<Button-1>", lambda event: self.start_new_conversation())  # Added parentheses

        # Botón para iniciar una nueva conversación
        if self.new_chat_icon:
            new_chat_button = tk.Button(
                row_frame, 
                image=self.new_chat_icon,
                command=self.start_new_conversation_new_chat, 
                bg='#2e2e2e', 
                borderwidth=0, 
                activebackground='#3e3e3e'
            )
            new_chat_button.image = self.new_chat_icon  # Mantener referencia
            new_chat_button.pack(side=tk.RIGHT, padx=5)

    def copy_to_clipboard(self, msg):
        root = self.chat_history.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append(msg)
        root.update()

def main(parent_frame):
    gui = GUI(parent_frame)

if __name__ == "__main__":
    main()
