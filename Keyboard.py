import pygame
import sys
import numpy as np
import random
import win32api
import win32con
import win32gui
import colorsys
import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Set up the display
width, height = 1000, 500
screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
pygame.display.set_caption("Pixel Keyboard Visualizer")

# Create layered window
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*(255, 0, 128)), 0, win32con.LWA_COLORKEY)

# Define colors
TRANSPARENT = (255, 0, 128)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
PURPLE_BUTTON = (128, 0, 128)
DARK_GRAY = (50, 50, 50)
BLACK = (0, 0, 0)

# Define button radius
button_radius = 20

# Update button positions
resize_button_center = (width - 30, height - 30)
exit_button_center = (width - 30, 30)
volume_button_center = (width - 130, height - 30)

# Update RGB Slider Position (shortened)
rgb_slider_rect = pygame.Rect(30, height - 70, 150, 10)  # Shortened width

# Add animation state to resize, exit, and volume buttons
resize_button = {'center': resize_button_center, 'radius': button_radius, 'pressed': False, 'animation_progress': 0}
exit_button = {'center': exit_button_center, 'radius': button_radius, 'pressed': False, 'animation_progress': 0}
volume_button = {'center': volume_button_center, 'radius': button_radius, 'pressed': False, 'animation_progress': 0}
show_slider = False

# Define volume-related variables
volume_slider_rect = pygame.Rect(volume_button_center[0] - 100, volume_button_center[1] + 20, 200, 10)
volume_knob_radius = 12  # Increased knob radius
volume_value = 1.0  # Initial volume value
dragging_slider = False

# RGB state
rgb_enabled = False
rgb_animation_progress = 0
rgb_hue = 0

# Define colors for RGB
rgb_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (143, 0, 255)]  # Rainbow colors
rgb_index = 0

# Slow down RGB cycle even more
RGB_CYCLE_STEP = 0.005  # Decreased from 0.0005 to 0.0002

# Define the range of frequencies for key press sounds
frequency_range = {
    'low_low': (200, 250),
    'low_mid': (250, 300),
    'low_high': (300, 350),
    'mid_low': (350, 400),
    'mid': (400, 450),
    'mid_high': (450, 500),
    'high_low': (500, 550),
    'high_mid': (550, 600),
    'high': (600, 650)
}

def generate_key_sound(frequency=440, duration=0.05, volume=0.1):
    sample_rate = 44100
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    wave = np.sin(2 * np.pi * frequency * t) * volume
    stereo_wave = np.vstack((wave, wave)).T
    stereo_wave = np.int16(stereo_wave * 32767)
    return pygame.sndarray.make_sound(stereo_wave.copy())

# Generate a wider range of key sounds
key_sounds = {
    'low_low': generate_key_sound(frequency=random.randint(*frequency_range['low_low'])),
    'low_mid': generate_key_sound(frequency=random.randint(*frequency_range['low_mid'])),
    'low_high': generate_key_sound(frequency=random.randint(*frequency_range['low_high'])),
    'mid_low': generate_key_sound(frequency=random.randint(*frequency_range['mid_low'])),
    'mid': generate_key_sound(frequency=random.randint(*frequency_range['mid'])),
    'mid_high': generate_key_sound(frequency=random.randint(*frequency_range['mid_high'])),
    'high_low': generate_key_sound(frequency=random.randint(*frequency_range['high_low'])),
    'high_mid': generate_key_sound(frequency=random.randint(*frequency_range['high_mid'])),
    'high': generate_key_sound(frequency=random.randint(*frequency_range['high'])),
}

