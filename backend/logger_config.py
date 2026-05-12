"""
Configuration du système de logging pour l'application
Enregistre tous les logs dans des fichiers avec rotation automatique
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Créer le dossier logs s'il n'existe pas
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Nom des fichiers de log avec date
LOG_FILE = os.path.join(LOGS_DIR, f'backend_{datetime.now().strftime("%Y%m%d")}.log')
ERROR_LOG_FILE = os.path.join(LOGS_DIR, f'backend_errors_{datetime.now().strftime("%Y%m%d")}.log')

def setup_logger(name='backend'):
    """
    Configure et retourne un logger avec rotation de fichiers
    - Logs généraux: backend_YYYYMMDD.log (max 10MB, 5 fichiers)
    - Logs d'erreurs: backend_errors_YYYYMMDD.log (max 10MB, 5 fichiers)
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Éviter les doublons si déjà configuré
    if logger.handlers:
        return logger
    
    # Format détaillé des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour tous les logs (DEBUG et plus)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler pour les erreurs uniquement (ERROR et CRITICAL)
    error_handler = RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Handler pour la console (INFO et plus)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger

# Logger global pour l'application
app_logger = setup_logger('backend')

def log_request(endpoint: str, method: str, params: dict = None):
    """Log une requête API"""
    app_logger.info(f"API Request: {method} {endpoint} - Params: {params}")

def log_error(error: Exception, context: str = ""):
    """Log une erreur avec contexte"""
    app_logger.error(f"Error in {context}: {type(error).__name__}: {str(error)}", exc_info=True)

def log_tool_call(tool_name: str, params: dict, result: str = None):
    """Log un appel d'outil AI"""
    app_logger.info(f"Tool Call: {tool_name} - Params: {params}")
    if result:
        app_logger.debug(f"Tool Result: {result[:200]}...")

def log_ai_request(provider: str, prompt_length: int, response_length: int = None):
    """Log une requête AI"""
    app_logger.info(f"AI Request: Provider={provider}, Prompt Length={prompt_length}")
    if response_length:
        app_logger.info(f"AI Response: Length={response_length}")

# Log de démarrage
app_logger.info("="*60)
app_logger.info("Backend AI Arduino - Démarrage")
app_logger.info(f"Logs sauvegardés dans: {LOGS_DIR}")
app_logger.info("="*60)
