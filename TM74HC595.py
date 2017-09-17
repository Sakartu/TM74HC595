from machine import Pin
import array

class TM74HC595Controller:
    _CHARS = {
    '0': 0xC0, '1': 0xF9, '2': 0xA4, '3': 0xB0, '4': 0x99, '5': 0x92, '6': 0x82,
    '7': 0xF8, '8': 0x80, '9': 0x90, 'A': 0x88, 'b': 0x83, 'C': 0xC6, 'd': 0xA1,
    'E': 0x86, 'F': 0x8E, 'G': 0xC2, 'H': 0x89, 'I': 0xF9, 'J': 0xF1, 'L': 0xC3,
    'n': 0xA9, 'O': 0xC0, 'P': 0x8C, 'q': 0x98, 'r': 0xCe, 'S': 0x92, 'U': 0xC1,
    'Y': 0x91, '‾': 0xFE, '-': 0xBF, '_': 0xF7, ' ': 0xFF
    }

    def __init__(self, sclk, rclk, dio, num_displays):
        self.sclk = Pin(sclk, Pin.OUT)
        self.rclk = Pin(rclk, Pin.OUT)
        self.dio = Pin(dio, Pin.OUT)
        self.num_displays = num_displays

    def _send_byte(self, b):
        for _ in range(8):
            if b & 0x80: # leftmost bit is 1
                # so write it
                self.dio.value(1)
            else:
                # otherwise write a 0
                self.dio.value(0)
            b <<= 1  # prepare for next bit
            # Cycle the clock as required for the TM74HC595 controller chip
            self.sclk.value(0)
            self.sclk.value(1)


    def _set_port(self, h, port):
        self._send_byte(h)
        self._send_byte(port)
        self.rclk.value(0)
        self.rclk.value(1)


    def show_sequence(self, sequence, redraw=100, clear=True):
        """
        Use this method to show a sequence of characters on the 8-segment
        display. Because the TM74HC595 controller can only control a single 
        display at a time, it sets each display very quickly, one after the
        other, so that the human eye does not see it flickering. The number of
        redraws it should do can be specified by the user, thus definig how 
        long the sequence should be displayed. The user can also choose to clear
        the display after the redraws or not.

        Be advised: not all characters are available for 8-segment displays! 
        See TM74HC595Controller._CHARS.keys() for a list of valid characters.

        :param sequence: The sequence of str-type characters to show. 
        :param redraw: The number of times this method should redraw the full 
        sequence
        :param clear: Whether this method should clear the display after all 
        redraws are done
        """
        to_display = array.array('B')
        i = 0
        while i < len(sequence):
            c = sequence[i]
            if c == '.':
                if i:  # not the first char
                    to_display[-1] &= 0b01111111  # Activate the '.'
            else:
                to_display.append(self._CHARS[c])
            i += 1

        for _ in range(redraw):
            for i, c in enumerate(to_display):
                i = self.num_displays - 1 - i
                self._set_port(c, 1<<i)

        if clear:
            for i in range(self.num_displays):  # clear display
                self._set_port(0xFF, 1<<i)
