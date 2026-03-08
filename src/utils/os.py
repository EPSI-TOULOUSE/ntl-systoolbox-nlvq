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
