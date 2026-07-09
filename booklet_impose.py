#!/usr/bin/env python3
"""
Booklet Imposition: A4 Landscape → 2-up A5 pages (2 PDFs: fronts + backs)
- HAR 4 PAGE APNE AAP MEIN EK STANDALONE BOOKLET CHUNK BANAYENGE.
- HYBRID COMPRESSION ENGINE: Canva/Heavy covers ko flat image banayega, normal text ko vectors rakhega.
"""

import sys
import math
from pathlib import Path
import fitz  # PyMuPDF library jo pypdf se 10x fast aur accurate layout fit karti hai

# =========================================================================
# CONFIGURATION — Default Margins (Points mein: 1 inch = 72 points)
# =========================================================================
A4_W, A4_H = 841.89, 595.28          # Standard A4 Landscape ki width aur height points mein
HALF_W = A4_W / 2                     # A4 ka adha hissa (420.945 points) jo hamara A5 width zone hai
A5_H = A4_H                           # Landscape mein height wahi rahegi jo A4 ki height hai

GUTTER_MARGIN   = 36   # Center fold (binding) ki total khali jagah (36 pt = 0.5 inch)
OUTER_MARGIN    = 12   # Page ke ekdum bahar wale left/right edges ka safe gap
TOP_MARGIN      = 12   # Page ke upar ka safe gap (Header ke liye)
BOTTOM_MARGIN   = 12   # Page ke neeche ka safe gap (Footer/Page number ke liye)

# PRINT_W: Asli chaudai jisme text chapna chahiye (Adha A4 - Gutter Margin - Outer Margin)
PRINT_W = HALF_W - GUTTER_MARGIN - OUTER_MARGIN
# PRINT_H: Asli lambai jisme text chapna chahiye (Total Height - Top Margin - Bottom Margin)
PRINT_H = A5_H - TOP_MARGIN - BOTTOM_MARGIN


# =========================================================================
# CORE FUNCTIONS
# =========================================================================

def place_page(src_doc: fitz.Document, src_page_idx: int, imposed_page: fitz.Page, x_offset: float, is_left: bool):
    """
    Yeh function ek single source page ko uthakar, naye A4 canvas par sahi coordinates 
    aur safety margins ke sath 'squeeze/fit' karke chipkata hai.
    """
    # Gutter ko dono pannon (Left aur Right) mein barabar baantne ke liye 2 se divide kiya
    gutter_shift = GUTTER_MARGIN / 2
    
    # Agar panna LEFT side baith raha hai toh use center fold se door LEFT ki taraf khiskayenge (- shift)
    # Agar panna RIGHT side baith raha hai toh use center fold se door RIGHT ki taraf khiskayenge (+ shift)
    h_shift = -gutter_shift if is_left else gutter_shift

    # --- COORDINATE MAPPING (Target Box Structure) ---
    # x0, y0: Sanche (Bounding Box) ka top-left corner jahan se printing shuru hogi
    x0 = x_offset + h_shift
    y0 = TOP_MARGIN
    # x1, y1: Sanche ka bottom-right corner jahan par printing khatam hogi
    x1 = x0 + PRINT_W
    y1 = y0 + PRINT_H
    
    # PyMuPDF ka Rect object banaya jo is fixed dabbe ko lock kar deta hai
    target_rect = fitz.Rect(x0, y0, x1, y1)
    
    # Source document se us particular page ka reference nikaala
    src_page = src_doc[src_page_idx]

    # --- SMART AUTO-DETECTION ENGINE (700MB Size aur Missing Cover Dono Ka Ilaaj) ---
    # Page ke andar ka text, drawings (shapes/vectors), aur image counts ko scan karte hain
    text_length = len(src_page.get_text().strip())
    drawings_count = len(src_page.get_drawings())
    images_count = len(src_page.get_images())

    # CONDITIONAL CHECK: Agar ye pehla panna (Cover) hai, ya ispe text bohot kam aur heavy graphics hain
    if src_page_idx == 0 or (text_length < 200 and (drawings_count > 30 or images_count > 0)):
        # RASTERIZATION MODE: Complex Canva layers/hidden masks ka photo snapshot le lete hain.
        # Matrix(2.5, 2.5) yani 2.5x zoom, jo print out ke liye ekdum crisp hai aur size bhi control rakhta hai.
        pix = src_page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5))
        # Snapshot ko target box ke andar force-fit stamp kar diya (Cover gayab nahi hoga)
        imposed_page.insert_image(target_rect, pixmap=pix)
    else:
        # VECTOR MODE: Normal text pages ko bina chitre (image) mein badle direct native code se pass karte hain.
        # keep_proportion=False lagane se text strict boundaries se chipak jata hai aur file size KB/MBs mein rehta hai.
        imposed_page.show_pdf_page(target_rect, src_doc, src_page_idx, keep_proportion=False)


