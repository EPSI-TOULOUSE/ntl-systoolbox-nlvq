import psutil


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
