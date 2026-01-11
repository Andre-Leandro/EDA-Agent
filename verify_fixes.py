#!/usr/bin/env python3
"""
Script de verificación rápida de los cambios implementados.
Ejecutar: python verify_fixes.py
"""

import os
import sys

def check_gitignore():
    """Verifica que plots/ esté en .gitignore"""
    try:
        with open('.gitignore', 'r') as f:
            content = f.read()
            if 'plots/' in content:
                print("✅ .gitignore - plots/ está correctamente ignorado")
                return True
            else:
                print("❌ .gitignore - plots/ NO está en .gitignore")
                return False
    except FileNotFoundError:
        print("❌ .gitignore - Archivo no encontrado")
        return False

def check_api_model():
    """Verifica que AnswerResponse tenga plot_url"""
    try:
        from api import AnswerResponse
        fields = AnswerResponse.model_fields.keys()
        if 'plot_url' in fields:
            print("✅ api.py - AnswerResponse tiene campo plot_url")
            return True
        else:
            print("❌ api.py - AnswerResponse NO tiene campo plot_url")
            return False
    except Exception as e:
        print(f"❌ api.py - Error al verificar: {e}")
        return False

def check_frontend():
    """Verifica que App.jsx tenga el código actualizado"""
    try:
        with open('frontend/src/App.jsx', 'r') as f:
            content = f.read()
            has_ploturl_state = 'plotUrl' in content and 'setPlotUrl' in content
            has_ploturl_in_history = 'item.plotUrl' in content
            
            if has_ploturl_state and has_ploturl_in_history:
                print("✅ frontend/src/App.jsx - Código actualizado correctamente")
                return True
            else:
                print("❌ frontend/src/App.jsx - Falta código de plotUrl")
                return False
    except FileNotFoundError:
        print("❌ frontend/src/App.jsx - Archivo no encontrado")
        return False

def main():
    print("=" * 70)
    print("VERIFICACIÓN DE CAMBIOS IMPLEMENTADOS")
    print("=" * 70)
    print()
    
    results = []
    
    print("Verificando cambios...")
    print()
    
    results.append(check_gitignore())
    results.append(check_api_model())
    results.append(check_frontend())
    
    print()
    print("=" * 70)
    
    if all(results):
        print("✨ ¡TODOS LOS CAMBIOS VERIFICADOS CORRECTAMENTE!")
        print()
        print("Ahora puedes:")
        print("  1. python api.py          # Iniciar backend")
        print("  2. cd frontend && npm run dev   # Iniciar frontend")
        print("  3. Abrir http://localhost:5173")
        print("  4. Probar: 'Create a histogram of ages'")
        print()
        print("Las imágenes se mostrarán automáticamente en el chat 🎨")
        return 0
    else:
        print("⚠️  Algunos cambios no se aplicaron correctamente")
        print("Revisa los errores arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())
