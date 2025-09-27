import time, os, win32print
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


DOWNLOADS = os.path.join(os.path.expanduser('~'), 'Downloads')
PRINTER_NAME = win32print.GetDefaultPrinter()


class Handler(FileSystemEventHandler):
def on_created(self, e):
if e.is_directory or not e.src_path.lower().endswith('.zpl'):
return
fp = e.src_path
print('Detectado:', fp)
# Esperar a que termine de escribirse
for _ in range(10):
try:
with open(fp, 'rb') as f: raw = f.read()
break
except Exception:
time.sleep(0.5)
h = win32print.OpenPrinter(PRINTER_NAME)
try:
job = win32print.StartDocPrinter(h, 1, ("ZPL Job", None, "RAW"))
win32print.StartPagePrinter(h)
win32print.WritePrinter(h, raw)
win32print.EndPagePrinter(h)
win32print.EndDocPrinter(h)
finally:
win32print.ClosePrinter(h)
os.remove(fp)
print('Impreso y borrado:', fp)


if __name__ == '__main__':
obs = Observer()
obs.schedule(Handler(), DOWNLOADS, recursive=False)
obs.start()
print('Vigilando', DOWNLOADS, '->', PRINTER_NAME)
try:
while True: time.sleep(1)
except KeyboardInterrupt:
obs.stop(); obs.join()