# Define key positions and sizes
keys = [
    *[{'rect': pygame.Rect(10 + i * 60, 10, 55, 55), 'label': f'F{i + 1}', 'code': getattr(pygame, f'K_F{i + 1}')} for i in range(12)],
    {'rect': pygame.Rect(10, 75, 55, 55), 'label': '`', 'code': pygame.K_BACKQUOTE},
    *[{'rect': pygame.Rect(10 + (i + 1) * 60, 75, 55, 55), 'label': str(i), 'code': getattr(pygame, f'K_{i}')} for i in range(1, 10)],
    {'rect': pygame.Rect(10 + 10 * 60, 75, 55, 55), 'label': '0', 'code': pygame.K_0},
    {'rect': pygame.Rect(10 + 11 * 60, 75, 55, 55), 'label': '-', 'code': pygame.K_MINUS},
    {'rect': pygame.Rect(10 + 12 * 60, 75, 55, 55), 'label': '=', 'code': pygame.K_EQUALS},
    {'rect': pygame.Rect(10 + 13 * 60, 75, 115, 55), 'label': 'Backspace', 'code': pygame.K_BACKSPACE},
    {'rect': pygame.Rect(10, 140, 85, 55), 'label': 'Tab', 'code': pygame.K_TAB},
    *[{'rect': pygame.Rect(100 + i * 60, 140, 55, 55), 'label': letter, 'code': getattr(pygame, f'K_{letter.lower()}')} for i, letter in enumerate("QWERTYUIOP")],
    {'rect': pygame.Rect(100 + 10 * 60, 140, 55, 55), 'label': '[', 'code': pygame.K_LEFTBRACKET},
    {'rect': pygame.Rect(100 + 11 * 60, 140, 55, 55), 'label': ']', 'code': pygame.K_RIGHTBRACKET},
    {'rect': pygame.Rect(100 + 12 * 60, 140, 85, 55), 'label': '\\', 'code': pygame.K_BACKSLASH},
    {'rect': pygame.Rect(10, 205, 100, 55), 'label': 'Caps', 'code': pygame.K_CAPSLOCK},
    *[{'rect': pygame.Rect(115 + i * 60, 205, 55, 55), 'label': letter, 'code': getattr(pygame, f'K_{letter.lower()}')} for i, letter in enumerate("ASDFGHJKL")],
    {'rect': pygame.Rect(115 + 9 * 60, 205, 55, 55), 'label': ';', 'code': pygame.K_SEMICOLON},
    {'rect': pygame.Rect(115 + 10 * 60, 205, 55, 55), 'label': "'", 'code': pygame.K_QUOTE},
    {'rect': pygame.Rect(115 + 11 * 60, 205, 100, 55), 'label': 'Enter', 'code': pygame.K_RETURN},
    {'rect': pygame.Rect(10, 270, 130, 55), 'label': 'Shift', 'code': pygame.K_LSHIFT},
    *[{'rect': pygame.Rect(145 + i * 60, 270, 55, 55), 'label': letter, 'code': getattr(pygame, f'K_{letter.lower()}')} for i, letter in enumerate("ZXCVBNM")],
    {'rect': pygame.Rect(145 + 7 * 60, 270, 55, 55), 'label': ',', 'code': pygame.K_COMMA},
    {'rect': pygame.Rect(145 + 8 * 60, 270, 55, 55), 'label': '.', 'code': pygame.K_PERIOD},
    {'rect': pygame.Rect(145 + 9 * 60, 270, 55, 55), 'label': '/', 'code': pygame.K_SLASH},
    {'rect': pygame.Rect(145 + 10 * 60, 270, 130, 55), 'label': 'Shift', 'code': pygame.K_RSHIFT},
    {'rect': pygame.Rect(10, 335, 70, 55), 'label': 'Ctrl', 'code': pygame.K_LCTRL},
    {'rect': pygame.Rect(85, 335, 70, 55), 'label': 'Win', 'code': pygame.K_LMETA},
    {'rect': pygame.Rect(160, 335, 70, 55), 'label': 'Alt', 'code': pygame.K_LALT},
    {'rect': pygame.Rect(235, 335, 350, 55), 'label': 'Space', 'code': pygame.K_SPACE},
    {'rect': pygame.Rect(590, 335, 70, 55), 'label': 'Alt', 'code': pygame.K_RALT},
    {'rect': pygame.Rect(665, 335, 70, 55), 'label': 'Win', 'code': pygame.K_RMETA},
    {'rect': pygame.Rect(740, 335, 70, 55), 'label': 'Menu', 'code': pygame.K_MENU},
    {'rect': pygame.Rect(815, 335, 70, 55), 'label': 'Ctrl', 'code': pygame.K_RCTRL},
]