def build_side(src_doc: fitz.Document, out_doc: fitz.Document, left_idx: int, right_idx: int, total_pages: int):
    """
    Yeh function ek single A4 Landscape sheet taiyar karta hai jiske andar 
    ek LEFT side ka panna hota hai aur ek RIGHT side ka panna hota hai.
    """
    # Naye target document mein ek fresh blank A4 Landscape page create kiya
    pg = out_doc.new_page(width=A4_W, height=A4_H)
    
    # Left panna hamesha outer margin se shuru hoga (ekdum shuruat se)
    left_x = OUTER_MARGIN
    # Right panna hamesha adhi width, center gutter aur outer margin ke baad shuru hoga
    right_x = HALF_W + GUTTER_MARGIN + OUTER_MARGIN

    # Validation: Agar LEFT index valid hai (total pages se kam hai), toh use left quadrant par place karo
    if left_idx < total_pages:
        place_page(src_doc, left_idx, pg, left_x, is_left=True)
        
    # Validation: Agar RIGHT index valid hai, toh use right quadrant par place karo
    if right_idx < total_pages:
        place_page(src_doc, right_idx, pg, right_x, is_left=False)
        
    return pg


def impose_booklet(src_path: Path, out_dir: Path,
                   gutter=GUTTER_MARGIN, outer=OUTER_MARGIN,
                   top=TOP_MARGIN, bottom=BOTTOM_MARGIN):
    """
    Main Business Logic: Input file ko read karna, use 4-4 ke groups mein process karna,
    aur Front/Back PDFs ko optimize karke save karna.
    """
    # CLI user agar naye margins pass karega toh unhe global variables mein update kar rahe hain
    global GUTTER_MARGIN, OUTER_MARGIN, TOP_MARGIN, BOTTOM_MARGIN, PRINT_W, PRINT_H
    GUTTER_MARGIN, OUTER_MARGIN, TOP_MARGIN, BOTTOM_MARGIN = gutter, outer, top, bottom
    PRINT_W = HALF_W - GUTTER_MARGIN - OUTER_MARGIN
    PRINT_H = A5_H - TOP_MARGIN - BOTTOM_MARGIN

    # PyMuPDF engine se source PDF file ko back-end mein open kiya
    src_doc = fitz.open(str(src_path))
    total = len(src_doc) # Total pannon ki ginti (Maan lijiye 61)
    print(f"Source: {total} pages")

    # Front aur Back ke liye alag-alag khali PDF containers banaye jisme final pages add honge
    front_writer = fitz.open()
    back_writer = fitz.open()

    # =========================================================================
    # INDEPENDENT 4-PAGE CHUNK LOOP (Step=4 yaani har baar agle 4 pannon par jump)
    # =========================================================================
    for base in range(0, total, 4):
        
        # --- FRONT SIDE COMBINATION ---
        # Har 4-page ke standalone signature mein:
        # Left mein aata hai 4th page (index+3) aur Right mein aata hai 1st page (index+0)
        p_front_left = base + 3
        p_front_right = base
        # In dono ko ek sheet par saja kar front_writer ke andar joda
        build_side(src_doc, front_writer, p_front_left, p_front_right, total)

        # --- BACK SIDE COMBINATION ---
        # Usi block ke piche wale side par:
        # Left mein aata hai 2nd page (index+1) aur Right mein aata hai 3rd page (index+2)
        p_back_left = base + 1
        p_back_right = base + 2
        # In dono ko ek sheet par saja kar back_writer ke andar joda
        build_side(src_doc, back_writer, p_back_left, p_back_right, total)

    # Output directory (folder) agar pehle se nahi bana toh use system mein create kiya
    out_dir.mkdir(parents=True, exist_ok=True)
    # Dono output files ke absolute safe paths generate kiye
    front_path = out_dir / f"{src_path.stem}_fronts.pdf"
    back_path = out_dir / f"{src_path.stem}_backs.pdf"

    # --- VECTOR COMPRESSION & SAVE ---
    # garbage=4: Poore PDF structure mein jitne bhi duplicate fonts ya images hain unhe delete karta hai.
    # deflate=True: Text aur internal coordinates ko binary level par compress karke size chota rakhta hai.
    front_writer.save(str(front_path), garbage=4, deflate=True)
    back_writer.save(str(back_path), garbage=4, deflate=True)

    print(f"✅ Fronts: {front_path}")
    print(f"✅ Backs:  {back_path}")
    print(f"   Mode: Independent 4-page standalone micro-booklets.")
    return front_path, back_path


# =========================================================================
# CLI INTERFACE — Command Line Se Scripts Ko Arguments Pass Karne Ke Liye
# =========================================================================
if __name__ == "__main__":
    import argparse
    # Parser object initialize kiya jo terminal input ko handle karega
    p = argparse.ArgumentParser(description="Independent 4-Page Booklet Imposition")
    
    # Argument Definitions (Kaunsa variable kya kaam karega aur default value kya hogi)
    p.add_argument("input", help="Input PDF path")
    p.add_argument("output_dir", nargs="?", default="output", help="Output directory")
    p.add_argument("--gutter", type=float, default=GUTTER_MARGIN, help="Inner/gutter margin (pts)")
    p.add_argument("--outer", type=float, default=OUTER_MARGIN, help="Outer margin (pts)")
    p.add_argument("--top", type=float, default=TOP_MARGIN, help="Top margin (pts)")
    p.add_argument("--bottom", type=float, default=BOTTOM_MARGIN, help="Bottom margin (pts)")
    args = p.parse_args() # User ke diye inputs ko parse/extract kiya

    # Function ko saare parameters ke sath fire kar diya
    impose_booklet(
        Path(args.input),
        Path(args.output_dir),
        gutter=args.gutter, outer=args.outer, top=args.top, bottom=args.bottom
    )