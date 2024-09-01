from flask import Flask, request, render_template_string
import subprocess
import threading
import os
import signal
import hashlib

app = Flask(__name__)

tmate_url = None
tmate_process = None
PASSWORD_HASH = hashlib.sha256(b"your_password_here").hexdigest()  # Thay "your_password_here" bằng mật khẩu thực

def set_process_name(name):
    import ctypes
    libc = ctypes.cdll.LoadLibrary('libc.so.6')
    buff = ctypes.create_string_buffer(len(name)+1)
    buff.value = name.encode('ascii')
    libc.prctl(15, ctypes.byref(buff), 0, 0, 0)

def run_tmate():
    global tmate_url, tmate_process
    if tmate_process:
        os.killpg(os.getpgid(tmate_process.pid), signal.SIGTERM)
    tmate_process = subprocess.Popen(["tmate", "-F"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid)
    for line in tmate_process.stdout:
        if "web session:" in line:
            tmate_url = line.split(": ")[1].strip()
            break

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tmate Control</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
            form { margin-bottom: 20px; }
            input[type="password"] { padding: 5px; margin-right: 10px; }
            input[type="submit"] { padding: 5px 10px; }
        </style>
    </head>
    <body>
        <h1>Tmate Control</h1>
        <form action="/tmate" method="post">
            <input type="password" name="password" placeholder="Enter password" required>
            <input type="submit" name="action" value="View URL">
            <input type="submit" name="action" value="New Session">
        </form>
    </body>
    </html>
    ''')

@app.route('/tmate', methods=['POST'])
def tmate_action():
    password = request.form.get('password')
    action = request.form.get('action')

    if not password or hashlib.sha256(password.encode()).hexdigest() != PASSWORD_HASH:
        return 'Invalid password', 403

    if action == 'View URL':
        if tmate_url:
            return f'Tmate URL: {tmate_url}'
        return 'Tmate URL not available yet', 404
    elif action == 'New Session':
        threading.Thread(target=run_tmate).start()
        return 'New tmate session started. Please wait a moment and then view the URL.', 202

if __name__ == '__main__':
    set_process_name("critical_process")  # Đặt tên cho quá trình để bảo vệ nó
    tmate_thread = threading.Thread(target=run_tmate)
    tmate_thread.start()
    app.run(host='0.0.0.0', port=80)