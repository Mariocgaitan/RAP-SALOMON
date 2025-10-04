from pyzxing import BarCodeReader
from PIL import Image
import os
import uuid
import concurrent.futures
from threading import Lock
from tqdm import tqdm  # Barra de progreso

# Bloqueo global para operaciones críticas
lock = Lock()

def procesar_imagen(image_path, errores_folder, proceso_txt, error_qr_txt, error_rename_txt):
    try:
        with lock:
            # Registrar que se está procesando la imagen
            with open(proceso_txt, "a") as file:
                file.write(f"Procesando imagen: {image_path}\n")

        image = Image.open(image_path)

        # Define las coordenadas del perímetro (zona rectangular)
        left = 1406  # Coordenada X superior izquierda
        upper = 2438  # Coordenada Y superior izquierda
        right = 2450  # Coordenada X inferior derecha
        lower = 3145  # Coordenada Y inferior derecha

        # Recorta la imagen
        cropped_image = image.crop((left, upper, right, lower))

        # Genera un nombre único para el archivo temporal
        temp_filename = f"recortada_{uuid.uuid4().hex}.png"
        cropped_image.save(temp_filename)

        # Inicializa el lector de ZXing dentro de la función
        reader = BarCodeReader()

        # Decodifica el QR de la imagen recortada
        result = reader.decode(temp_filename)

        # Elimina el archivo temporal después de usarlo
        os.remove(temp_filename)

        # Si no se detectó ningún QR
        if not result:
            error_image_path = os.path.join(errores_folder, os.path.basename(image_path))
            with lock:
                os.rename(image_path, error_image_path)
                with open(error_qr_txt, "a") as file:
                    file.write(f"No se pudo leer el QR de la imagen: {image_path}\n")
                with open(proceso_txt, "a") as file:
                    file.write(f"Error: No se pudo leer el QR de la imagen: {image_path}\n")
            return

        # Si se detectó un QR
        qr_value = result[0]['raw'].decode('utf-8')

        # Obtiene la extensión de la imagen original
        file_name, file_extension = os.path.splitext(os.path.basename(image_path))

        # Genera el nuevo nombre con el valor del QR
        new_image_name = os.path.join(os.path.dirname(image_path), f"{file_name}_{qr_value}{file_extension}")

        # Renombrar con un bloqueo para evitar conflictos
        with lock:
            if os.path.exists(new_image_name):
                error_image_path = os.path.join(errores_folder, os.path.basename(image_path))
                os.rename(image_path, error_image_path)
                with open(error_rename_txt, "a") as file:
                    file.write(f"El archivo con el mismo nombre ya existe: {new_image_name}, imagen que no se pudo modificar: {image_path}\n")
                with open(proceso_txt, "a") as file:
                    file.write(f"Error: El archivo con el mismo nombre ya existe: {new_image_name}\n")
                return

            # Renombra la imagen original
            os.rename(image_path, new_image_name)

            # Registro exitoso en el archivo de proceso
            with open(proceso_txt, "a") as file:
                file.write(f"Imagen renombrada exitosamente a: {new_image_name}\n")

    except Exception as e:
        # Manejo de errores generales
        with lock:
            error_image_path = os.path.join(errores_folder, os.path.basename(image_path))
            try:
                os.rename(image_path, error_image_path)
            except Exception as rename_error:
                with open(proceso_txt, "a") as file:
                    file.write(f"Error al mover la imagen {image_path} a la carpeta de errores: {rename_error}\n")
            finally:
                with open(error_qr_txt, "a") as file:
                    file.write(f"Error al procesar la imagen {image_path}: {str(e)}\n")


def procesar_carpeta(ruta_carpeta):
    for root, dirs, files in os.walk(ruta_carpeta):
        if "De control" in root:
            errores_folder = os.path.join(root, "Errores")
            os.makedirs(errores_folder, exist_ok=True)

            # Archivos de registro específicos de la carpeta "De control"
            proceso_txt = os.path.join(root, "Proceso_imagenes.txt")
            error_qr_txt = os.path.join(root, "Error_al_leer_el_qr.txt")
            error_rename_txt = os.path.join(root, "Error_al_renombrar.txt")

            # Asegúrate de crear los archivos vacíos al inicio
            with open(proceso_txt, "w") as file:
                file.write("Inicio del registro de proceso.\n")
            with open(error_qr_txt, "w") as file:
                file.write("Errores al leer QR:\n")
            with open(error_rename_txt, "w") as file:
                file.write("Errores al renombrar archivos:\n")

            # Filtra solo los archivos con extensiones de imágenes
            image_files = [os.path.join(root, f) for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

            # Crear la barra de progreso con tqdm
            with tqdm(total=len(image_files), desc="Procesando imágenes", unit="imagen") as pbar:
                # Procesar las imágenes en paralelo
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    # Enviar tareas para cada imagen
                    futures = [executor.submit(procesar_imagen, image_path, errores_folder, proceso_txt, error_qr_txt, error_rename_txt) for image_path in image_files]

                    # Esperar que todos los hilos terminen y actualizar la barra
                    for future in concurrent.futures.as_completed(futures):
                        pbar.update(1)  # Actualiza la barra de progreso por cada imagen procesada


# Ruta de la carpeta principal
ruta_carpeta_principal = r"C:\Users\mario\OneDrive\Documentos\Imagenes\Recortes - Copy (10) - Copy - Copy (3)"

# Procesa la carpeta principal
procesar_carpeta(ruta_carpeta_principal)
print("Proceso terminado")
