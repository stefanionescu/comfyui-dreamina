"""The names this extension uses in spaces shared with other packs."""

# Every node identifier is this prefix and the class name.
NODE_PREFIX = 'Dreamina'

# The menu headings that group the nodes.
MENUS = {
    'SHARED': 'Dreamina',
    'IMAGE': 'Dreamina/Image',
    'VIDEO': 'Dreamina/Video',
    'AUDIO': 'Dreamina/Audio',
}

# The socket types more than one node shares, prefixed so no other pack's socket of the same name connects.
SOCKET_TYPES = {
    'REFERENCES': 'DREAMINA_REFERENCES',
}

__all__ = [
    'MENUS',
    'NODE_PREFIX',
    'SOCKET_TYPES',
]
