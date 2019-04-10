import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class InterruptException(Exception):
    pass

class TerminalApp():
    '''Base class for a terminal game
    provides send and read mechanims'''

    terminal_width = 80

    @classmethod
    def _name(cls):

        return cls.appname if hasattr(cls, 'appname') else "Unnamed application"

    def __init__(self, serial):
        self.serial = serial

    def send(self, text, trailing_newline=True):
        if trailing_newline and (text == '' or text[-1] != '\n'):
            text += '\n'
        data = text.replace('\n', '\r\n').encode('ascii', 'replace')

        self.serial.write(data)

    def print_broken_keys(self):
        '''prints a little helptext for broken keys'''
        if self.serial.brokenkeys == {}:
            # no broken keys
            return
        self.send("This terminal has broken keys: ")
        text = ''
        for i,k in self.serial.brokenkeys.items():
            if k == " ":
                text += "Press '{}' for SPACE, ".format(i)
            else:
                text += "Press '{}' for '{}', ".format(i, k)
        self.send(text)


    def read_line(self):
        return self.serial.readline().decode('ascii')[0:-1]

    def prompt(self, text=""):
        '''Sends a question waits for a response

        game.promt("What is your name? ")
        user then presses types a response and return key
        and this function returns that response
        '''
        self.send(text, trailing_newline=False)
        response = self.read_line().lower()
        return response

    def read_char(self):
        '''Reads a single character, echoing back to the serial port
        and translating to sring.

        We expect the serial port to be in half duplex so its our
        responsibility to echo'''
        read_char = self.serial.read(1).decode('ascii')
        return read_char

    def read_key(self, text=""):
        '''Reads a single charater response, without
        wiating for a newline'''
        self.send(text, trailing_newline=False)
        response = self.read_char().lower()
        return response

    def start(self):
        raise NotImplemented("Application doesn't have start method")

    def sleep(self, seconds):
        t1 = datetime.now()
        self.serial.timeout = seconds
        value = self.serial.read()
        self.serial.timeout = None
        t2 = datetime.now()
        elapsed  = (t2 - t1).total_seconds()

        if value == b'\0':
            raise InterruptException
        else:
            if seconds - elapsed <= 0:
                return
            self.sleep(seconds - elapsed)

