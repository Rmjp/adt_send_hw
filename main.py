from paramiko import SSHClient, AutoAddPolicy
from dotenv import dotenv_values
from flask import Flask, jsonify, request

env = dotenv_values('.env')
HOST = env['HOST']
USER = env['USER']
PASSWORD = env['PASSWORD']
PORT = env['PORT']

print(HOST, USER, PASSWORD, PORT)
client = SSHClient()
client.load_system_host_keys()
client.load_host_keys('~/.ssh/known_hosts')
client.set_missing_host_key_policy(AutoAddPolicy())
client.connect(HOST, username=USER, password=PASSWORD,port=PORT)

def check_connect():
    if not client.get_transport().is_active():
        client.connect(HOST, username=USER,port=PORT)

def hw_status():
    check_connect()
    stdin, stdout, stderr = client.exec_command('hw-status --all')
    return stdout.read().decode('utf-8')

def hw_send(lab_name, file_name):
    check_connect()
    stdin, stdout, stderr = client.exec_command('hw-send '+lab_name+' '+file_name)
    return stdout.read().decode('utf-8')

def send_file_to_server(file_name):
    check_connect()
    sftp = client.open_sftp()
    sftp.put(file_name, '~/send/'+file_name)
    sftp.close()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
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
    status = hw_status()
    return status

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3002)

client.close()