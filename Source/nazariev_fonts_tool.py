import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

try:
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    FONTTOOLS_AVAILABLE = True
except ImportError:
    FONTTOOLS_AVAILABLE = False

# Image Processing Logic

def get_symbol_bounds(image):
    """Finds the actual bounding box of non-transparent pixels."""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    pixels = image.load()
    width, height = image.size
    
    x_min, y_min = width, height
    x_max, y_max = -1, -1
    
    found = False
    for y in range(height):
        for x in range(width):
            if pixels[x, y][3] > 0:  # Alpha > 0
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x)
                y_max = max(y_max, y)
                found = True
                
    if not found:
        return None
        
    return (x_min, y_min, x_max, y_max)

def slice_sheet(image_path, cell_w, cell_h):
    """Slices the image into cells."""
    try:
        img = Image.open(image_path).convert('RGBA')
    except Exception as e:
        print(f"Error opening image: {e}")
        return []
        
    img_w, img_h = img.size
    cells = []
    
    for y in range(0, img_h, cell_h):
        for x in range(0, img_w, cell_w):
            box = (x, y, x + cell_w, y + cell_h)
            crop = img.crop(box)
            bounds = get_symbol_bounds(crop)
            if bounds:
                cells.append({
                    'image': crop,
                    'bounds': bounds,
                    'original_pos': (x, y)
                })
    return cells

# GUI Components

class FontToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NazarievFontsTool v1.0")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", foreground="#333333", font=("Segoe UI", 10))
        self.style.configure("TEntry", fieldbackground="#ffffff", foreground="#000000", insertcolor="#000000")
        self.style.configure("TButton", background="#e1e1e1", foreground="#333333")
        
        self.cells = []
        self.mappings = {} # index -> char
        self.preview_scale = 4
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top Panel: Settings
        top_panel = ttk.Frame(self.root, padding=10)
        top_panel.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(top_panel, text="Cell W:").pack(side=tk.LEFT, padx=5)
        self.cell_w_entry = ttk.Entry(top_panel, width=5)
        self.cell_w_entry.insert(0, "16")
        self.cell_w_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(top_panel, text="Cell H:").pack(side=tk.LEFT, padx=5)
        self.cell_h_entry = ttk.Entry(top_panel, width=5)
        self.cell_h_entry.insert(0, "16")
        self.cell_h_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(top_panel, text="Global Baseline:").pack(side=tk.LEFT, padx=5)
        self.baseline_entry = ttk.Entry(top_panel, width=5)
        self.baseline_entry.insert(0, "0")
        self.baseline_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(top_panel, text="Space Width:").pack(side=tk.LEFT, padx=5)
        self.space_w_entry = ttk.Entry(top_panel, width=5)
        self.space_w_entry.insert(0, "4")
        self.space_w_entry.pack(side=tk.LEFT, padx=5)
        
        self.load_btn = ttk.Button(top_panel, text="Load Sheet", command=self.load_sheet)
        self.load_btn.pack(side=tk.LEFT, padx=10)
        
        self.export_btn = ttk.Button(top_panel, text="Export FNT", command=self.export_font)
        self.export_btn.pack(side=tk.RIGHT, padx=10)
        
        self.export_ttf_btn = ttk.Button(top_panel, text="Export TTF", command=self.export_ttf)
        self.export_ttf_btn.pack(side=tk.RIGHT, padx=5)
        
        if not FONTTOOLS_AVAILABLE:
            self.export_ttf_btn.config(state=tk.DISABLED)
            ttk.Label(top_panel, text="(pip install fonttools)", foreground="#ff5555").pack(side=tk.RIGHT, padx=5)
        
        # Middle Area: Scrollable Grid
        self.canvas = tk.Canvas(self.root, bg="#ffffff", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def load_sheet(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.bmp *.jpg")])
        if not file_path:
            return
            
        self.image_path = file_path
        cell_w = int(self.cell_w_entry.get())
        cell_h = int(self.cell_h_entry.get())
        
        self.cells = slice_sheet(file_path, cell_w, cell_h)
        self.refresh_grid()
        
    def refresh_grid(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        cols = 8
        
        # --- Add Dedicated Space Entry ---
        space_frame = tk.Frame(self.scrollable_frame, bg="#e1e1e1", bd=2, relief=tk.SOLID, padx=5, pady=5)
        space_frame.grid(row=0, column=0, padx=5, pady=5)
        
        tk.Label(space_frame, text="SPACE", bg="#e1e1e1", fg="#000000", font=("Segoe UI", 8, "bold")).pack()
        tk.Label(space_frame, text="(ID 32)", bg="#e1e1e1", fg="#666666", font=("Segoe UI", 7)).pack()
        
        space_entry = tk.Entry(space_frame, width=5, bg="#ffffff", fg="#000000", insertbackground="black", justify='center')
        space_entry.insert(0, " ") # Pre-filled with space
        space_entry.pack(pady=2)
        self.mappings["space"] = " " # Special key for space mapping
        
        # Bind space entry
        space_entry.bind("<KeyRelease>", lambda e: self.update_mapping("space", e.widget.get()))

        # --- Render Sliced Cells ---
        for i, cell in enumerate(self.cells):
            grid_idx = i + 1 # Offset by 1 for space
            frame = tk.Frame(self.scrollable_frame, bg="#e1e1e1", bd=1, relief=tk.RAISED, padx=5, pady=5)
            frame.grid(row=grid_idx // cols, column=grid_idx % cols, padx=5, pady=5)
            
            # Preview scaled up
            scaled_img = cell['image'].resize(
                (cell['image'].width * self.preview_scale, cell['image'].height * self.preview_scale),
                Image.NEAREST
            )
            tk_img = ImageTk.PhotoImage(scaled_img)
            
            lbl = tk.Label(frame, image=tk_img, bg="#ffffff")
            lbl.image = tk_img 
            lbl.pack()
            
            entry = tk.Entry(frame, width=5, bg="#ffffff", fg="#000000", insertbackground="black", justify='center')
            entry.pack(pady=2)
            
            # Bind entry to mapping
            def make_callback(index):
                return lambda event: self.update_mapping(index, event.widget.get())
            
            entry.bind("<KeyRelease>", make_callback(i))

    def update_mapping(self, index, value):
        if value:
            self.mappings[index] = value
        else:
            if index in self.mappings:
                del self.mappings[index]
                
    def export_font(self):
        if not self.cells or not self.mappings:
            messagebox.showwarning("Warning", "Nothing to export! Map some characters first.")
            return
            
        save_dir = filedialog.askdirectory()
        if not save_dir:
            return
            
        font_name = os.path.splitext(os.path.basename(self.image_path))[0]
        fnt_path = os.path.join(save_dir, f"{font_name}.fnt")
        atlas_path = os.path.join(save_dir, f"{font_name}_atlas.png")
        
        # 1. Prepare data for packing
        mapped_data = []
        for key, char in self.mappings.items():
            if key == "space":
                # Space special case
                space_w = int(self.space_w_entry.get())
                mapped_data.append({
                    'char': ' ',
                    'id': 32,
                    'img': None,
                    'w': 0,
                    'h': 0,
                    'xoffset': 0,
                    'yoffset': 0,
                    'xadvance': space_w
                })
                continue
                
            cell = self.cells[key]
            bx = cell['bounds']
            w = bx[2] - bx[0] + 1
            h = bx[3] - bx[1] + 1
            
            # Crop to actual symbol
            symbol_img = cell['image'].crop(bx)
            
            mapped_data.append({
                'char': char,
                'id': ord(char),
                'img': symbol_img,
                'w': w,
                'h': h,
                'xoffset': bx[0],
                'yoffset': bx[1]
            })
        
        # 2. Pack Atlas (Simple Strip Packing for now, can be improved to square)
        # Sort by height for better packing
        mapped_data.sort(key=lambda x: x['h'], reverse=True)
        
        atlas_w = 256 # Default width, can grow
        atlas_h = 0
        
        current_x = 0
        current_y = 0
        row_h = 0
        
        # Pre-calculate positions
        for item in mapped_data:
            if item['id'] == 32: continue # Space has no image
            
            if current_x + item['w'] + 1 > atlas_w:
                current_x = 0
                current_y += row_h + 1
                row_h = 0
            
            item['atlas_x'] = current_x
            item['atlas_y'] = current_y
            
            current_x += item['w'] + 1
            row_h = max(row_h, item['h'])
            atlas_h = max(atlas_h, current_y + row_h)
            
        # Create Atlas Image
        atlas_img = Image.new('RGBA', (atlas_w, atlas_h), (0,0,0,0))
        global_baseline = int(self.baseline_entry.get())
        
        # 3. Generate FNT content
        fnt_lines = [
            f"info face=\"{font_name}\" size=16 bold=0 italic=0 charset=\"\" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=1,1 outline=0",
            f"common lineHeight={int(self.cell_h_entry.get())} base={global_baseline} scaleW={atlas_w} scaleH={atlas_h} pages=1 packed=0 alphaChnl=1 redChnl=0 greenChnl=0 blueChnl=0",
            f"page id=0 file=\"{font_name}_atlas.png\"",
            f"chars count={len(mapped_data)}"
        ]
        
        for item in mapped_data:
            if item['id'] == 32:
                # Space special case
                fnt_lines.append(f"char id=32 x=0 y=0 width=0 height=0 xoffset=0 yoffset=0 xadvance={item['xadvance']} page=0 chnl=15")
                continue
                
            atlas_img.paste(item['img'], (item['atlas_x'], item['atlas_y']))
            
            # YOffset adjustment logic: 
            # In FNT, yoffset is from top. Our yoffset is pixel-pos in cell.
            # We add user baseline to tweak.
            y_off = item['yoffset'] + global_baseline
            x_adv = item['w'] + 1
            
            fnt_lines.append(
                f"char id={item['id']} x={item['atlas_x']} y={item['atlas_y']} "
                f"width={item['w']} height={item['h']} "
                f"xoffset=0 yoffset={y_off} xadvance={x_adv} page=0 chnl=15"
            )
            
        # 4. Save
        with open(fnt_path, 'w') as f:
            f.write('\n'.join(fnt_lines))
        
        atlas_img.save(atlas_path)
        messagebox.showinfo("Success", f"Exported successfully to {save_dir}")

    def export_ttf(self):
        if not FONTTOOLS_AVAILABLE:
            messagebox.showerror("Error", "fonttools library is not installed. Run 'pip install fonttools'.")
            return
            
        if not self.cells or not self.mappings:
            messagebox.showwarning("Warning", "Nothing to export! Map some characters first.")
            return
            
        save_dir = filedialog.askdirectory()
        if not save_dir:
            return
            
        try:
            font_name = os.path.splitext(os.path.basename(self.image_path))[0]
            # Replace spaces and special chars for internal font name
            safe_name = "".join([c if c.isalnum() else "" for c in font_name]) or "PixelFont"
            ttf_path = os.path.join(save_dir, f"{font_name}.ttf")
            
            # TTF Parameters
            UPM = 1024
            cell_h = int(self.cell_h_entry.get())
            scale = UPM // cell_h
            global_baseline = int(self.baseline_entry.get())
            
            ascent = global_baseline * scale
            descent = -(cell_h - global_baseline) * scale
            
            fb = FontBuilder(UPM, isTTF=True)
            
            glyphs = {}
            metrics = {} 
            cmap = {} 
            glyph_order = ['.notdef']
            
            # 1. Create .notdef glyph (Standard square with X)
            pen = TTGlyphPen(None)
            pen.moveTo((scale, 0))
            pen.lineTo((scale, ascent))
            pen.lineTo((scale*5, ascent))
            pen.lineTo((scale*5, 0))
            pen.closePath()
            glyphs['.notdef'] = pen.glyph()
            metrics['.notdef'] = (scale*6, scale)
            
            # 2. Iterate mappings
            for key, char in self.mappings.items():
                if key == "space":
                    space_w = int(self.space_w_entry.get())
                    g_name = "space"
                    glyphs[g_name] = TTGlyphPen(None).glyph()
                    metrics[g_name] = (space_w * scale, 0)
                    cmap[32] = g_name
                    if g_name not in glyph_order:
                        glyph_order.append(g_name)
                    continue
                    
                cell = self.cells[key]
                bx = cell['bounds']
                crop_box = (bx[0], bx[1], bx[2] + 1, bx[3] + 1)
                symbol_img = cell['image'].crop(crop_box)
                w, h = symbol_img.size
                
                g_name = f"uni{ord(char):04X}"
                cmap[ord(char)] = g_name
                if g_name not in glyph_order:
                    glyph_order.append(g_name)
                
                pen = TTGlyphPen(None)
                pixels = symbol_img.load()
                
                # Draw optimized vector rectangles (horizontal merging)
                for py in range(h):
                    px = 0
                    while px < w:
                        if pixels[px, py][3] > 128:
                            x_start = px
                            # Find the end of the contiguous segment of solid pixels
                            while px < w and pixels[px, py][3] > 128:
                                px += 1
                            x_end = px # Exclusive bound
                            
                            # Map to font coordinates
                            cell_y = py + bx[1]
                            y_top = ascent - cell_y * scale
                            y_bot = ascent - (cell_y + 1) * scale
                            
                            x_left = x_start * scale
                            x_right = x_end * scale
                            
                            # Draw clockwise: bot-left, top-left, top-right, bot-right
                            pen.moveTo((x_left, y_bot))
                            pen.lineTo((x_left, y_top))
                            pen.lineTo((x_right, y_top))
                            pen.lineTo((x_right, y_bot))
                            pen.closePath()
                        else:
                            px += 1
                            
                glyphs[g_name] = pen.glyph()
                metrics[g_name] = ((w + 1) * scale, 0)
                
            # 3. Setup Tables
            fb.setupGlyphOrder(glyph_order)
            fb.setupCharacterMap(cmap)
            fb.setupGlyf(glyphs)
            fb.setupHorizontalMetrics(metrics)
            
            # Metadata and metrics headers
            fb.setupHorizontalHeader(ascent=ascent, descent=descent, lineGap=0)
            fb.setupHead(unitsPerEm=UPM)
            
            nameStrings = {
                'familyName': safe_name,
                'styleName': 'Regular',
                'uniqueFontIdentifier': f'Nazariev:{safe_name}:2024',
                'fullName': safe_name,
                'psName': f'{safe_name}-Regular',
                'version': 'Version 1.000',
            }
            fb.setupNameTable(nameStrings)
            
            # OS/2 is critical for Windows
            fb.setupOS2(
                sTypoAscender=ascent, 
                sTypoDescender=descent,
                usWinAscent=ascent,
                usWinDescent=abs(descent)
            )
            
            fb.setupPost() # Default post table
            
            fb.save(ttf_path)
            messagebox.showinfo("Success", f"TTF successfully exported to {save_dir}")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            messagebox.showerror("Export Error", f"An error occurred during TTF export:\n{str(e)}\n\n{error_details}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FontToolApp(root)
    root.mainloop()
