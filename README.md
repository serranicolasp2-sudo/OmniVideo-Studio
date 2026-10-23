# OmniVideo Studio — Suite Audiovisual Unificada

[![Tu Tiendita IA](https://img.shields.io/badge/Tu%20Tiendita%20IA-tutiendita--ia.store-1E3C96.svg)](https://tutiendita-ia.store)
[![Release](https://img.shields.io/badge/Release-v1.0.0-E0435C.svg)](https://github.com/serranicolasp2-sudo/OmniVideo-Studio/releases/latest)
[![Windows](https://img.shields.io/badge/Plataforma-Windows%2010%20%2F%2011%20x64-FFD23F.svg?labelColor=1A1712)](https://tutiendita-ia.store)
[![FFmpeg](https://img.shields.io/badge/Motor-FFmpeg%20Full%20Hardware-green.svg)](https://ffmpeg.org)

**OmniVideo Studio** es la estación unificada de procesamiento y mejora audiovisual de **Tu Tiendita IA**, diseñada especialmente para creadores de contenido, animadores 3D (Pixar/CGI), editores de video y community managers.

Aúna las capacidades de **OmniBoost**, **OmniFlow** y **OmniScale** en una sola interfaz moderna, ligera e intuitiva, e introduce el **Modo Cadena (Single-Pass Pipeline)**.

---

## 🚀 ¿Por qué una suite unificada?

Anteriormente, para mejorar un video, aumentar sus cuadros a 60 FPS y escalarlo a 4K, era necesario pasarlo por tres programas distintos. Eso implicaba:
- **3 exportaciones sucesivas** (triplicando el tiempo de procesamiento).
- **3 recompresiones de video**, acumulando degradación y pérdida de nitidez generacional.
- **588 MB** de peso descargado (al duplicar FFmpeg en tres portables distintos).

Con **OmniVideo Studio**:
1. **Un solo motor FFmpeg compartido**: El instalador completo pesa solo **123 MB** y el portable **176 MB**.
2. **Modo Cadena en 1 sola pasada**: Aplica limpieza de ruido, contraste adaptativo CAS, interpolación a 60 FPS y escalado Lanczos/Spline36 directamente en el filtergraph de FFmpeg antes de la codificación final.
3. **Cero pérdida generacional**: Se codifica una única vez al archivo final.
4. **Soporte de Hardware Completo**: NVIDIA NVENC (preset P7 HQ multipass), AMD AMF y CPU libx264 con auto-fallback inteligente.

---

## 🎛️ Modos de Procesamiento

| Modo | Descripción | Tecnologías Clave |
|---|---|---|
| **🎬 Mejorar (OmniBoost)** | Mejora de contraste, realce de bordes y restauración. | CAS (Contrast Adaptive Sharpening), de-banding gradfun, desruido hqdn3d y curvas gamma/color. |
| **⚡ Fluidez (OmniFlow)** | Interpolación de cuadros a 48, 50, 60 o 120 FPS. | Flujo Óptico bidireccional (`minterpolate` MCI + AOBMC), Motion Blend y modo Anime. |
| **📱 Escalar (OmniScale)** | Reescalado adaptativo a 1080p, 2K o 4K Ultra HD. | Lanczos, Spline36, CAS y detección de relación de aspecto (16:9 apaisado, 9:16 vertical Reels/TikTok, 1:1). |
| **🔗 Cadena (Single-Pass)** | Ejecuta **Mejora + Fluidez + Escalado** en una sola pasada. | Filtergraph compuesto en memoria sin archivos temporales intermedios. |

---

## 📥 Descarga e Instalación

Podés descargar la versión oficial desde [GitHub Releases](https://github.com/serranicolasp2-sudo/OmniVideo-Studio/releases/latest):

- **Instalador para Windows (`.exe` ~123 MB)**: Asistente guiado que crea accesos directos en el Escritorio y Menú Inicio.
- **Versión Portable (`.zip` ~176 MB)**: Descomprimir y ejecutar directamente desde `OmniVideo Studio.exe` (ideal para pendrives o almacenamiento externo). No requiere conexión a internet ni librerías adicionales.

---

## 🛠️ Requisitos del Sistema

- **Sistema Operativo**: Windows 10 o Windows 11 (64-bit).
- **Procesador**: Intel Core i3 / AMD Ryzen 3 o superior.
- **Memoria RAM**: 4 GB mínimo (8 GB recomendado para 4K).
- **Aceleración por Hardware (Opcional)**:
  - NVIDIA GeForce GTX 900 o superior (arquitectura Maxwell, Pascal, Turing, Ampere, Ada Lovelace).
  - AMD Radeon RX 400 o superior.

---

## 💻 Desarrollo y Compilación Local

Para desarrolladores o colaboradores:

```bash
# Clonar el repositorio
git clone https://github.com/serranicolasp2-sudo/OmniVideo-Studio.git
cd OmniVideo-Studio

# Ejecutar con Python
python app_omnivideo_studio.py

# Compilar ejecutable con PyInstaller
python build_omnivideo.py
```

---

## 🏢 Créditos y Licencia

Desarrollado para el ecosistema de [Tu Tiendita IA](https://tutiendita-ia.store).  
Licencia MIT.
