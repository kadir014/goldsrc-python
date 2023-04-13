"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .engine import Engine


class InputManager:
    """
    Input manager class.
    """

    def __init__(self, engine: "Engine"):
        self.engine = engine

        # Dictionaries to store input states
        #                         held pressed released
        self.__key_states = {k:   [0,  0,      0] for k in KEY_DICT}
        self.__mouse_states = {b: [0,  0,      0] for b in MOUSE_DICT}

    def update(self):
        """ Update input states. """

        # Reset pressed and released states
        for k in self.__key_states:
            self.__key_states[k][1] = 0
            self.__key_states[k][2] = 0

        for b in self.__mouse_states:
            self.__mouse_states[b][1] = 0
            self.__mouse_states[b][2] = 0

        for event in self.engine.events:
            if event.type == pygame.KEYDOWN:
                self.__key_states[KEY_INVDICT[event.key]][0] = 1
                self.__key_states[KEY_INVDICT[event.key]][1] = 1

            elif event.type == pygame.KEYUP:
                self.__key_states[KEY_INVDICT[event.key]][0] = 0
                self.__key_states[KEY_INVDICT[event.key]][1] = 0
                self.__key_states[KEY_INVDICT[event.key]][2] = 1

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.__mouse_states[MOUSE_INVDICT[event.button]][0] = 1
                self.__mouse_states[MOUSE_INVDICT[event.button]][1] = 1

            elif event.type == pygame.MOUSEBUTTONUP:
                self.__mouse_states[MOUSE_INVDICT[event.button]][0] = 0
                self.__mouse_states[MOUSE_INVDICT[event.button]][1] = 0
                self.__mouse_states[MOUSE_INVDICT[event.button]][2] = 1

    def key_pressed(self, key: str) -> bool:
        """ Check if key gets pressed. """
        return self.__key_states[key][1]

    def key_released(self, key: str) -> bool:
        """ Check if key gets released. """
        return self.__key_states[key][2]

    def key_held(self, key: str) -> bool:
        """ Check if key is held down. """
        return self.__key_states[key][0]

    def mouse_pressed(self, button: str) -> bool:
        """ Check if mouse button gets pressed. """
        return self.__mouse_states[button][1]

    def mouse_released(self, button: str) -> bool:
        """ Check if mouse button gets released. """
        return self.__mouse_states[button][2]

    def mouse_held(self, button: str) -> bool:
        """ Check if mouse button is held down. """
        return self.__mouse_states[button][0]

    def mouse_wheel_up(self) -> bool:
        """ Check if mouse wheel rotated upwards. """
        return self.__mouse_states["wheelup"][1]

    def mouse_wheel_down(self) -> bool:
        """ Check if mouse wheel is rotated downwards. """
        return self.__mouse_states["wheeldown"][1]


