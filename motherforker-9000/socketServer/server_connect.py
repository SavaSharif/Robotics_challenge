import socket
import threading

# Receiving port 8787
# Sending port 8989

BUFFER_SIZE = 1024
SHUTDOWN_COMMANDS = ["q", "shutdown", "exit"]

class Sender(threading.Thread):
    def __init__(self, server,\
                 rec_ip='192.168.2.101', rec_port=8787):
        threading.Thread.__init__(self)
        self.rec_ip = rec_ip
        self.rec_port = rec_port

        self.server = server
        self.running = True

        self.img2send = None
        self.message2send = None

    def run(self):
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_socket.connect((self.rec_ip, self.rec_port))

        while self.running:
            if self.img2send != None:
                # TODO sending images, start with prefix 'img:' 
                self.img2send = None
                
            if self.message2send != None:
                sender_socket.sendall(bytes("msg:" + self.message2send, "utf-8"))
                if self.message2send in SHUTDOWN_COMMANDS: self.running = False
                self.message2send = None

        sender_socket.close()
            

class Receiver(threading.Thread):
    def __init__(self, server,\
                rec_ip='192.168.2.100', rec_port=8787):
        threading.Thread.__init__(self)
        self.rec_ip = rec_ip
        self.rec_port = rec_port

        self.server = server
        self.running = True

    def run(self):
        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receiver_socket.bind((self.rec_ip, self.rec_port))

        receiver_socket.listen(2)
        conn, _ = receiver_socket.accept()

        while self.running:
            received_message = conn.recv(BUFFER_SIZE)
            if received_message:
                received_message = received_message.decode("utf-8")
                if received_message[:3] == "msg:":
                    received_message = received_message[4:]
                    print(received_message)
                    if received_message in SHUTDOWN_COMMANDS: self.running = False

        conn.close()
        receiver_socket.close()


class ServerBorgClient:
    def __init__(self,\
                 yetiborg_ip='192.168.2.101',\
                 server_ip="192.168.2.100"):
        self.yetiborg_ip = yetiborg_ip
        self.server_ip = server_ip

        print("Server IP", server_ip)
        print("Yetiborg IP", yetiborg_ip)

        self.receiver = Receiver(self, self.server_ip)
        self.sender = Sender(self, self.yetiborg_ip)

        self.running = True

    def run(self):
        self.receiver.start()
        print("Server receiver started, make sure yetiborg receiver is started before continuing")
        _ = input("Press enter to continue")
        self.sender.start()
        while self.running:
            message = input()
            if message == "image":
                myfile = open("motherforker-9000/face.jpg")
                bytes = myfile.read()
                
            else:
                self.sender.message2send = message
                if message in SHUTDOWN_COMMANDS:
                    self.running = False

server = ServerBorgClient(server_ip=socket.gethostbyname(socket.gethostname()))
server.run()