# Add animation state to each key
for key in keys:
    key['pressed'] = False
    key['animation_progress'] = 0
    key['sound'] = random.choice(list(key_sounds.values()))
    key['sound_playing'] = False
    key['original_rect'] = key['rect'].copy()

# Font for rendering text
font = pygame.font.Font(None, 24)

def draw_pixelated_key(surface, rect, color, border_color, pressed, animation_progress, border_width=2, pixel_size=5):
    offset = int(3 * animation_progress)
    animated_rect = rect.move(0, offset)

    # Draw the key body
    for x in range(animated_rect.left, animated_rect.right, pixel_size):
        for y in range(animated_rect.top, animated_rect.bottom, pixel_size):
            pygame.draw.rect(surface, color, (x, y, pixel_size, pixel_size))

    # Draw the border
    for i in range(border_width):
        border_rect = animated_rect.inflate(i * 2, i * 2)
        pygame.draw.rect(surface, border_color, border_rect, 1)

    # Draw the shadow
    shadow_rect = pygame.Rect(animated_rect.left, animated_rect.bottom, animated_rect.width, 3)
    shadow_color = (0, 0, 0, 80)
    for x in range(shadow_rect.left, shadow_rect.right, pixel_size):
        for y in range(shadow_rect.top, shadow_rect.bottom, pixel_size):
            pygame.draw.rect(surface, shadow_color, (x, y, pixel_size, pixel_size))

    # Draw the label
    label_surface = font.render(key['label'], True, BLACK if color == WHITE else WHITE)
    label_rect = label_surface.get_rect(center=animated_rect.center)
    surface.blit(label_surface, label_rect.topleft)

def draw_volume_slider(surface):
    # Draw the slider background
    pygame.draw.rect(surface, DARK_GRAY, volume_slider_rect, border_radius=5)
    # Draw the filled part based on the volume value
    filled_rect = pygame.Rect(volume_slider_rect.x, volume_slider_rect.y, volume_value * volume_slider_rect.width,
                              volume_slider_rect.height)
    pygame.draw.rect(surface, WHITE, filled_rect, border_radius=5)
    # Draw the knob
    knob_x = volume_slider_rect.x + (volume_value * volume_slider_rect.width) - volume_knob_radius
    pygame.draw.circle(surface, BLACK, (int(knob_x), volume_slider_rect.centery), volume_knob_radius)