# String key name to Pygame key constant mapping
KEY_DICT = {
    "backspace": pygame.K_BACKSPACE,
    "tab": pygame.K_TAB ,
    "clear": pygame.K_CLEAR,
    "return": pygame.K_RETURN,
    "pause": pygame.K_PAUSE,
    "escape": pygame.K_ESCAPE,
    "space": pygame.K_SPACE,
    "exclaim": pygame.K_EXCLAIM,
    "quotedbl": pygame.K_QUOTEDBL,
    "hash": pygame.K_HASH,
    "dollar": pygame.K_DOLLAR,
    "ampersand": pygame.K_AMPERSAND,
    "quote": pygame.K_QUOTE,
    "lparen": pygame.K_LEFTPAREN,
    "rparen": pygame.K_RIGHTPAREN,
    "asterisk": pygame.K_ASTERISK,
    "plus": pygame.K_PLUS,
    "comma": pygame.K_COMMA,
    "minus": pygame.K_MINUS,
    "period": pygame.K_PERIOD,
    "slash" : pygame.K_SLASH,
    "0": pygame.K_0,
    "1": pygame.K_1,
    "2": pygame.K_2,
    "3": pygame.K_3,
    "4": pygame.K_4,
    "5": pygame.K_5,
    "6": pygame.K_6,
    "7": pygame.K_7,
    "8": pygame.K_8,
    "9": pygame.K_9,
    "colon": pygame.K_COLON,
    "semicolon": pygame.K_SEMICOLON,
    "less": pygame.K_LESS,
    "equals": pygame.K_EQUALS,
    "greater": pygame.K_GREATER,
    "question": pygame.K_QUESTION,
    "at": pygame.K_AT,
    "leftbracket": pygame.K_LEFTBRACKET,
    "backslash": pygame.K_BACKSLASH,
    "rightbracet": pygame.K_RIGHTBRACKET,
    "caret": pygame.K_CARET,
    "underscore": pygame.K_UNDERSCORE,
    "backquote": pygame.K_BACKQUOTE,
    "a": pygame.K_a,
    "b": pygame.K_b,
    "c": pygame.K_c,
    "d": pygame.K_d,
    "e": pygame.K_e,
    "f": pygame.K_f,
    "g": pygame.K_g,
    "h": pygame.K_h,
    "i": pygame.K_i,
    "j": pygame.K_j,
    "k": pygame.K_k,
    "l": pygame.K_l,
    "m": pygame.K_m,
    "n": pygame.K_n,
    "o": pygame.K_o,
    "p": pygame.K_p,
    "q": pygame.K_q,
    "r": pygame.K_r,
    "s": pygame.K_s,
    "t": pygame.K_t,
    "u": pygame.K_u,
    "v": pygame.K_v,
    "w": pygame.K_w,
    "x": pygame.K_x,
    "y": pygame.K_y,
    "z": pygame.K_z,
    "delete": pygame.K_DELETE,
    "n0": pygame.K_KP0,
    "n1": pygame.K_KP1,
    "n2": pygame.K_KP2,
    "n3": pygame.K_KP3,
    "n4": pygame.K_KP4,
    "n5": pygame.K_KP5,
    "n6": pygame.K_KP6,
    "n7": pygame.K_KP7,
    "n8": pygame.K_KP8,
    "n9": pygame.K_KP9,
    "nperiod": pygame.K_KP_PERIOD,
    "divide": pygame.K_KP_DIVIDE,
    "multiply": pygame.K_KP_MULTIPLY,
    "nminus": pygame.K_KP_MINUS,
    "nplus": pygame.K_KP_PLUS,
    "enter": pygame.K_KP_ENTER,
    "nequals": pygame.K_KP_EQUALS,
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "right": pygame.K_RIGHT,
    "left": pygame.K_LEFT,
    "insert": pygame.K_INSERT,
    "home": pygame.K_HOME,
    "end": pygame.K_END,
    "pageup": pygame.K_PAGEUP,
    "pagedown": pygame.K_PAGEDOWN,
    "f1": pygame.K_F1,
    "f2": pygame.K_F2,
    "f3": pygame.K_F3,
    "f4": pygame.K_F4,
    "f5": pygame.K_F5,
    "f6": pygame.K_F6,
    "f7": pygame.K_F7,
    "f8": pygame.K_F8,
    "f9": pygame.K_F9,
    "f10": pygame.K_F10,
    "f11": pygame.K_F11,
    "f12": pygame.K_F12,
    "f13": pygame.K_F13,
    "f14": pygame.K_F14,
    "f15": pygame.K_F15,
    "numlock": pygame.K_NUMLOCK,
    "capslock": pygame.K_CAPSLOCK,
    "scrollock": pygame.K_SCROLLOCK,
    "rshift": pygame.K_RSHIFT,
    "lshift": pygame.K_LSHIFT,
    "rctrl": pygame.K_RCTRL,
    "lctrl": pygame.K_LCTRL,
    "ralt": pygame.K_RALT,
    "lalt": pygame.K_LALT,
    "rmeta": pygame.K_RMETA, 
    "lmeta": pygame.K_LMETA,
    "lsuper": pygame.K_LSUPER,
    "rsuper": pygame.K_RSUPER,
    "altgr": pygame.K_MODE,
    "help": pygame.K_HELP,
    "print":  pygame.K_PRINT,
    "sysreq": pygame.K_SYSREQ,
    "break": pygame.K_BREAK,
    "menu": pygame.K_MENU,
    "power": pygame.K_POWER,
    "euro": pygame.K_EURO,
}

# Mouse button names to Pygame button event mapping
# TODO: Extra buttons don't work
MOUSE_DICT = {
    "left": 1,
    "right": 3,
    "middle": 2,
    "wheelup": 4,
    "wheeldown": 5,
    # for mouses with extra buttons on it
    "extra1": 6,
    "extra2": 7,
    "extra3": 8,
    "extra4": 9,
    "extra5": 10,
    "extra6": 11
}

# Inverted mappings used by input manager
KEY_INVDICT = {v: k for k, v in KEY_DICT.items()}
MOUSE_INVDICT = {v: k for k, v in MOUSE_DICT.items()}