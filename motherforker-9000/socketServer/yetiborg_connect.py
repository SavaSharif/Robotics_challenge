import socket
import threading

# Receiving port 8787
# Sending port 8989

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

    def run(self):
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_socket.connect((self.rec_ip, self.rec_port))

        while self.running:
            if self.img2send != None:
                # TODO sending images
                self.img2send = None
                
            if self.message2send != None:
                sender_socket.sendall(bytes(self.message2send, "utf-8"))
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
                received_message = received_message.decode("utf-8")
                print(received_message)
                if received_message in SHUTDOWN_COMMANDS: self.running = False

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

        self.receiver = Receiver(self, self.yetiborg_ip)
        self.sender = Sender(self, self.server_ip)

        self.running = True

    def run(self):
        self.receiver.start()
        print("Yetiborg receiver started, make sure server receiver is started before continuing")
        _ = input("Press enter to continue")
        self.sender.start()
        while self.running:
            message = input()
            self.sender.message2send = message
            if message in SHUTDOWN_COMMANDS:
                self.running = False
        

client = YetiBorgClient('192.168.2.101', '192.168.2.103')
client.run()