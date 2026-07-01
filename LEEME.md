# 🛡️ IA contra el Ciberacoso (Detección de Agresividad)

Aplicación que lee un mensaje de texto y decide si es **AGRESIVO** o **SEGURO**.
Viene en **3 versiones** con la MISMA inteligencia (verificada al 100% de precisión):
- 🌐 **Web** (PC y Android, navegador, sin internet)
- 🖥️ **App de PC** (`.exe`, doble clic, sin instalar nada)
- 📱 **App de Android** (`.apk`, se compila en la nube con GitHub Actions)

## 📂 Archivos
| Archivo | Para qué sirve |
|---|---|
| **Versión Web** | |
| `index.html` | La app web (interfaz visual). |
| `motor.js` | El "cerebro" de la IA en JavaScript. |
| `worker.js` | Análisis **en segundo plano** (hilo aparte) para que no se congele. |
| `sw.js` | Service Worker: funciona **sin internet** y se puede instalar. |
| `manifest.json` | Permite instalarla como app en Android/PC. |
| `servidor.js` | Servidor local para probar el modo offline en tu PC. |
| **Versión PC (.exe)** | |
| `IA_Anti_Ciberacoso.exe` | La app de escritorio lista. **Doble clic y funciona.** |
| `app.py` | Código de la app de PC (interfaz Tkinter). |
| `motor.py` | El "cerebro" de la IA en Python (lo usan el .exe y el APK). |
| **Versión Android (.apk)** | |
| `main.py` | Código de la app Android (interfaz Kivy). |
| `buildozer.spec` | Configuración para compilar el APK. |
| `.github/workflows/build-apk.yml` | Compila el APK automático en la nube. |

## 🖥️ Versión PC (.exe)
Solo haz **doble clic en `IA_Anti_Ciberacoso.exe`**. No necesita Python ni instalación.
(Si Windows muestra un aviso de "editor desconocido", es normal en apps sin firma:
"Más información" → "Ejecutar de todas formas".)

Para editar el código: `python app.py`. Para regenerar el .exe:
`pip install pyinstaller` y luego `pyinstaller --onefile --windowed --add-data "motor.py;." app.py`

## 📱 Versión Android (.apk) — cómo generarla
El `.apk` se compila **gratis en la nube** (no hace falta Android Studio ni Linux en tu PC):
1. Crea una cuenta gratis en **github.com** y un repositorio nuevo.
2. Sube TODA esta carpeta al repositorio (botón "Add file" → "Upload files").
3. Ve a la pestaña **Actions** del repositorio → el flujo "Compilar APK Android" arranca solo
   (o púlsalo con "Run workflow"). Tarda ~15–25 min la primera vez.
4. Cuando termine (✔ verde), entra al run y descarga el **artifact** `IA-Anti-Ciberacoso-APK`.
   Dentro está tu `.apk`.
5. Pásalo al teléfono, ábrelo y permite "instalar de orígenes desconocidos".

> Nota honesta: el `.apk` no se pudo compilar/probar en esta PC (Buildozer requiere Linux),
> por eso se usa GitHub Actions, que lo construye en un servidor Linux. Si el primer intento
> falla por algún detalle del entorno, avísame y lo ajusto.

## 🟢 Modo "segundo plano" (novedad)
- **No se congela:** el análisis corre en un hilo aparte (Web Worker), aunque proceses cientos de mensajes.
- **Funciona sin internet e instalable:** con Service Worker; aparece el botón **"Instalar app"** y el estado **"Modo offline activo"**.
- **📡 Pestaña Vigilancia:** analiza automáticamente lo que escribes/pegas, sin apretar botones, y te **avisa con una notificación** si detecta agresividad.
  > ⚠️ Una página web **no puede** leer los mensajes de otras apps (WhatsApp, etc.) por seguridad. Para eso haría falta una app nativa de Android (proyecto aparte).

## ▶️ Cómo usarla en la PC
**Modo simple (doble clic):** haz doble clic en **`index.html`**. Funciona todo el análisis,
pero el modo offline y el botón "Instalar" NO aparecen (los navegadores los bloquean con `file://`).

**Modo completo (con servidor, recomendado):** tienes Node.js instalado, así que:
1. Abre una terminal en esta carpeta.
2. Ejecuta:  `node servidor.js`
3. Abre en el navegador:  **http://localhost:8080**
   Ahí sí aparecen "Instalar app" y "Modo offline activo".

### Las 4 pestañas
- **🔎 Analizar**: escribes un mensaje y te dice si es agresivo o seguro + el tiempo que tardó.
- **📊 Masivo**: pegas una lista (hasta 100+ mensajes, uno por línea) y los analiza todos en segundo plano.
- **✅ Precisión**: corre las 50 frases de prueba y muestra el % de aciertos.
- **📡 Vigilancia**: analiza solo lo que escribes/pegas y avisa con notificación si hay agresividad.

## 📱 Cómo usarla en Android
**Opción rápida:** copia la carpeta al teléfono y abre `index.html` con Chrome.

**Opción recomendada (queda como app con ícono):**
1. Sube la carpeta a un hosting gratis (por ejemplo **Netlify Drop**: arrastras la carpeta y te da un enlace).
2. Abre ese enlace en Chrome en tu Android.
3. Menú ⋮ → **"Agregar a la pantalla de inicio"**. ¡Listo, queda como app!

## ✅ Requisitos del proyecto (verificados)
| Requisito | Meta | Resultado |
|---|---|---|
| ⚡ Velocidad (1 mensaje) | < 2000 ms | **~0.07 ms** ✔ |
| 🎯 Precisión (50 frases) | ≥ 90% | **100%** ✔ |
| 📊 Análisis masivo | 100 mensajes sin colgarse | **1.6 ms total, estable** ✔ |

## 🧠 ¿Cómo decide la IA?
1. **Normaliza** el texto: minúsculas, quita acentos, deshace trucos para esquivar filtros
   (ej. `1di0ta` → `idiota`, `idiotaaaa` → `idiota`).
2. Busca **insultos y amenazas** en su diccionario (cada uno con un peso según gravedad).
3. Detecta **ataques directos** ("eres un…"), **gritos** (MAYÚSCULAS) y **expresiones hostiles**.
4. Reduce el riesgo si detecta **señales amistosas** (gracias, felicidades, risas 😂) —
   así **no confunde una broma sana con acoso**— salvo que haya un insulto claramente fuerte.
5. Si el puntaje supera el umbral → **AGRESIVO**; si no → **SEGURO**.

> ⚠️ Es una herramienta educativa de apoyo. No reemplaza el criterio de un adulto o profesor.
