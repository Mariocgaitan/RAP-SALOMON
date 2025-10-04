from pytesseract import pytesseract
from PIL import Image
import os
import re
from multiprocessing import Pool, cpu_count, Manager
from tqdm import tqdm  # Para la barra de progreso

# Ruta completa al ejecutable de Tesseract
pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Carpeta principal
carpeta_principal = r"C:\Users\mario\OneDrive\Documentos\Imagenes\17-09-24 - Copy (3) - Copy (2)"


def procesar_imagen(args):
    ruta_imagen, queue = args
    try:
        # Extraer texto de la imagen
        texto = pytesseract.image_to_string(Image.open(ruta_imagen), lang="spa")  # Cambiar idioma si es necesario

        # Guardar el texto extraído en un archivo .txt dentro de la subcarpeta "Errores"
        nombre_base = os.path.splitext(os.path.basename(ruta_imagen))[0]
        carpeta_errores = os.path.dirname(ruta_imagen)
        ruta_txt = os.path.join(carpeta_errores, f"{nombre_base}.txt")
        with open(ruta_txt, "w", encoding="utf-8") as file:
            file.write(texto)

        # Buscar patrón "WVU" seguido de 12 caracteres
        match = re.search(r"(WVU\S{12})|(WNE\S{12})", texto)
        if match:
            wvu_value = match.group(1)
            # Crear nuevo nombre para el archivo PNG
            nuevo_nombre = f"{nombre_base}_{wvu_value}.png"
            nueva_ruta = os.path.join(carpeta_errores, nuevo_nombre)

            # Renombrar la imagen
            os.rename(ruta_imagen, nueva_ruta)

        else:
            # Si no encuentra el patrón, agregar "_errorrenombrando"
            nuevo_nombre = f"{nombre_base}_errorrenombrando.png"
            nueva_ruta = os.path.join(carpeta_errores, nuevo_nombre)
            os.rename(ruta_imagen, nueva_ruta)

    except Exception as e:
        # Registrar errores en el archivo de errores dentro de la subcarpeta "Errores"
        carpeta_errores = os.path.dirname(ruta_imagen)
        ruta_errores = os.path.join(carpeta_errores, "errores.txt")
        with open(ruta_errores, "a", encoding="utf-8") as error_file:
            error_file.write(f"Error procesando {ruta_imagen}: {e}\n")
    finally:
        # Notificar al proceso principal que se procesó una imagen
        queue.put(1)


def buscar_imagenes(carpeta_principal):
    # Buscar imágenes en subcarpetas "Errores"
    imagenes = []
    for carpeta, subcarpetas, archivos in os.walk(carpeta_principal):
        if "Errores" in carpeta:
            # Crear archivos de registro en cada carpeta "Errores"
            archivo_errores = os.path.join(carpeta, "errores.txt")
            archivo_movimientos = os.path.join(carpeta, "movimientos.txt")
            with open(archivo_errores, "w", encoding="utf-8") as error_file:
                error_file.write("Errores encontrados durante el procesamiento:\n\n")
            with open(archivo_movimientos, "w", encoding="utf-8") as movimientos_file:
                movimientos_file.write("Movimientos realizados durante el procesamiento:\n\n")

            # Agregar imágenes a la lista
            for archivo in archivos:
                if archivo.lower().endswith(".png"):
                    imagenes.append(os.path.join(carpeta, archivo))
    return imagenes


if __name__ == "__main__":
    # Buscar imágenes en las carpetas "Errores"
    imagenes = buscar_imagenes(carpeta_principal)

    # Procesar imágenes en paralelo
    num_procesos = min(cpu_count(), len(imagenes))
    print(f"Procesando {len(imagenes)} imágenes con {num_procesos} procesos...")

    # Crear un manager para manejar la cola
    with Manager() as manager:
        queue = manager.Queue()

        # Crear una barra de progreso con tqdm
        with tqdm(total=len(imagenes), desc="Procesando imágenes", unit="imagen") as pbar:
            # Crear un pool de procesos
            with Pool(num_procesos) as pool:
                # Mapear la función procesar_imagen con la cola de progreso
                for _ in pool.imap_unordered(procesar_imagen, [(ruta, queue) for ruta in imagenes]):
                    # Actualizar la barra de progreso con el conteo de la cola
                    while not queue.empty():
                        queue.get()  # Sacar un elemento de la cola
                        pbar.update(1)
print("Proceso terminado")