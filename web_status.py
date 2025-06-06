from flask import Flask, request, render_template_string, jsonify
import subprocess
import threading
import os
import signal
import hashlib
import time
import datetime

app = Flask(__name__)

tmate_ssh = None
tmate_process = None
start_time = time.time()
PASSWORD_HASH = hashlib.sha256(b"hieuxyz2009").hexdigest()
UPLOAD_FOLDER = '/home/ubuntu'

def set_process_name(name):
    import ctypes
    libc = ctypes.cdll.LoadLibrary('libc.so.6')
    buff = ctypes.create_string_buffer(len(name)+1)
    buff.value = name.encode('ascii')
    libc.prctl(15, ctypes.byref(buff), 0, 0, 0)

def run_tmate():
    global tmate_ssh, tmate_process
    try:
        if tmate_process:
            os.killpg(os.getpgid(tmate_process.pid), signal.SIGTERM)
        
        # Xóa socket cũ nếu có
        if os.path.exists('/tmp/tmate.sock'):
            os.remove('/tmp/tmate.sock')
        
        # Tạo session mới với socket
        subprocess.run(['tmate', '-S', '/tmp/tmate.sock', 'new-session', '-d'], check=True)
        
        # Đợi tmate sẵn sàng
        subprocess.run(['tmate', '-S', '/tmp/tmate.sock', 'wait', 'tmate-ready'], check=True)
        
        # Lấy SSH command và lưu vào file
        subprocess.run(['tmate', '-S', '/tmp/tmate.sock', 'display', '-p', '#{tmate_ssh}'], 
                      stdout=open('tmate_info.txt', 'w'), check=True)
        
        # Đọc SSH command từ file
        with open('tmate_info.txt', 'r') as f:
            tmate_ssh = f.read().strip()
        
        print(f"Tmate SSH: {tmate_ssh}")
        
    except Exception as e:
        print(f"Error starting tmate: {e}")
        tmate_ssh = None

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tmate Control</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                line-height: 1.6; 
                padding: 20px; 
                background-color: #f4f4f4;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .uptime {
                background: #e8f4fd;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 20px;
                border-left: 4px solid #007acc;
            }
            form { margin-bottom: 20px; }
            input[type="password"] { 
                padding: 8px; 
                margin-right: 10px; 
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            input[type="submit"] { 
                padding: 8px 15px; 
                background: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 5px;
            }
            input[type="submit"]:hover {
                background: #005a99;
            }
            input[type="file"] {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .ssh-info {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #e9ecef;
                font-family: monospace;
                word-break: break-all;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Tmate Control</h1>
            
            <div class="uptime">
                <h3>Server Uptime: <span id="uptime">Calculating...</span></h3>
            </div>
            
            <form action="/tmate" method="post">
                <input type="password" name="password" placeholder="Enter password" required>
                <input type="submit" name="action" value="View SSH">
                <input type="submit" name="action" value="New Session">
            </form>
            
            <h2>File Upload</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="files" multiple>
                <input type="submit" value="Upload">
            </form>
        </div>

        <script>
            function updateUptime() {
                fetch('/uptime')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('uptime').textContent = data.uptime;
                    })
                    .catch(error => {
                        console.error('Error fetching uptime:', error);
                    });
            }

            // Cập nhật uptime mỗi giây
            updateUptime();
            setInterval(updateUptime, 1000);
        </script>
    </body>
    </html>
    ''')

@app.route('/uptime')
def get_uptime():
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    if days > 0:
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        uptime_str = f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        uptime_str = f"{minutes}m {seconds}s"
    else:
        uptime_str = f"{seconds}s"
    
    return jsonify({'uptime': uptime_str})

@app.route('/tmate', methods=['POST'])
def tmate_action():
    password = request.form.get('password')
    action = request.form.get('action')

    if not password or hashlib.sha256(password.encode()).hexdigest() != PASSWORD_HASH:
        return 'Invalid password', 403

    if action == 'View SSH':
        if tmate_ssh:
            return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Tmate SSH Info</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        padding: 20px; 
                        background-color: #f4f4f4;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }
                    .ssh-command {
                        background: #2d3748;
                        color: #e2e8f0;
                        padding: 15px;
                        border-radius: 5px;
                        font-family: monospace;
                        font-size: 14px;
                        word-break: break-all;
                        margin: 20px 0;
                    }
                    .copy-btn {
                        background: #48bb78;
                        color: white;
                        border: none;
                        padding: 10px 15px;
                        border-radius: 5px;
                        cursor: pointer;
                        margin-top: 10px;
                    }
                    .copy-btn:hover {
                        background: #38a169;
                    }
                    .back-btn {
                        background: #4299e1;
                        color: white;
                        text-decoration: none;
                        padding: 10px 15px;
                        border-radius: 5px;
                        display: inline-block;
                        margin-top: 20px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Tmate SSH Connection</h1>
                    <p>Use the following SSH command to connect:</p>
                    <div class="ssh-command" id="sshCommand">{{ ssh_command }}</div>
                    <button class="copy-btn" onclick="copyToClipboard()">Copy Command</button>
                    <br>
                    <a href="/" class="back-btn">← Back to Home</a>
                </div>

                <script>
                    function copyToClipboard() {
                        const sshCommand = document.getElementById('sshCommand').textContent;
                        navigator.clipboard.writeText(sshCommand).then(() => {
                            alert('SSH command copied to clipboard!');
                        }).catch(err => {
                            console.error('Failed to copy: ', err);
                        });
                    }
                </script>
            </body>
            </html>
            ''', ssh_command=tmate_ssh)
        return 'Tmate SSH command not available yet', 404
    elif action == 'New Session':
        threading.Thread(target=run_tmate).start()
        return 'New tmate session started. Please wait a moment and then view the SSH command.', 202

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return 'Không có file nào được chọn'
    files = request.files.getlist('files')
    if not files:
        return 'Không có file nào được chọn'
    saved_files = []
    for file in files:
        if file.filename:
            filename = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filename)
            saved_files.append(file.filename)
    if saved_files:
        return f'Các file sau đã được upload thành công: {", ".join(saved_files)}'
    return 'Không có file nào được chọn'

if __name__ == '__main__':
    set_process_name("critical_process")
    tmate_thread = threading.Thread(target=run_tmate)
    tmate_thread.start()
    app.run(host='0.0.0.0', port=80)
