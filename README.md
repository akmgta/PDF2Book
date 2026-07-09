Markdown
# 📚 Infinite 4-Page Micro-Booklet Imposition Tool

Yeh ek professional Python tool hai jo kisi bhi normal **A4 Portrait PDF** (jaise Canva, InDesign, ya standard eBooks) ko automatic format karke **A4 Landscape 2-Up (Micro-Booklets)** mein convert kar deta hai. 

---

### 🎯 Yeh Kaise Kaam Karta Hai? (The Infinite 4-Page Signature Logic)

Yeh tool kisi fix page limit se bandha nahi hai. Iska mathematical loop **Infinite Pages** ki PDF ko bhi seamlessly process kar sakta hai. Chahe aapki PDF mein 4 panne hon, 61 hon, 500 hon, ya 5,000—yeh script poori kitab ko **4-4 pannon ke independent chunks** mein todkar unki micro-booklets banata chala jata hai.

**Har 4-Page ke independent block ka automatic sequence aisa hoga:**
* **Sheet 1 Front:** Left side -> Page 4 | Right side -> Page 1 (Cover)
* **Sheet 1 Back:** Left side -> Page 2 | Right side -> Page 3
* **Sheet 2 Front:** Left side -> Page 8 | Right side -> Page 5
* **Sheet 2 Back:** Left side -> Page 6 | Right side -> Page 7
* ... *(Aur yeh loop isi tarah aage infinite chalta rahega: 9-12, 13-16, 17-20...)*

#### ⚠️ Padded Pages (Agar Total Pages 4 se divide na hon):
Agar aapki PDF ke total pages 4 ke multiple nahi hain (jaise aapki kitnaab mein **61 pages** hain), toh tool bache hue aakhri slots ko balance karne ke liye **khali (Blank) pages** automatic array ke aakhri mein jod deta hai. Isse aapka layout kabhi kharab nahi hota aur har booklet apne aap mein complete banti hai.

---

## 🛠️ Key Features (Khas Khubiyan)

1. **Smart Hybrid Compression Engine:** Yeh tool automatically scan karta hai ki kaunsa panna heavy hai (jaise Canva templates ya vector-heavy cover photos). Un heavy pannon ko yeh **2.5x High-Resolution Image** mein badal kar flat kar deta hai taaki **Cover Photo gayab na ho**, aur normal text pannon ko **Native Vector** rakhta hai taaki output PDF ka size **700MB hone ke bajaye 2-5MB** rahe.
2. **Strict Sancha Fitting (`keep_proportion=False`):** Pannon ke purane invisible blank canvases aur margins ko ignore karke, content ko forcefully target box mein fit karta hai jisse text ekdum bhara-bhara aur crisp dikhta hai.
3. **Full Margins Control (via CLI):** Aap terminal se hi Gutter (center fold), Outer, Top, aur Bottom margins ko points mein control kar sakte hain.

---

## 🚀 Setup & Installation (Shuruat Kaise Karein)

### Step 1: Purane toote hue environment ko saaf karein (Optional)
Agar aapka purana `venv` launcher crash ho chuka hai, toh us folder par right-click karke use **Delete** kar dein ya terminal mein yeh command chalayein:
```bash
Remove-Item -Recurse -Force venv
Step 2: Fresh Virtual Environment banayein aur active karein
Bash
# Naya environment banane ke liye
python -m venv venv

# Windows PowerShell mein activate karne ke liye
.\venv\Scripts\Activate.ps1
(Activation ke baad aapke terminal ke aage green rang mein (venv) likha hua dikhega).

Step 3: Requirements install karein
Hamari requirements.txt file ka use karke direct library install karne ke liye yeh command chalayein:

Bash
pip install -r requirements.txt
💻 Kaise Chalayein? (Usage)
1. Simple Run (Default Settings)
Apni asli PDF file (jaise aapki_kitab.pdf) ko isi project folder ke andar rakhein aur terminal mein chalayein:

Bash
python booklet_impose1.py aapki_kitab.pdf
Yeh command output/ naam ka ek naya folder banayegi aur uske andar do naye files generate karegi:

aapki_kitab_fronts.pdf (Saare aage ke panne)

aapki_kitab_backs.pdf (Saare piche ke panne)

2. Advance Run (Custom Margins ke sath)
Agar aapko binding ke liye center ka gap (Gutter) badhana hai ya edges ka margin change karna hai:

Bash
python booklet_impose1.py aapki_kitab.pdf --gutter 40 --outer 15 --top 10 --bottom 10
(Note: Margins ki value Points mein honi chahiye, jahan 1 inch = 72 points aur 0.5 inch = 36 points hota hai).

🖨️ Printing & Binding Instructions (Print Kaise Nikalein)
Agar aapke paas Single-Sided Printer (Manual Duplex) hai, toh perfect binding ke liye in steps ko follow karein:

Print Fronts First: Pehle output/aapki_kitab_fronts.pdf ko open karein aur uske saare panna print nikaal lein.

Flip the Stack: Nikle hue pannon ke bundle ko bina aage-piche kiye, Short-Edge (Choti Karwat) ki taraf se palti (flip) karke wapas printer ki tray mein daal dein.

Print Backs: Ab output/aapki_kitab_backs.pdf ko open karke print command de dein.

Fold & Staple: Ab har ek sheet ko beech se fold (mod) lijiye. Har ek sheet apne aap mein ek complete 4 pannon ki choti kitab hogi. Aap unhe center se fold karke staple kar sakte hain!

📁 Project Structure (Folder Files Layout)
Plaintext
Booklet Cloude/
├── venv/                   # Active and isolated Python packages
├── output/                 # Processed Front/Back PDFs yahan aayenge
├── booklet_impose1.py      # Main Python implementation script
├── requirements.txt        # Project dependencies (PyMuPDF version lock)
└── README.md               # Yeh documentation guide file
💡 Tip: Agar aapka printer pages ko ulta nikaalta hai, toh back side print karte waqt Adobe Reader mein "Print in Reverse Order" ka option check kar sakte hain.