[app]

# Nombre visible de la app
title = IA contra el Ciberacoso

# Nombre de paquete (sin espacios ni mayúsculas)
package.name = antiacoso
package.domain = org.antiacoso

# Carpeta con el código y qué archivos incluir
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# Solo empaquetamos lo necesario de la app (evita meter el .exe, dist, etc.)
source.include_patterns = main.py,motor.py
source.exclude_dirs = dist,build,__pycache__,.github,.buildozer

version = 1.0

# Dependencias que se instalan dentro del APK
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

# Íconos / presentación (opcional; si no existen, usa los de Kivy)
# icon.filename = %(source.dir)s/icono.png

[buildozer]

log_level = 2
warn_on_root = 0

[android]

# Versiones de Android
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a

# Permite acortar tiempos; acepta licencias del SDK automáticamente en CI
android.accept_sdk_license = True
