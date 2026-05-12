"""
Script de test pour vérifier que les erreurs sont bien enregistrées dans ERRORS.txt
"""
import sys
import os

# Ajouter le backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from logger_config import app_logger, log_error

print("Test du système d'enregistrement des erreurs...")
print("=" * 60)

# Test 1: Erreur simple
try:
    raise ValueError("Test erreur simple pour ERRORS.txt")
except Exception as e:
    log_error(e, "test_erreur_simple")
    print("✓ Test 1: Erreur simple enregistrée")

# Test 2: Erreur avec contexte
try:
    result = 10 / 0
except Exception as e:
    log_error(e, "test_division_par_zero")
    print("✓ Test 2: Division par zéro enregistrée")

# Test 3: Erreur de fichier
try:
    with open("fichier_inexistant.txt", "r") as f:
        content = f.read()
except Exception as e:
    log_error(e, "test_fichier_inexistant")
    print("✓ Test 3: Erreur de fichier enregistrée")

# Test 4: Log d'erreur direct
app_logger.error("Test erreur directe sans exception")
print("✓ Test 4: Erreur directe enregistrée")

# Test 5: Log critique
app_logger.critical("Test erreur CRITIQUE")
print("✓ Test 5: Erreur critique enregistrée")

print("=" * 60)
print("\nTous les tests terminés!")
print("\nConsultez ERRORS.txt pour voir les erreurs enregistrées:")
print("  - Manuellement: type ERRORS.txt")
print("  - Avec script: view_errors.bat")
print("\nOu utilisez: view_errors.bat (option 2 pour voir les dernières)")
