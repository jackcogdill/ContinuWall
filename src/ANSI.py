# Compatibility for both Python 2 and 3
# =======================================
from __future__ import absolute_import, print_function
__metaclass__ = type
try:
    input = raw_input
except NameError:
    pass
# =======================================

ESC = 27
RESET = '%c[0m' % ESC

ANSI_CSI_N   = lambda n, c: '%c[%d%c' % (ESC, n, c)
ANSI_CSI_N_M = lambda n, m, c: '%c[%d;%d%c' % (ESC, n, m, c)

def move_up(n):       print(ANSI_CSI_N(n, 'A'))
def move_down(n):     print(ANSI_CSI_N(n, 'B'))
def move_forward(n):  print(ANSI_CSI_N(n, 'C'))
def move_backward(n): print(ANSI_CSI_N(n, 'D'))

def move_column(n):   print(ANSI_CSI_N(n, 'G'), end='')


COLORS = {
    'black':   '0',
    'red':     '1',
    'green':   '2',
    'yellow':  '3',
    'blue':    '4',
    'magenta': '5',
    'cyan':    '6',
    'white':   '7',
    'reset':   RESET
}

def clear(num_lines=None):
    # Clear whole screen
    if num_lines is None:
        print('%c[2J' % ESC)

    # Specified number of lines to clear
    else:
        move_up(num_lines)
        print('%c[0J' % ESC)
        move_up(2)

def color(string, color_name=None, background=None, bold=False):
    # Only return the color (no reset) or reset itself
    if color_name is None and background is None:
        return (
            RESET if string == 'reset'
            else '%c[3%cm' % (ESC, COLORS.get(string))
        )

    # Sandwich the string in between the color and reset
    else:
        prefix = RESET

        if string != 'reset':
            fg_color = (
                ('3%c' % COLORS.get(color_name))
                if color_name is not None
                else '0'
            )
            bg_color = (
                ('4%c' % COLORS.get(background))
                if background is not None
                else ''
            )

            prefix = '%c[%s;%sm' % (ESC, fg_color, bg_color)

            if bold:
                prefix += '%c[1m' % ESC

        return '%s%s%s' % (
            prefix,
            string,
            RESET
        )
