# Wiz Lamp Control

Aplicación de escritorio para controlar una lámpara **Philips Wiz** desde tu PC, sin necesidad de abrir el celular. Desarrollada en Python con `tkinter` y `pywizlight`.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

<img width="440" height="630" alt="image" src="https://github.com/user-attachments/assets/2b8c9368-0083-45fd-84c0-235fab16af28" />
<img width="440" height="630" alt="image" src="https://github.com/user-attachments/assets/5bff811f-128e-40d9-ba5d-c747ed585339" />


## Funciones

- **buscar y conectar** con la lampara mediante **IP**
- **Encender / Apagar** la lámpara con un clic
- **Control de color RGB** con sliders individuales por canal
- **Modos preconfigurados**: Blanco Cálido y Blanco Frío
- **Control de brillo** de 1% a 100%
- **Modo claro / oscuro** en la interfaz con un botón toggle
- **barra de estado** en la esquina inferior de la aplicación

---

## Requisitos

- Python 3.9 o superior
- La lámpara Wiz debe estar en la **misma red Wi-Fi** que tu PC
- Tkinter (incluido por defecto en la mayoría de instalaciones de Python)

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/NahuelDumbsky/wiz-lamp-control.git
cd wiz-lamp-control

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Correr la aplicación
python lamp_control.py
```

---

## Compilar como ejecutable

Para distribuir la app sin necesitar Python instalado, usá [PyInstaller](https://pyinstaller.org/).

```bash
pip install pyinstaller
```

**Windows** (genera `dist/lamp_control.exe`):
```bash
pyinstaller --onefile --windowed --hidden-import pywizlight lamp_control.py
```

**Linux** (genera `dist/lamp_control`):
```bash
pyinstaller --onefile --hidden-import pywizlight lamp_control.py
```

> PyInstaller solo compila para el sistema operativo donde se ejecuta.
> Para generar ambos binarios necesitás correr el comando en cada plataforma por separado.

Los ejecutables compilados están disponibles en la sección [**Releases**](../../releases).

---

## Estructura del proyecto

```
wiz-lamp-control/
├── lamp_control.py     # Código fuente principal
├── requirements.txt    # Dependencias Python
└── README.md
```

---

## Dependencias

| Paquete | Versión mínima | Uso |
|---|---|---|
| `pywizlight` | 0.6.0 | Comunicación con la lámpara Wiz vía UDP |

`tkinter` y `asyncio` vienen incluidos con Python y no requieren instalación adicional.

---

## Licencia

MIT — libre para usar, modificar y distribuir.
