import numpy as np
import glfw
import moderngl
from guipy.backend._events import (
    Event, QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, MOUSEMOTION, K_RETURN, K_BACKSPACE,
)
from guipy.backend._shaders import VERTEX_SHADER, FRAGMENT_SHADER


# Map GLFW keys to our key constants
_KEY_MAP = {
    glfw.KEY_ENTER: K_RETURN,
    glfw.KEY_KP_ENTER: K_RETURN,
    glfw.KEY_BACKSPACE: K_BACKSPACE,
}


class Window:
    """Window class using glfw + moderngl for display."""

    def __init__(self, width, height, title="guipy"):
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")

        # Request OpenGL 3.3 core
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

        self._window = glfw.create_window(width, height, title, None, None)
        if not self._window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")

        glfw.make_context_current(self._window)

        self._ctx = moderngl.create_context()
        self._width = width
        self._height = height

        # Fullscreen quad
        vertices = np.array([
            # x, y, u, v
            -1.0, -1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 0.0,
            -1.0,  1.0, 0.0, 1.0,
             1.0,  1.0, 1.0, 1.0,
        ], dtype='f4')

        self._prog = self._ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=FRAGMENT_SHADER,
        )

        vbo = self._ctx.buffer(vertices)
        self._vao = self._ctx.vertex_array(
            self._prog,
            [(vbo, '2f 2f', 'in_position', 'in_texcoord')],
        )

        self._texture = self._ctx.texture((width, height), 4)
        self._texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self._event_queue = []
        self._close_requested = False

        # Set up GLFW callbacks
        glfw.set_window_close_callback(self._window, self._on_close)
        glfw.set_mouse_button_callback(self._window, self._on_mouse_button)
        glfw.set_key_callback(self._window, self._on_key)
        glfw.set_char_callback(self._window, self._on_char)

        # Track pending char for combining with KEYDOWN
        self._pending_unicode = None

    def _on_close(self, window):
        self._close_requested = True
        self._event_queue.append(Event(QUIT))

    def _on_mouse_button(self, window, button, action, mods):
        if action == glfw.PRESS:
            self._event_queue.append(Event(MOUSEBUTTONDOWN, button=button))
        elif action == glfw.RELEASE:
            self._event_queue.append(Event(MOUSEBUTTONUP, button=button))

    def _on_key(self, window, key, scancode, action, mods):
        if action == glfw.PRESS or action == glfw.REPEAT:
            mapped_key = _KEY_MAP.get(key, key)
            # For return/backspace, fire immediately with empty unicode
            if key in _KEY_MAP:
                self._event_queue.append(Event(KEYDOWN, key=mapped_key, unicode=""))
            else:
                # Wait for char callback to provide unicode
                self._pending_unicode = mapped_key

    def _on_char(self, window, codepoint):
        char = chr(codepoint)
        key = self._pending_unicode if self._pending_unicode is not None else codepoint
        self._event_queue.append(Event(KEYDOWN, key=key, unicode=char))
        self._pending_unicode = None

    def get_events(self):
        """Poll for events and return the event list."""
        glfw.poll_events()
        events = self._event_queue[:]
        self._event_queue.clear()
        return events

    def get_mouse_pos(self):
        """Get current mouse position."""
        x, y = glfw.get_cursor_pos(self._window)
        return (int(x), int(y))

    def display(self, surface):
        """Upload a Surface to the GPU and render it."""
        pixels = surface._pixels
        # Flip vertically for OpenGL (origin at bottom-left)
        flipped = np.flipud(pixels).copy()

        h, w = flipped.shape[:2]
        if w != self._texture.width or h != self._texture.height:
            self._texture.release()
            self._texture = self._ctx.texture((w, h), 4)
            self._texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self._texture.write(flipped.tobytes())
        self._texture.use(0)

        self._ctx.clear()
        self._vao.render(moderngl.TRIANGLE_STRIP)
        glfw.swap_buffers(self._window)

    def should_close(self):
        return self._close_requested or glfw.window_should_close(self._window)

    def destroy(self):
        """Clean up resources."""
        self._texture.release()
        self._vao.release()
        self._prog.release()
        self._ctx.release()
        glfw.destroy_window(self._window)
        glfw.terminate()
