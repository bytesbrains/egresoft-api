# Como inicializar el proyecto

Cuando desarrollamos utilizando librerias/paquetes externos en python utilizamos un gestor de paquetes, en este caso se utiliza Pip - Pip3 y un entorno virtual donde estara contenido nuestras librerias. Pero como utilizamos github no se debe subir nuestro entorno virtual ya que es nuestra carpeta donde esta contenido todo lo que utilizamos y puede ser antiproducente subir muchos archivos.

## Crear un entorno virtual python

```
python -m venv myenv
```

## Activar el entorno virtual

* **macOS y Linux**
  ```
  source myenv/bin/activate
  ```

* **Windows**
  ```
  myenv\Scripts\activate.bat
  ```

## Instalar los paquetes de requeriments.txt
  ```
  pip install -r requirements.txt
  ```

## Desactivar el entorno virtual
  Cuando hayas terminado de trabajar en tu proyecto, puedes desactivar el entorno virtual ejecutando:

  ```
  deactivate
  ```

## Correr el servidor
Abre tu terminal y ejecuta el siguiente comando desde la ubicación donde se encuentra tu archivo main.py:
```
uvicorn app:app --reload
```
Donde app(archivo):app(nombre de la instancia de FastAPI en nuestro archivo.py)

## Final
**Despues de estos pasos, tu entorno de desarrollo ya estara configurado y listo**