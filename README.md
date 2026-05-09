# 👾 NazarievFontsTool: Pixel-to-Vector Magic

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build](https://img.shields.io/badge/build-optimized-orange.svg)
![Optimization](https://img.shields.io/badge/algorithm-horizontal--merge-brightgreen.svg)

**NazarievFontsTool** is a high-performance desktop utility designed for game developers and pixel artists. It transforms raw pixel-art sprite sheets into fully functional, industry-standard fonts. Whether you need a classic `.fnt` for a retro engine or a modern vector `.ttf`, this tool handles it with surgical precision and smart optimization.

---

## 🖼️ Visual Gallery

| 🖌️ Source Sprite Sheet | 🖥️ Tool Interface | 🚀 Final Result (Unity/OS) |
| :---: | :---: | :---: |
| ![Source Sheet](./images/Source%20Sheet.jpg) | ![GUI Preview](./images/GUI%20Preview.jpg) | ![Final Font](./images/Final%20Font.jpg) |
| *Your original pixel-art numbers & symbols.* | *The intuitive mapping & setup GUI.* | *The perfectly rendered vector output.* |

---

## 🔥 Why NazarievFontsTool?

Most converters simply turn every pixel into a vector square, resulting in "heavy" files and rendering artifacts. **NazarievFontsTool** is smarter. It understands the geometry of your font.

*   **Smart Scanline Optimization**: Our proprietary horizontal merge algorithm reduces vertex count by up to **70-80%**.
*   **Pixel-Perfect Integrity**: No blurring. No anti-aliasing issues. Just sharp, crisp pixels translated into vectors.
*   **Game-Dev Ready**: Generates AngelCode `.fnt` files that work out-of-the-box in **Unity (TextMeshPro)**, **Godot**, and **Defold**.

---

## 🛠️ Core Features

*   **🚀 Advanced Auto-Cropping**: Automatically detects the "ink" boundaries of each symbol, ensuring perfect kerning and spacing.
*   **💎 Vector Optimization (Horizontal Merge)**: Scans every row and merges adjacent pixels into single rectangular paths, making the `.ttf` incredibly lightweight.
*   **⚖️ Global Baseline Control**: Adjust the vertical alignment of all characters to ensure they sit perfectly on the "floor" of your text line.
*   **🧩 Interactive Mapping**: A user-friendly grid with magnified previews makes assigning characters to your sprites fast and error-free.

---

## 🧠 Technical Deep Dive: Horizontal Merge

The core strength of this tool is the optimization of the `.ttf` geometry. Instead of creating a vector path for every single pixel, the engine uses a **Scanline RLE (Run-Length Encoding)** approach.

For each row of a character, the algorithm identifies continuous sequences of filled pixels and generates a single rectangle using the following logic:

$$(x_{start}, y) \rightarrow (x_{start}, y+1) \rightarrow (x_{end}+1, y+1) \rightarrow (x_{end}+1, y)$$

This ensures that the font remains "light" for the GPU and prevents the "micro-gap" artifacts common in pixel-to-vector conversions.

$$Vertices_{optimized} \ll Vertices_{standard}$$

---

## 🚀 Getting Started

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/YourUsername/NazarievFontsTool.git
    cd NazarievFontsTool
    ```

2.  **Install dependencies**:
    ```bash
    pip install Pillow fonttools
    ```

### Running the Application

To run the source code directly:
```bash
python Source/nazariev_fonts_tool.py
```

### Building the Executable

To create a standalone `.exe` for Windows:
1.  Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  Run the build command:
    ```bash
    pyinstaller --onefile --noconsole --name "NazarievFontsTool" Source/nazariev_fonts_tool.py
    ```
    *The executable will be located in the `dist` folder.*

---

## 🤝 Credits & Support

Developed with a focus on efficiency and aesthetics for the **Nazariev** project.

Feel free to open an **Issue** or submit a **Pull Request** if you have ideas for new optimization algorithms! We are always looking for ways to make pixel-to-vector translation even more efficient.

---
*License: MIT*
