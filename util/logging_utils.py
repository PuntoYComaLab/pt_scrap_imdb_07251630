import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

def log_info(message):
    """Función reutilizable para logging de información"""
    logging.info(message)

def log_error(message):
    """Función reutilizable para logging de errores"""
    logging.error(message)

def log_warning(message):
    """Función reutilizable para logging de advertencias"""
    logging.warning(message) 