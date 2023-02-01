import PySimpleGUI as sg
import socketserver
import threading
import ssl
stop_thread = False

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        window['output'].print('Connected by', self.client_address)
        #window['output'].print('Received', self.data) 
        self.request.sendall(b'HTTP/1.0 200 OK\n\nHello World')

def connect(host, port, use_https):
    global stop_thread
    try:
        window['output'].print('Server started')
        if use_https:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile='./cert.pem', keyfile='./key.pem')
            with socketserver.TCPServer((host, port), Handler) as httpd:
                httpd.allow_reuse_address = True
                httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
                while not stop_thread:
                    httpd.handle_request()
                    if stop_thread:
                        httpd.server_close()
            pass
        else:
            with socketserver.TCPServer((host, port), Handler) as httpd:
                httpd.allow_reuse_address = True
                while not stop_thread:
                    httpd.handle_request()
                    if stop_thread:
                        httpd.server_close()
                        break
    except:
        pass

def main():
    global window
    global stop_thread
    layout = [
        [sg.Text('Host:'), sg.InputText(key='host', default_text='localhost')],
        [sg.Text('Port:'), sg.InputText(key='port', default_text='80')],
        [sg.Checkbox("HTTPS", key="https")],
        [sg.Button('Start', key="connect"), sg.Button('Stop', key="stop"), sg.Button('Exit', key="exit")],
        [sg.Multiline(key='output', size=(80, 10), autoscroll=True, reroute_stdout=True, reroute_cprint=True, disabled=True)]
    ]

    window = sg.Window('Simple HTTP Server With GUI', layout, finalize=True)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'exit':
            stop_thread = True
            break
        elif event == 'connect':
            window['output'].update(disabled=True)
            window['connect'].update(disabled=True)
            window['exit'].update(disabled=True)
            window['host'].update(disabled=True)
            window['port'].update(disabled=True)
            window['stop'].update(disabled=False)
            use_https = values["https"]
            threading.Thread(target=connect, args=(values['host'], int(values['port']), use_https)).start()
            stop_thread = False
        elif event == 'stop':
            window['output'].update(disabled=True)
            window['connect'].update(disabled=False)
            window['exit'].update(disabled=False)
            window['host'].update(disabled=False)
            window['port'].update(disabled=False)
            window['stop'].update(disabled=True)
            window['output'].print('Server stopped')
            stop_thread = True

    window.close()

if __name__ == '__main__':
    main()
