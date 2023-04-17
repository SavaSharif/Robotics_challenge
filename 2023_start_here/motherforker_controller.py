import ZeroBorg3 as ZeroBorg
import sys, time
import tty, termios, fcntl, os, atexit
import numpy as np

old_settings=None

def init_any_key():
   global old_settings
   old_settings = termios.tcgetattr(sys.stdin)
   new_settings = termios.tcgetattr(sys.stdin)
   new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON) # lflags
   new_settings[6][termios.VMIN] = 0  # cc
   new_settings[6][termios.VTIME] = 0 # cc
   termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)


@atexit.register
def term_any_key():
   global old_settings
   if old_settings:
      termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def any_key():
   ch_set = []
   ch = os.read(sys.stdin.fileno(), 1)
   while ch is not None and len(ch) > 0:
      ch_set.append(ch)
      ch = os.read(sys.stdin.fileno(), 1)
   return ch_set


class _Getch:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        try:
            tty.setraw(sys.stdin.fileno())
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class ZBController:
    def __init__(self):
        self.time_start = time.time()

        # Setup the ZeroBorg
        self.ZB = ZeroBorg.ZeroBorg()
        #ZB.i2cAddress = 0x44                   # Uncomment and change the value if you have changed the board address
        self.ZB.Init()
        if not self.ZB.foundChip:
            boards = ZeroBorg.ScanForZeroBorg()
            if len(boards) == 0:
                print ('No ZeroBorg found, check you are attached :)')
            else:
                print ('No ZeroBorg at address %02X, but we did find boards:' % (self.ZB.i2cAddress))
                for board in boards:
                    print ('    %02X (%d)' % (board, board))
                print ('If you need to change the IC address change the setup line so it is correct, e.g.')
                print ('ZB.i2cAddress = 0x%02X' % (boards[0]))
            sys.exit()
        #ZB.SetEpoIgnore(True)                  # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
        self.ZB.SetCommsFailsafe(False)              # Disable the communications failsafe
        self.ZB.ResetEpo()


        # Movement settings (worked out from our YetiBorg v2 on a smooth surface)
        self.timeForward1m = 5.7                     # Number of seconds needed to move about 1 meter
        self.timeSpin360   = 4.8                     # Number of seconds needed to make a full left / right spin
        self.testMode = False                        # True to run the motion tests, False to run the normal sequence

        # Power settings
        self.voltageIn = 8.4                         # Total battery voltage to the ZeroBorg (change to 9V if using a non-rechargeable battery)
        self.voltageOut = 6.0                        # Maximum motor voltage

        # Setup the power limits
        if self.voltageOut > self.voltageIn:
            self.maxPower = 1.0
        else:
            self.maxPower = self.voltageOut / float(self.voltageIn)

        self.running = True
        self.active_commands = { # directionm number of seconds
            "forward" : 0.0,
            "left" : 0.0,
            "right" : 0.0,
            "backward" : 0.0
        }

        self.command2servo = {
            "forward" : np.array([1.0, 1.0, 1.0, 1.0]),
            "left" : np.array([1.0, 1.0, -1.0, -1.0]),
            "right": np.array([-1.0, -1.0, 1.0, 1.0]),
            "backward" : np.array([-1.0, -1.0, -1.0, -1.0])
        }

        self.command2break = {
            "forward" : np.array([-1.0, -1.0, -1.0, -1.0]),
            "left" : np.array([-0.5, -0.5, 0.5, 0.5]),
            "right": np.array([0.5, 0.5, -0.5, -.5]),
            "backward" : np.array([0.5, 0.5, 0.5, 0.5])
        }

        self.servos = [0.0, 0.0, 0.0, 0.0] # rr, fr, fl , rl
        self.brakes = [0.0, 0.0, 0.0, 0.0]
        
        self.current_time = time.time()


    def main(self):
        planned_commands = ["w", "d", "wd", "w", "d"]
        planned_command_times = [0, 2, 4, 6, 6.5]

        # Main loop
        while self.running:
            self.get_input()
            self.update_active_commands()
            self.update_servos()
            time.sleep(0.05)

    def update_active_commands(self):
        self.current_time = time.time()
        self.servos = np.array([0.0, 0.0, 0.0, 0.0])
        self.brakes = np.array([0.0, 0.0, 0.0, 0.0])
        for comm in self.active_commands.keys():
            if self.current_time < self.active_commands[comm]:
                self.servos += self.command2servo[comm]
            
            elif self.active_commands[comm] != 0.0:
                self.brakes += self.command2break[comm]
                self.active_commands[comm] = 0.0

        self.servos += self.brakes
        max_val = max((max(abs(self.servos)), 1.0))
        self.servos = self.servos / max_val

        
    def update_servos(self):
        # print("servos", self.servos)
        if max(self.servos) == 0.0 and max(self.servos):
            self.ZB.MotorsOff()
        
        else:
            self.ZB.SetMotor1(-self.servos[0] * self.maxPower)
            self.ZB.SetMotor2(-self.servos[1] * self.maxPower)
            self.ZB.SetMotor3(-self.servos[2] * self.maxPower)
            self.ZB.SetMotor4(-self.servos[3] * self.maxPower)

    def get_input(self):
        key = any_key()
        if key != []:
            key = key[0].decode("utf-8")
            if "q" in key:
                self.running = False
            else:
                if "w" in key:
                    self.active_commands["forward"] = self.current_time + 1
                elif "a" in key:
                    self.active_commands["left"] = self.current_time + 1
                elif "s" in key:
                    self.active_commands["backward"] = self.current_time + 1
                elif "d" in key:
                    self.active_commands["right"] = self.current_time + 1
                elif "i" in key:
                    self.active_commands["forward"] = self.current_time + 0.01
                elif "j" in key:
                    self.active_commands["left"] = self.current_time + 0.01
                elif "k" in key:
                    self.active_commands["backward"] = self.current_time + 0.01
                elif "l" in key:
                    self.active_commands["right"] = self.current_time + 0.01

init_any_key()
ZBC = ZBController()
ZBC.main()