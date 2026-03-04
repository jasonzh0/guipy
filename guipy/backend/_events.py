# Event type constants
QUIT = 0x100
MOUSEBUTTONDOWN = 0x401
MOUSEBUTTONUP = 0x402
KEYDOWN = 0x300
MOUSEMOTION = 0x404


# Key constants
K_RETURN = 0x0D
K_BACKSPACE = 0x08


class Event:
    """Simple event dataclass for input and window events."""

    def __init__(self, event_type, **kwargs):
        self.type = event_type
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        attrs = {k: v for k, v in self.__dict__.items() if k != "type"}
        return f"Event(type={self.type}, {attrs})"
