import psutil


def getMemStatus():
    """
    Retourne un dict avec les infos mémoire du système.
    """
    mem = psutil.virtual_memory()
    return {
        'total': mem.total,  # total RAM en octets
        'available': mem.available,  # mémoire dispo pour apps
        'used': mem.used,  # mémoire utilisée
        'free': mem.free,  # mémoire libre pure
        'percent': mem.percent,  # utilisation en %
        'active': getattr(mem, 'active', None),  # Linux: mémoire active
        'inactive': getattr(mem, 'inactive', None),  # Linux: inactive
        'buffers': getattr(mem, 'buffers', None),  # Linux: buffers
        'cached': getattr(mem, 'cached', None),  # Linux: cache
        'shared': getattr(mem, 'shared', None),  # Linux: shared mem
        'slab': getattr(mem, 'slab', None),  # Linux: slab cache
    }
