import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import xml.etree.ElementTree as ET
import os

class Recept:
    def __init__(self, naziv, sastojci, upute):
        self.naziv = naziv
        self.sastojci = sastojci
        self.upute = upute
        self.omiljen = False

    def tip(self):
        return "Recept"

    def __str__(self):
        oznaka = "\u2764\uFE0F" if self.omiljen else ""
        return f"{self.naziv} {oznaka}"

class SlaniRecept(Recept):
    def __init__(self, naziv, sastojci, upute, kuhinja):
        super().__init__(naziv, sastojci, upute)
        self.kuhinja = kuhinja

    def tip(self):
        return "Slano"

class SlatkiRecept(Recept):
    def __init__(self, naziv, sastojci, upute, vrijeme):
        super().__init__(naziv, sastojci, upute)
        self.vrijeme = vrijeme

    def tip(self):
        return "Slatko"


class KuharicaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kuharica")
        self.root.config(bg="#FFA500")

        self.recepti = []

        self.create_menu()
        self.create_widgets()
        self.update_listboxes(status="Aplikacija pokrenuta.")

    
    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Spremi", command=self.spremi)
        file_menu.add_command(label="Učitaj", command=self.ucitaj)
        file_menu.add_separator()
        file_menu.add_command(label="Izlaz", command=self.root.quit)
        menu.add_cascade(label="Datoteka", menu=file_menu)

        
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="O aplikaciji", command=self.o_aplikaciji)
        menu.add_cascade(label="Pomoć", menu=help_menu)

    
    def create_widgets(self):
        # Logo
        logo_text = """_ __ _ _  _ _  ___  ___  _  ___  ___  
| / /| | || | || . || . \\| ||  _>| . |
|  \\ | ' ||   ||   ||   /| || <__|   |
|_\\_\\`___'|_|_||_|_||_\\_\\|_|`___/|_|_|"""
        tk.Label(self.root, text=logo_text, font=("Courier", 10), bg="#FFA500").pack()

        
        tk.Label(self.root, text="Pretraga po sastojku:", bg="#FFA500").pack(pady=(10,0))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.update_listboxes(status="Pretraga ažurirana."))
        tk.Entry(self.root, textvariable=self.search_var).pack()

       
        frame_listbox = tk.Frame(self.root, bg="#FFA500")
        frame_listbox.pack(pady=10)

        #Slani recepti
        slani_frame = tk.Frame(frame_listbox, bg="#FFA500")
        slani_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(slani_frame, text="Slani recepti:", bg="#FFA500").pack()
        self.listbox_slano = tk.Listbox(slani_frame, width=40, height=15)
        self.listbox_slano.pack()
        self.listbox_slano.bind("<Double-Button-1>", self.prikazi_detalje_slano)

        #Slatki recepti
        slatki_frame = tk.Frame(frame_listbox, bg="#FFA500")
        slatki_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(slatki_frame, text="Slatki recepti:", bg="#FFA500").pack()
        self.listbox_slatko = tk.Listbox(slatki_frame, width=40, height=15)
        self.listbox_slatko.pack()
        self.listbox_slatko.bind("<Double-Button-1>", self.prikazi_detalje_slatko)

        
        kontrola_frame = tk.Frame(self.root, bg="#FFA500")
        kontrola_frame.pack(pady=10)
        tk.Button(kontrola_frame, text="Dodaj Slani Recept", command=self.dodaj_slani).grid(row=0, column=0, padx=5, pady=2)
        tk.Button(kontrola_frame, text="Dodaj Slatki Recept", command=self.dodaj_slatki).grid(row=0, column=1, padx=5, pady=2)
        tk.Button(kontrola_frame, text="Označi/Skini omiljenost (Slano)", command=self.toggle_omiljen_slano).grid(row=1, column=0, padx=5, pady=2)
        tk.Button(kontrola_frame, text="Označi/Skini omiljenost (Slatko)", command=self.toggle_omiljen_slatko).grid(row=1, column=1, padx=5, pady=2)

        
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.root, textvariable=self.status_var, bg="#FFA500", anchor='w')
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

    
    def update_listboxes(self, status=None):
        query = self.search_var.get().lower()

        self.listbox_slano.delete(0, tk.END)
        self.listbox_slatko.delete(0, tk.END)
        for r in self.recepti:
            if query in r.sastojci.lower():
                if isinstance(r, SlaniRecept):
                    self.listbox_slano.insert(tk.END, str(r))
                else:
                    self.listbox_slatko.insert(tk.END, str(r))
        self.status_var.set(status if status else f"Broj recepata: {len(self.recepti)}")

    
    def dodaj_slani(self):
        try:
            naziv = simpledialog.askstring("Naziv", "Unesite naziv recepta:")
            sastojci = simpledialog.askstring("Sastojci", "Unesite sastojke:")
            upute = simpledialog.askstring("Upute", "Unesite upute:")
            kuhinja = simpledialog.askstring("Kuhinja", "Unesite kuhinju:")
            if None in [naziv, sastojci, upute, kuhinja]:
                return
            r = SlaniRecept(naziv, sastojci, upute, kuhinja)
            self.recepti.append(r)
            self.update_listboxes(status=f"Dodan slani recept: {naziv}")
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def dodaj_slatki(self):
        try:
            naziv = simpledialog.askstring("Naziv", "Unesite naziv recepta:")
            sastojci = simpledialog.askstring("Sastojci", "Unesite sastojke:")
            upute = simpledialog.askstring("Upute", "Unesite upute:")
            vrijeme = simpledialog.askstring("Vrijeme", "Unesite vrijeme hlađenja/pečenja:")
            if None in [naziv, sastojci, upute, vrijeme]:
                return
            r = SlatkiRecept(naziv, sastojci, upute, vrijeme)
            self.recepti.append(r)
            self.update_listboxes(status=f"Dodan slatki recept: {naziv}")
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    
    def toggle_omiljen_slano(self):
        try:
            idx = self.listbox_slano.curselection()[0]
            prikaz = self.listbox_slano.get(idx)
            for r in self.recepti:
                if str(r) == prikaz and isinstance(r, SlaniRecept):
                    r.omiljen = not r.omiljen
                    self.update_listboxes(status=f"Omiljenost promijenjena: {r.naziv}")
                    break
        except IndexError:
            messagebox.showwarning("Upozorenje", "Odaberite recept.")

    def toggle_omiljen_slatko(self):
        try:
            idx = self.listbox_slatko.curselection()[0]
            prikaz = self.listbox_slatko.get(idx)
            for r in self.recepti:
                if str(r) == prikaz and isinstance(r, SlatkiRecept):
                    r.omiljen = not r.omiljen
                    self.update_listboxes(status=f"Omiljenost promijenjena: {r.naziv}")
                    break
        except IndexError:
            messagebox.showwarning("Upozorenje", "Odaberite recept.")

    
    def prikazi_detalje_slano(self, event):
        self.prikazi_detalje(self.listbox_slano, SlaniRecept)

    def prikazi_detalje_slatko(self, event):
        self.prikazi_detalje(self.listbox_slatko, SlatkiRecept)

    def prikazi_detalje(self, listbox, klasa):
        try:
            idx = listbox.curselection()[0]
            prikaz = listbox.get(idx)
            for r in self.recepti:
                if str(r) == prikaz and isinstance(r, klasa):
                    info = f"Naziv: {r.naziv}\nSastojci: {r.sastojci}\nUpute: {r.upute}"
                    if isinstance(r, SlaniRecept):
                        info += f"\nKuhinja: {r.kuhinja}"
                    else:
                        info += f"\nVrijeme hlađenja/pečenja: {r.vrijeme}"
                    messagebox.showinfo("Detalji recepta", info)
                    break
        except IndexError:
            pass

    #O aplikaciji
    def o_aplikaciji(self):
        info = """Kuharica 1.0
Autor: Antonia Tušćan
Logo:
_ __ _ _  _ _  ___  ___  _  ___  ___  
| / /| | || | || . || . \\| ||  _>| . |
|  \\ | ' ||   ||   ||   /| || <__|   |
|_\\_\\`___'|_|_||_|_||_\\_\\|_|`___/|_|_|"""
        messagebox.showinfo("O aplikaciji", info)

    
    def spremi(self):
        try:
            file = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files","*.xml")])
            if not file:
                return
            root = ET.Element("Recepti")
            for r in self.recepti:
                if isinstance(r, SlaniRecept):
                    el = ET.SubElement(root, "SlaniRecept")
                    ET.SubElement(el, "Kuhinja").text = r.kuhinja
                else:
                    el = ET.SubElement(root, "SlatkiRecept")
                    ET.SubElement(el, "Vrijeme").text = r.vrijeme
                ET.SubElement(el, "Naziv").text = r.naziv
                ET.SubElement(el, "Sastojci").text = r.sastojci
                ET.SubElement(el, "Upute").text = r.upute
                ET.SubElement(el, "Omiljen").text = str(r.omiljen)
            tree = ET.ElementTree(root)
            tree.write(file, encoding="utf-8", xml_declaration=True)
            self.update_listboxes(status="Katalog spremljen.")
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def ucitaj(self):
        try:
            file = filedialog.askopenfilename(filetypes=[("XML files","*.xml")])
            if not file or not os.path.exists(file):
                return
            tree = ET.parse(file)
            root = tree.getroot()
            self.recepti.clear()
            for el in root:
                naziv = el.find("Naziv").text
                sastojci = el.find("Sastojci").text
                upute = el.find("Upute").text
                omiljen = el.find("Omiljen").text == "True"
                if el.tag == "SlaniRecept":
                    kuhinja = el.find("Kuhinja").text
                    r = SlaniRecept(naziv, sastojci, upute, kuhinja)
                else:
                    vrijeme = el.find("Vrijeme").text
                    r = SlatkiRecept(naziv, sastojci, upute, vrijeme)
                r.omiljen = omiljen
                self.recepti.append(r)
            self.update_listboxes(status="Katalog učitan.")
        except Exception as e:
            messagebox.showerror("Greška", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = KuharicaApp(root)
    root.mainloop()
