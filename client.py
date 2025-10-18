import customtkinter as ctk
import socketio
import threading

# === Налаштування ===
RENDER_SERVER_URL = 'https://merezha-2-ruj3.onrender.com'

# === Socket.IO клієнт ===
sio = socketio.Client()
private_message_clients = None


class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Мережевий чат")
        self.geometry("600x500")

        # === Верхня панель: прізвисько ===
        self.username_label = ctk.CTkLabel(self, text="Прізвисько:")
        self.username_label.pack(pady=5)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Введіть своє прізвисько")
        self.username_entry.pack(pady=5)

        self.connect_button = ctk.CTkButton(self, text="Підключитися", command=self.connect_to_server)
        self.connect_button.pack(pady=5)

        # === Лог повідомлень ===
        self.chat_log = ctk.CTkTextbox(self, width=550, height=250)
        self.chat_log.pack(pady=10)
        self.chat_log.configure(state="disabled")

        # === Поле для вводу повідомлень ===
        self.message_entry = ctk.CTkEntry(self, placeholder_text="Введіть повідомлення...")
        self.message_entry.pack(fill="x", padx=10, pady=5)

        self.send_button = ctk.CTkButton(self, text="Надіслати", command=self.send_message)
        self.send_button.pack(pady=5)

        # === Кнопки команд ===
        self.commands_frame = ctk.CTkFrame(self)
        self.commands_frame.pack(pady=10)

        self.users_button = ctk.CTkButton(self.commands_frame, text="/users", command=lambda: sio.emit("users"))
        self.users_button.grid(row=0, column=0, padx=5)

        self.random_button = ctk.CTkButton(self.commands_frame, text="randomito", command=lambda: sio.emit("random"))
        self.random_button.grid(row=0, column=1, padx=5)

        self.nova_button = ctk.CTkButton(self.commands_frame, text="nova", command=lambda: sio.emit("nova"))
        self.nova_button.grid(row=0, column=2, padx=5)

        self.private_button = ctk.CTkButton(self.commands_frame, text="Приват", command=lambda: sio.emit("users", "start"))
        self.private_button.grid(row=0, column=3, padx=5)

    def log_message(self, text):
        self.chat_log.configure(state="normal")
        self.chat_log.insert("end", text + "\n")
        self.chat_log.see("end")
        self.chat_log.configure(state="disabled")

    def connect_to_server(self):
        username = self.username_entry.get().strip()
        if not username:
            self.log_message("[‼️] Введіть прізвисько!")
            return

        def run_client():
            try:
                sio.connect(RENDER_SERVER_URL)
                sio.emit("set_username", username)
            except Exception as e:
                self.log_message("[‼️] Трабли зі з'єднанням: " + str(e))

        threading.Thread(target=run_client, daemon=True).start()

    def send_message(self):
        msg = self.message_entry.get().strip()
        if msg:
            sio.send(msg)
            self.message_entry.delete(0, "end")


# === Обробники socket.io ===
@sio.event
def connect():
    app.log_message("[✔️] Підключений до серверу.")


@sio.event
def disconnect():
    app.log_message("[❌] Кікнуто.")


@sio.on("message")
def on_message(data):
    app.log_message(str(data))


@sio.on("private_message")
def send_message_private(data):
    global private_message_clients
    app.log_message("[CLIENT] Отримано список для приватного чату.")
    private_message_clients = data["clients"]


# === Запуск програми ===
app = ChatApp()
app.mainloop()