def draw_perfectly_round_button(surface, center, radius, color, outline_color, pressed, animation_progress):
    offset = int(3 * animation_progress)
    animated_center = (center[0], center[1] + offset)

    shadow_center = (animated_center[0], animated_center[1] + radius // 2)
    shadow_color = (0, 0, 0, 80)
    pygame.draw.circle(surface, shadow_color, shadow_center, radius)

    pygame.draw.circle(surface, color, animated_center, radius)
    pygame.draw.circle(surface, outline_color, animated_center, radius, 2)

def draw_buttons(surface):
    draw_perfectly_round_button(surface, resize_button['center'], resize_button['radius'], (0, 120, 255), GRAY,
                                resize_button['pressed'], resize_button['animation_progress'])
    draw_perfectly_round_button(surface, exit_button['center'], exit_button['radius'], (255, 60, 60), GRAY,
                                exit_button['pressed'], exit_button['animation_progress'])
    draw_perfectly_round_button(surface, volume_button['center'], volume_button['radius'], PURPLE_BUTTON, GRAY,
                                volume_button['pressed'], volume_button['animation_progress'])

    volume_icon = font.render("🔊", True, WHITE)  # Sound icon
    surface.blit(volume_icon, (volume_button['center'][0] - 10, volume_button['center'][1] - 10))

def hsv_to_rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

def draw_rgb_glow(surface, rect, hue, intensity):
    glow_color = hsv_to_rgb(hue, 1, 1)
    glow_surface = pygame.Surface(rect.inflate(10, 10).size, pygame.SRCALPHA)
    pygame.draw.rect(glow_surface, (*glow_color, int(255 * intensity)), glow_surface.get_rect(), border_radius=8)
    surface.blit(glow_surface, rect.inflate(10, 10).topleft)

def draw_rgb_slider(surface, rect, enabled, animation_progress, hue):
    # Draw the slider background
    pygame.draw.rect(surface, DARK_GRAY, rect, border_radius=10)

    # Draw the filled part based on the enabled state
    filled_rect = pygame.Rect(rect.x, rect.y, rect.width * animation_progress, rect.height)
    fill_color = hsv_to_rgb(hue, 1, 1)
    pygame.draw.rect(surface, fill_color, filled_rect, border_radius=10)

    # Draw the knob with increased size
    knob_x = rect.x + (rect.width * animation_progress if enabled else 0)
    pygame.draw.circle(surface, WHITE, (int(knob_x), rect.centery), 12)  # Increased knob radius

    # Draw label above the slider
    label_surface = font.render("RGB", True, WHITE)
    label_rect = label_surface.get_rect(center=(rect.centerx, rect.top - 20))
    surface.blit(label_surface, label_rect.topleft)

# Update the window size
def update_window_size(new_width, new_height):
    global width, height, screen, resize_button, exit_button, volume_button, volume_slider_rect, rgb_slider_rect

    width, height = new_width, new_height
    screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
    resize_button['center'] = (width - 30, height - 30)
    exit_button['center'] = (width - 30, 30)
    volume_button['center'] = (width - 130, height - 30)

    volume_slider_rect.x = volume_button['center'][0] - 100
    volume_slider_rect.y = volume_button['center'][1] + 20  # Adjust to follow the button

    # Keep the RGB slider position fixed at the bottom left, but ensure it doesn't overlap with the keyboard
    rgb_slider_rect.x = 30
    rgb_slider_rect.y = min(height - 70, keys[-1]['rect'].bottom + 20)  # Ensure it's below the keyboard

    # Scale key positions if needed
    scale_x = width / 1000
    scale_y = height / 500
    for key in keys:
        original_rect = key['original_rect']
        key['rect'] = pygame.Rect(
            int(original_rect.x * scale_x),
            int(original_rect.y * scale_y),
            int(original_rect.width * scale_x),
            int(original_rect.height * scale_y)
        )

    # Ensure the window stays on top
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, width, height,
                          win32con.SWP_NOMOVE | win32con.SWP_NOACTIVATE)

# Set up the key states
for key in keys:
    key['pressed'] = False
    key['animation_progress'] = 0
    key['sound'] = random.choice(list(key_sounds.values()))
    key['original_rect'] = key['rect'].copy()

# Define the structure for keyboard hooks
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", ctypes.wintypes.DWORD),
        ("scanCode", ctypes.wintypes.DWORD),
        ("flags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.wintypes.ULONG))
    ]

