import platform
import socket
import time

import distro
import psutil


def getOSStatus():
    """
    Retourne un dict avec les infos système.
    """
    boot_time = psutil.boot_time()

    system_info = {
        'hostname': socket.gethostname(),
        'os': platform.system(),
        'os_version': platform.version(),
        'platform': platform.platform(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'cpu_cores': psutil.cpu_count(logical=True),
        'physical_cores': psutil.cpu_count(logical=False),
        'uptime_seconds': int(time.time() - boot_time),
        'uptime_human': time.strftime('%H:%M:%S', time.gmtime(time.time() - boot_time)),
        'linux_distribution': None,  # default
    }

    # check Linux et distro dispo
    if system_info['os'] == 'Linux' and distro:
        system_info['linux_distribution'] = distro.info()

    return system_info


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


def getCPUStatus():
    """
    Retourne un dict avec l'utilisation CPU.
    """
    return {
        'percent_total': psutil.cpu_percent(interval=1),  # % CPU total
        'percent_per_core': psutil.cpu_percent(interval=1, percpu=True),  # % par core
        'cores_count': psutil.cpu_count(logical=True),  # total cores logiques
        'physical_cores': psutil.cpu_count(logical=False),  # cores physiques
    }
