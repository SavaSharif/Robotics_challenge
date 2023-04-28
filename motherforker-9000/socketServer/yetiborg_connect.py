import socket
import threading
import time 
# Receiving port 8787

BUFFER_SIZE = 1024
SHUTDOWN_COMMANDS = ["q", "shutdown", "exit"]

class Sender(threading.Thread):
    def __init__(self, yetiborg,\
                 rec_ip='192.168.2.100', rec_port=8787):
        
        threading.Thread.__init__(self)
        self.rec_ip = rec_ip
        self.rec_port = rec_port

        self.yetiborg = yetiborg
        self.running = True

        self.img2send = None
        self.message2send = None

        self.t_req = 0
        self.t_start = 0
        self.t_done = 0

    def run(self):
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_socket.connect((self.rec_ip, self.rec_port))

        while self.running:
            if self.img2send != None:
                self.t_start = time.time()
                sender_socket.sendall(self.img2send)
                self.img2send = None
                self.t_done = time.time()
                print("Time passed since send img request:", self.t_done - self.t_req)
                print("Sending time:", self.t_done - self.t_start)
                
            if self.message2send != None:
                sender_socket.sendall(bytes("msg:" + self.message2send, "utf-8"))
                if self.message2send in SHUTDOWN_COMMANDS: self.running = False
                self.message2send = None

        sender_socket.close()
            

class Receiver(threading.Thread):
    def __init__(self, yetiborg,\
                rec_ip='192.168.2.101', rec_port=8787):
        threading.Thread.__init__(self)
        self.rec_ip = rec_ip
        self.rec_port = rec_port

        self.yetiborg = yetiborg
        self.running = True

    def run(self):
        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receiver_socket.bind((self.rec_ip, self.rec_port))

        receiver_socket.listen(2)
        conn, _ = receiver_socket.accept()

        while self.running:
            received_message = conn.recv(BUFFER_SIZE)
            if received_message:
                print("Received message")
                if str(received_message[0:4]) == "msg:":
                    received_message = received_message.decode("utf-8")
                    received_message = received_message[4:]
                    print(received_message)
                    if received_message in SHUTDOWN_COMMANDS: self.running = False
                else:
                    myfile = open("testimage.jpg", 'wb')
                    myfile.write(received_message)
                    myfile.close()

        conn.close()
        receiver_socket.close()


class YetiBorgClient:
    def __init__(self,\
                 yetiborg_ip='192.168.2.101',\
                 server_ip="192.168.2.100"):
        self.yetiborg_ip = yetiborg_ip
        self.server_ip = server_ip

        print("Server IP", server_ip)
        print("Yetiborg IP", yetiborg_ip)

        # self.receiver = Receiver(self, self.yetiborg_ip)
        # self.sender = Sender(self, self.server_ip)

        # Local testing
        self.receiver = Receiver(self, self.yetiborg_ip, 8787)
        self.sender = Sender(self, self.server_ip, 8989)

        self.running = True

    def run(self):
        self.receiver.start()
        print("Yetiborg receiver started, make sure server receiver is started before continuing")
        _ = input("Press enter to continue")
        self.sender.start()
        while self.running:
            message = input("Please type something")
            if message == "image":
                self.sender.t_req = time.time()
                myfile = open("face.png", "rb")
                bytes2send = myfile.read()
                self.sender.img2send = bytes2send
                
            else:
                self.sender.message2send = message
                if message in SHUTDOWN_COMMANDS:
                    self.running = False
        

# client = YetiBorgClient('192.168.2.101', '192.168.2.103')
client = YetiBorgClient(server_ip=socket.gethostbyname(socket.gethostname()), yetiborg_ip=socket.gethostbyname(socket.gethostname()))
client.run()