# Create a mapping between Windows virtual key codes and Pygame key codes
vk_to_pygame = {
    0x08: pygame.K_BACKSPACE,
    0x09: pygame.K_TAB,
    0x0D: pygame.K_RETURN,
    0x13: pygame.K_PAUSE,
    0x14: pygame.K_CAPSLOCK,
    0x1B: pygame.K_ESCAPE,
    0x20: pygame.K_SPACE,
    0x21: pygame.K_PAGEUP,
    0x22: pygame.K_PAGEDOWN,
    0x23: pygame.K_END,
    0x24: pygame.K_HOME,
    0x25: pygame.K_LEFT,
    0x26: pygame.K_UP,
    0x27: pygame.K_RIGHT,
    0x28: pygame.K_DOWN,
    0x2C: pygame.K_PRINT,
    0x2D: pygame.K_INSERT,
    0x2E: pygame.K_DELETE,
    0x30: pygame.K_0,
    0x31: pygame.K_1,
    0x32: pygame.K_2,
    0x33: pygame.K_3,
    0x34: pygame.K_4,
    0x35: pygame.K_5,
    0x36: pygame.K_6,
    0x37: pygame.K_7,
    0x38: pygame.K_8,
    0x39: pygame.K_9,
    0x41: pygame.K_a,
    0x42: pygame.K_b,
    0x43: pygame.K_c,
    0x44: pygame.K_d,
    0x45: pygame.K_e,
    0x46: pygame.K_f,
    0x47: pygame.K_g,
    0x48: pygame.K_h,
    0x49: pygame.K_i,
    0x4A: pygame.K_j,
    0x4B: pygame.K_k,
    0x4C: pygame.K_l,
    0x4D: pygame.K_m,
    0x4E: pygame.K_n,
    0x4F: pygame.K_o,
    0x50: pygame.K_p,
    0x51: pygame.K_q,
    0x52: pygame.K_r,
    0x53: pygame.K_s,
    0x54: pygame.K_t,
    0x55: pygame.K_u,
    0x56: pygame.K_v,
    0x57: pygame.K_w,
    0x58: pygame.K_x,
    0x59: pygame.K_y,
    0x5A: pygame.K_z,
    0x5B: pygame.K_LMETA,
    0x5C: pygame.K_RMETA,
    0x60: pygame.K_KP0,
    0x61: pygame.K_KP1,
    0x62: pygame.K_KP2,
    0x63: pygame.K_KP3,
    0x64: pygame.K_KP4,
    0x65: pygame.K_KP5,
    0x66: pygame.K_KP6,
    0x67: pygame.K_KP7,
    0x68: pygame.K_KP8,
    0x69: pygame.K_KP9,
    0x6A: pygame.K_KP_MULTIPLY,
    0x6B: pygame.K_KP_PLUS,
    0x6D: pygame.K_KP_MINUS,
    0x6E: pygame.K_KP_PERIOD,
    0x6F: pygame.K_KP_DIVIDE,
    0x70: pygame.K_F1,
    0x71: pygame.K_F2,
    0x72: pygame.K_F3,
    0x73: pygame.K_F4,
    0x74: pygame.K_F5,
    0x75: pygame.K_F6,
    0x76: pygame.K_F7,
    0x77: pygame.K_F8,
    0x78: pygame.K_F9,
    0x79: pygame.K_F10,
    0x7A: pygame.K_F11,
    0x7B: pygame.K_F12,
    0x90: pygame.K_NUMLOCK,
    0x91: pygame.K_SCROLLOCK,
    0xA0: pygame.K_LSHIFT,
    0xA1: pygame.K_RSHIFT,
    0xA2: pygame.K_LCTRL,
    0xA3: pygame.K_RCTRL,
    0xA4: pygame.K_LALT,
    0xA5: pygame.K_RALT,
}

# Define the hook callback
CMPFUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(KBDLLHOOKSTRUCT))

def hook_callback(nCode, wParam, lParam):
    if nCode >= 0:
        kb = lParam.contents
        pygame_key = vk_to_pygame.get(kb.vkCode)
        if pygame_key:
            if wParam == win32con.WM_KEYDOWN:
                for key in keys:
                    if pygame_key == key['code']:
                        key['pressed'] = True
                        key['sound'].set_volume(volume_value)  # Set sound volume based on the slider
                        if not key['sound_playing']:
                            key['sound'].play()
                            key['sound_playing'] = True
            elif wParam == win32con.WM_KEYUP:
                for key in keys:
                    if pygame_key == key['code']:
                        key['pressed'] = False
                        key['sound_playing'] = False
    return user32.CallNextHookEx(None, nCode, wParam, lParam)

# Set up the keyboard hook
hook_callback_func = CMPFUNC(hook_callback)
hook = user32.SetWindowsHookExA(win32con.WH_KEYBOARD_LL, hook_callback_func, None, 0)

if not hook:
    print("Failed to set hook")
    sys.exit(1)

# Main game loop
clock = pygame.time.Clock()
running = True
dragging_slider = False
is_dragging = False
drag_start_pos = (0, 0)

