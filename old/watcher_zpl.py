import os
import time
import win32print
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# === CONFIGURACIÓN ===
CARPETA_A_MONITOREAR = r"C:\Users\Lautaro\Downloads"
EXTENSION_OBJETIVO = ".zpl"

class ManejadorDeEventos(FileSystemEventHandler):
    def procesa_archivo(self, path):
        if (
            not os.path.isdir(path)
            and path.lower().endswith(EXTENSION_OBJETIVO)
            and not path.lower().endswith(".tmp.zpl")
        ):
            print(f"🖨️ Detectado (crear/modif): {path}")
            time.sleep(1.5)
            imprimir_zpl(path)

    def on_created(self, event):
        self.procesa_archivo(event.src_path)

    def on_modified(self, event):
        self.procesa_archivo(event.src_path)

def imprimir_zpl(zpl_path):
    try:
        with open(zpl_path, 'r', encoding='utf-8') as f:
            contenido = f.read()

        impresora = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(impresora)
        job = win32print.StartDocPrinter(hprinter, 1, ("Etiqueta ZPL", None, "RAW"))
        win32print.StartPagePrinter(hprinter)
        win32print.WritePrinter(hprinter, contenido.encode('utf-8'))
        win32print.EndPagePrinter(hprinter)
        win32print.EndDocPrinter(hprinter)
        win32print.ClosePrinter(hprinter)

        print(f"✅ Impreso correctamente: {os.path.basename(zpl_path)}")
        os.remove(zpl_path)

    except Exception as e:
        print(f"❌ Error al imprimir {zpl_path}: {e}")

if __name__ == "__main__":
    print(f"👀 Monitoreando: {CARPETA_A_MONITOREAR}")
    observer = Observer()
    observer.schedule(ManejadorDeEventos(), CARPETA_A_MONITOREAR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
