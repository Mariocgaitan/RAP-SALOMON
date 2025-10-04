from pytesseract import pytesseract
from PIL import Image
import os
import concurrent.futures
from multiprocessing import Pool, cpu_count
import re
import shutil
from tqdm import tqdm  # Importar tqdm para la barra de progreso

# Especificar la ruta completa al ejecutable de Tesseract (en caso de que no se haya agregado al PATH)
pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Asegúrate de que esta ruta sea correcta

carpeta_principal = r"C:\Users\mario\OneDrive\Documentos\Imagenes\Prueba textos - Copy"  # Cambia esto por tu ruta
# Directorio donde se guardarán las imágenes filtradas
carpeta_constancias = os.path.join(carpeta_principal, "De control", "Constancias")

# Crear la carpeta para las constancias si no existe
if not os.path.exists(carpeta_constancias):
    os.makedirs(carpeta_constancias)

archivo_errores = os.path.join(carpeta_principal, "errores.txt")
archivo_detalles = os.path.join(carpeta_principal, "detalles_con_control.txt")
archivo_movimientos = os.path.join(carpeta_principal, "errores_movimientos.txt")

def procesar_imagen(ruta_imagen):
    try:
        # Extraer texto de la imagen
        texto = pytesseract.image_to_string(Image.open(ruta_imagen), lang='spa')  # Cambia 'spa' si el idioma es otro
        
        nombre_archivo = os.path.splitext(os.path.basename(ruta_imagen))[0] + ".txt"
        ruta_archivo = os.path.join(os.path.dirname(ruta_imagen), nombre_archivo)
        
        with open(ruta_archivo, "w", encoding="utf-8") as file:
            file.write(texto)
        
        if "DE CONTROL" in texto.upper():
            try:
                # Mover la imagen a la carpeta de constancias
                nueva_ruta_imagen = os.path.join(carpeta_constancias, os.path.basename(ruta_imagen))
                shutil.move(ruta_imagen, nueva_ruta_imagen)
                
                # Registrar la información en el archivo de detalles
                with open(archivo_detalles, "a", encoding="utf-8") as detalles_file:
                    detalles_file.write(f"Imagen: {ruta_imagen}\n")
                    detalles_file.write(f"  Contiene 'DE CONTROL'. Movida a: {nueva_ruta_imagen}\n\n")
            except Exception as mover_error:
                # Registrar errores de movimiento en el archivo de errores
                with open(archivo_movimientos, "a", encoding="utf-8") as error_file:
                    error_file.write(f"Error moviendo {ruta_imagen}: {mover_error}\n")

    except Exception as e:
        with open(archivo_errores, "a", encoding="utf-8") as error_file:
            error_file.write(f"Error procesando {ruta_imagen}: {e}\n")

# Función para recorrer la carpeta y obtener todas las imágenes
def obtener_imagenes(carpeta_principal):
    imagenes = []
    for carpeta, subcarpetas, archivos in os.walk(carpeta_principal):
        for archivo in archivos:
            if archivo.lower().endswith('.png'):
                imagenes.append(os.path.join(carpeta, archivo))
    return imagenes

# Función para procesar las imágenes con barra de progreso
def procesar_imagenes_con_barra(imagenes):
    with tqdm(total=len(imagenes), desc="Procesando imágenes", unit="imagen") as pbar:
        # Procesar imágenes en paralelo usando múltiples procesos
        with Pool(cpu_count()) as pool:
            for _ in pool.imap_unordered(procesar_imagen, imagenes):
                pbar.update(1)  # Actualiza la barra de progreso por cada imagen procesada

if __name__ == "__main__":
    # Limpiar los archivos de errores y detalles antes de iniciar
    with open(archivo_errores, "w", encoding="utf-8") as error_file:
        error_file.write("Errores encontrados durante el procesamiento:\n\n")

    with open(archivo_detalles, "w", encoding="utf-8") as detalles_file:
        detalles_file.write("Imágenes con la palabra clave 'DE CONTROL' ':\n\n")
    
    with open(archivo_movimientos, "w", encoding="utf-8") as error_renombrar_file:
        error_renombrar_file.write("Errores encontrados al intentar renombrar las imágenes:\n\n")

    # Obtener todas las imágenes de la carpeta principal
    imagenes = obtener_imagenes(carpeta_principal)
    
    # Llamar a la función de procesamiento con la barra de progreso
    procesar_imagenes_con_barra(imagenes)
print("Proceso terminado")