# Animation progress initialization
rgb_enabled = False
rgb_animation_progress = 0
rgb_cycle_progress = 0

# Resizing state variable
resizing = False

# Main game loop
while running:
    # Update RGB cycle progress with slower speed
    rgb_hue = (rgb_hue + RGB_CYCLE_STEP) % 1

    # Update RGB animation progress
    if rgb_enabled:
        rgb_animation_progress = min(1, rgb_animation_progress + 0.05)
    else:
        rgb_animation_progress = max(0, rgb_animation_progress - 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Check if any button is pressed
            if (mouse_pos[0] - volume_button['center'][0]) ** 2 + (mouse_pos[1] - volume_button['center'][1]) ** 2 <= volume_button['radius'] ** 2:
                show_slider = not show_slider
                volume_button['pressed'] = True
            elif (mouse_pos[0] - resize_button['center'][0]) ** 2 + (mouse_pos[1] - resize_button['center'][1]) ** 2 <= resize_button['radius'] ** 2:
                resizing = True
                resize_button['pressed'] = True
            elif (mouse_pos[0] - exit_button['center'][0]) ** 2 + (mouse_pos[1] - exit_button['center'][1]) ** 2 <= exit_button['radius'] ** 2:
                exit_button['pressed'] = True
                running = False
            elif rgb_slider_rect.collidepoint(mouse_pos):
                rgb_enabled = not rgb_enabled
            elif volume_slider_rect.collidepoint(mouse_pos):
                dragging_slider = True
            else:
                is_dragging = True
                win32gui.ReleaseCapture()
                win32api.SendMessage(hwnd, win32con.WM_NCLBUTTONDOWN, win32con.HTCAPTION, 0)

        elif event.type == pygame.MOUSEBUTTONUP:
            resize_button['pressed'] = False
            exit_button['pressed'] = False
            volume_button['pressed'] = False
            dragging_slider = False
            resizing = False
            is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if resizing:
                new_width = max(200, event.pos[0])
                new_height = max(200, event.pos[1])
                update_window_size(new_width, new_height)
            elif dragging_slider:
                # Update volume based on mouse position on the slider
                slider_x = event.pos[0] - volume_slider_rect.x
                volume_value = min(max(slider_x / volume_slider_rect.width, 0), 1)  # Clamp volume value between 0 and 1

    screen.fill(TRANSPARENT)  # Restore transparent background

    for key in keys:
        if key['pressed']:
            key['animation_progress'] = min(1, key['animation_progress'] + 0.1)
        else:
            key['animation_progress'] = max(0, key['animation_progress'] - 0.1)

        # Draw keys with RGB glow if enabled, otherwise use the keyboard color
        if rgb_enabled:
            draw_rgb_glow(screen, key['rect'], rgb_hue, rgb_animation_progress)
        else:
            pygame.draw.rect(screen, GRAY, key['rect'].inflate(10, 10), border_radius=8)

        draw_pixelated_key(screen, key['rect'], WHITE if key['pressed'] else GRAY, WHITE, key['pressed'],
                           key['animation_progress'])

    # Draw RGB slider with smooth animation
    draw_rgb_slider(screen, rgb_slider_rect, rgb_enabled, rgb_animation_progress, rgb_hue)

    # Update button animations
    for button in [resize_button, exit_button, volume_button]:
        if button['pressed']:
            button['animation_progress'] = min(1, button['animation_progress'] + 0.1)
        else:
            button['animation_progress'] = max(0, button['animation_progress'] - 0.1)

    draw_buttons(screen)

    if show_slider:
        draw_volume_slider(screen)

    pygame.display.flip()
    clock.tick(60)  # Increased frame rate for smoother animations

    # Ensure the window stays on top
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)

    # Process Windows messages to ensure the hook works
    msg = ctypes.wintypes.MSG()
    while user32.PeekMessageA(ctypes.byref(msg), None, 0, 0, win32con.PM_REMOVE) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageA(ctypes.byref(msg))

# Clean up
user32.UnhookWindowsHookEx(hook)
pygame.quit()
sys.exit()



