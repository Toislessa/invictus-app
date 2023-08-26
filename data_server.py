import time
import subprocess
import sys

print(sys.executable)

while True:
    subprocess.call([sys.executable, "intervalos13.py"])
    time.sleep(60)  # Espera 60 segundos antes de executar novamente
