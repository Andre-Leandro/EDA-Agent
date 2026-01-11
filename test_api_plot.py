"""
Script de prueba para verificar que la API devuelve plot_url correctamente.
"""

import requests
import json

# URL de la API
API_URL = "http://localhost:8000"

def test_api_plot_url():
    print("=" * 80)
    print("PRUEBA: Verificación de plot_url en respuesta de la API")
    print("=" * 80)
    print()
    
    # Pregunta que debería generar un gráfico
    question = "Create a simple histogram of passenger ages"
    
    print(f"📤 Enviando pregunta: '{question}'")
    print()
    
    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Respuesta recibida exitosamente")
            print()
            print("📊 Datos de la respuesta:")
            print(json.dumps(data, indent=2))
            print()
            
            # Verificar que plot_url esté presente
            if data.get('plot_url'):
                print(f"✅ plot_url encontrado: {data['plot_url']}")
                print()
                
                # Intentar acceder a la imagen
                image_url = f"{API_URL}{data['plot_url']}"
                print(f"🖼️  Verificando acceso a la imagen: {image_url}")
                
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    print(f"✅ Imagen accesible (Tamaño: {len(img_response.content)} bytes)")
                    print()
                    print("🎉 ¡TODO FUNCIONA CORRECTAMENTE!")
                else:
                    print(f"❌ Error al acceder a la imagen: {img_response.status_code}")
            else:
                print("⚠️  plot_url NO está en la respuesta")
                print()
                print("Posibles causas:")
                print("  1. El agente no generó un gráfico")
                print("  2. El regex no encontró la URL en la respuesta")
                print("  3. El formato de respuesta del agente cambió")
        else:
            print(f"❌ Error en la API: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar a la API")
        print()
        print("Asegúrate de que el servidor esté corriendo:")
        print("  $ python api.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    test_api_plot_url()
