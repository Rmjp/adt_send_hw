from paramiko import SSHClient, AutoAddPolicy
from dotenv import dotenv_values
from flask import Flask, jsonify, request, render_template
import os

env_path = os.environ.get('ENV_PATH')

env = dotenv_values(env_path)
HOST = env['HOST']
USER = env['USER']
PASSWORD = env['PASSWORD']
PORT = env['PORT']
AUTH = env['AUTH']
current_dir = os.getcwd()
print(HOST, USER, PASSWORD, PORT)
client = SSHClient()
client.set_missing_host_key_policy(AutoAddPolicy())
client.connect(HOST, username=USER, password=PASSWORD,port=PORT)

def check_connect():
    if not client.get_transport().is_active():
        client.connect(HOST, username=USER, password=PASSWORD,port=PORT)

def hw_status():
    check_connect()
    stdin, stdout, stderr = client.exec_command('hw-status --all')
    return stdout.read().decode('utf-8')

def hw_send(lab_name, file_name):
    check_connect()
    stdin, stdout, stderr = client.exec_command('hw-send '+lab_name+' '+ "~/send/" + file_name)
    return stdout.read().decode('utf-8') + stderr.read().decode('utf-8')

def send_file_to_server(file_name):
    check_connect()
    sftp = client.open_sftp()
    print(current_dir + "/" +file_name)
    sftp.put(current_dir + "/" +file_name, './send/'+file_name)
    sftp.close()

def check_auth(auth):
    if auth == AUTH:
        return True
    return False

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    val = request.cookies.get('auth')
    if not check_auth(val):
        return 'Not Auth', 401
    if 'file' not in request.files:
        return 'No file part in the request', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    new_filename = 'send.c'  # Specify the new filename here

    file.save(new_filename)
    send_file_to_server(new_filename)
    lab_name = request.form['lab_name']
    return hw_send(lab_name, new_filename)

'''
+-------------------+-------+---------+-----------------------------------+------------+
|      LABNAME      | LABNO | #SUBMIT |              STATUS               |  DUEDATE   |
+-------------------+-------+---------+-----------------------------------+------------+
|    helloWorld     |  01   |    1    |                 P                 | 10/7/2023  |
|     trapezoid     |  01   |    6    |               PPPP                | 10/7/2023  |
|      waiting      |  01   |    1    |               PPPP                | 10/7/2023  |
|   timeConverter   |  01   |    3    |               PPPPP               | 10/7/2023  |
|   asciiCompare    |  01   |    0    |             NOT SEND              | 10/7/2023  |
|       eater       |  01   |    0    |             NOT SEND              | 10/7/2023  |
+-------------------+-------+---------+-----------------------------------+------------+
'''
@app.route('/status')
def status():
    val = request.cookies.get('auth')
    if not check_auth(val):
        return 'Not Auth', 401
    status = hw_status()
    return status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)

client.close()