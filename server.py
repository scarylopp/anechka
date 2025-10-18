from flask import Flask, request
from flask_socketio import SocketIO, send, disconnect
import os, random

app = Flask(__name__)
app.config['SECRET_KEY'] = '!'
socketio = SocketIO(app, cors_allowed_origins='*')

# Зберігаємо імена користувачів за session ID
users = {}

@app.route('/')
def index():
    return 'Сервер працює!'

@socketio.on('nova')
def customFunction():
    print('Перевірка!')
    send('\n\n\n\n\n\n\n\nПеревірка успішна! =)')

@socketio.on('connect')
def handle_connect():
    print(f"[ПІДКЛЮЧЕННЯ] Клієнт: {request.sid}")

@socketio.on('set_username')
def handle_set_username(username):
    users[request.sid] = username
    print(f"[ІМʼЯ ВСТАНОВЛЕНО] {request.sid} тепер '{username}'")
    send(f"{username} приєднався до чату.", broadcast=True)

@socketio.on('message')
def handle_message(msg):
    username = users.get(request.sid, "Анонім")
    full_msg = f"{username}: {msg}"
    print(f"[ПОВІДОМЛЕННЯ] {full_msg}")
    send(full_msg, broadcast=True)

@socketio.on('random')
def generate_number():
    resultNum = random.randint(0,100)
    send(resultNum, broadcast=True)

@socketio.on('reserved')
def reserved():
    send(f"Ваша кастомна функція =>", to=request.sid)


@socketio.on('users')
def list_users(data=None):
    if data is None:
        data = ''
    
    user_list = list(users.values())
    send(f"[SERVER] Active users: {', '.join(user_list)}", to=request.sid)
    
    if data == 'start':
        print('emit success DMs')
        socketio.emit("private_message", {'clients': users}, to=request.sid)
        
@socketio.on('send_dm')   
def send_dm_msg(data):
    send(f"Receiver: {data['rcver']}, message: {data['msg']}", to=data['rcver'])

@socketio.on('disconnect')
def handle_disconnect():
    username = users.pop(request.sid, "Анонім")
    print(f"[ВІДКЛЮЧЕННЯ] {username} ({request.sid})")
    send(f"{username} вийшов з чату.", broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
