import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
import os

# modeli
class Recept:
    def __init__(self, naziv, sastojci, upute, tezina="Srednje"):
        self.naziv = naziv or ""
        self.sastojci = sastojci or ""
        self.upute = upute or ""
        self.omiljen = False
        self.tezina = tezina or "Srednje"

    def tip(self):
        return "Recept"

    def __str__(self):
        oznaka = "\u2764\uFE0F" if self.omiljen else ""
        return f"{self.naziv} {oznaka}"

class SlaniRecept(Recept):
    def __init__(self, naziv, sastojci, upute, kuhinja, tezina="Srednje"):
        super().__init__(naziv, sastojci, upute, tezina)
        self.kuhinja = kuhinja or ""

    def tip(self):
        return "Slani"

class SlatkiRecept(Recept):
    def __init__(self, naziv, sastojci, upute, vrijeme, tezina="Srednje"):
        super().__init__(naziv, sastojci, upute, tezina)
        self.vrijeme = vrijeme or ""

    def tip(self):
        return "Slatki"

# funkcije i glavna baza
class KuharicaBaza:
    def __init__(self):
        self.recepti = []

    def dodaj(self, recept):
        self.recepti.append(recept)

    def obrisi(self, recept):
        if recept in self.recepti:
            self.recepti.remove(recept)

    def filtriraj(self, po_sastojku="", tip="Svi", omiljeni=False):
        rezultat = []
        q = (po_sastojku or "").lower().strip()
        for r in self.recepti:
            if q and q not in (r.sastojci or "").lower() and q not in (r.naziv or "").lower():
                continue
            if tip != "Svi" and r.tip() != tip:
                continue
            if omiljeni and not r.omiljen:
                continue
            rezultat.append(r)
        return rezultat

    def spremi_xml(self, datoteka):
        root = ET.Element("Recepti")
        for r in self.recepti:
            if isinstance(r, SlaniRecept):
                el = ET.SubElement(root, "SlaniRecept")
                ET.SubElement(el, "Kuhinja").text = r.kuhinja
            elif isinstance(r, SlatkiRecept):
                el = ET.SubElement(root, "SlatkiRecept")
                ET.SubElement(el, "Vrijeme").text = r.vrijeme
            else:
                el = ET.SubElement(root, "Recept")
            ET.SubElement(el, "Naziv").text = r.naziv
            ET.SubElement(el, "Sastojci").text = r.sastojci
            ET.SubElement(el, "Upute").text = r.upute
            ET.SubElement(el, "Omiljen").text = "True" if r.omiljen else "False"
            ET.SubElement(el, "Tezina").text = r.tezina
        ET.ElementTree(root).write(datoteka, encoding="utf-8", xml_declaration=True)

    def ucitaj_xml(self, datoteka):
        if not os.path.exists(datoteka):
            return
        tree = ET.parse(datoteka)
        root = tree.getroot()
        self.recepti.clear()

        for el in root:
            def txt(tag):
                node = el.find(tag)
                return node.text if node is not None and node.text is not None else ""

            naziv = txt("Naziv")
            sastojci = txt("Sastojci")
            upute = txt("Upute")
            tezina = txt("Tezina") or "Srednje"  
            omiljen_txt = txt("Omiljen").strip().lower()
            omiljen = omiljen_txt in ("true", "1", "yes")

            if el.tag == "SlaniRecept":
                kuhinja = txt("Kuhinja")
                r = SlaniRecept(naziv, sastojci, upute, kuhinja, tezina)
            elif el.tag == "SlatkiRecept":
                vrijeme = txt("Vrijeme")
                r = SlatkiRecept(naziv, sastojci, upute, vrijeme, tezina)
            else:
                r = Recept(naziv, sastojci, upute, tezina)

            r.omiljen = omiljen
            self.recepti.append(r)

#aplikacija
class KuharicaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kuharica")
        self.root.geometry("750x650")
        self.root.configure(bg='orange')

        ttk.Style().theme_use("classic")

        self.baza = KuharicaBaza()

        self.meni()
        self.widgeti()
        self.update_listbox()

    def meni(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Spremi", command=self.spremlji)
        file_menu.add_command(label="Učitaj", command=self.ucitaj)
        file_menu.add_separator()
        file_menu.add_command(label="Izlaz", command=self.root.quit)
        menu.add_cascade(label="Datoteka", menu=file_menu)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="O aplikaciji", command=self.o_aplikaciji)
        menu.add_cascade(label="Pomoć", menu=help_menu)

    def widgeti(self):
        self.logo = tk.PhotoImage(file="logo.png")
        self.logo = self.logo.subsample(4, 4)
        tk.Label(self.root, image=self.logo, bg="orange").pack(pady=5)
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(pady=10)

        ttk.Label(filter_frame, text="Pretraga po sastojku:").grid(row=0, column=0)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.update_listbox())
        ttk.Entry(filter_frame, textvariable=self.search_var, width=30).grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Vrsta:").grid(row=0, column=2)
        self.tip_var = tk.StringVar(value="Svi")
        ttk.Combobox(filter_frame, textvariable=self.tip_var, values=["Svi", "Slani", "Slatki"], width=10).grid(row=0, column=3)
        ttk.Button(filter_frame, text="Filtriraj", command=self.update_listbox).grid(row=0, column=4, padx=5)

        self.omiljeni_var = tk.BooleanVar()
        ttk.Checkbutton(filter_frame, text="Samo omiljeni", variable=self.omiljeni_var, command=self.update_listbox).grid(row=0, column=5)

        self.listbox = tk.Listbox(self.root, width=90, height=18)
        self.listbox.pack(padx=10, pady=10)
        self.listbox.bind("<Double-Button-1>", self.prikazi_detalje)

        gumbi = ttk.Frame(self.root)
        gumbi.pack()

        ttk.Button(gumbi, text="Dodaj Slani", command=self.dodaj_slani).grid(row=0, column=0, padx=5)
        ttk.Button(gumbi, text="Dodaj Slatki", command=self.dodaj_slatki).grid(row=0, column=1, padx=5)
        ttk.Button(gumbi, text="Uredi", command=self.uredi_recept).grid(row=0, column=2, padx=5)
        ttk.Button(gumbi, text="Obriši", command=self.obrisi_recept).grid(row=0, column=3, padx=5)
        ttk.Button(gumbi, text="Omiljen", command=self.toggle_omiljen).grid(row=0, column=4, padx=5)

        self.status_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.status_var).pack(side=tk.BOTTOM, fill=tk.X)

    def update_listbox(self, status=None):
        self.listbox.delete(0, tk.END)
        query = self.search_var.get()
        tip = self.tip_var.get()
        omiljeni = self.omiljeni_var.get()

        prikazani = self.baza.filtriraj(query, tip, omiljeni)
        for r in prikazani:
            self.listbox.insert(tk.END, str(r))
            index = self.listbox.size() - 1
            boja = {"Jednostavno": "lightgreen", "Složeno": "lightcoral"}.get(r.tezina, "white")
            try:
                self.listbox.itemconfig(index, {"bg": boja})
            except Exception:
                pass
        self.status_var.set(status if status else f"Ukupno recepata: {len(self.baza.recepti)}")

    def unos_recepta(self, tip, recept=None):
        win = tk.Toplevel(self.root)
        win.title("Unos recepta")
        win.geometry("400x400")

        tk.Label(win, text="Naziv:").pack()
        e_naziv = tk.Entry(win)
        e_naziv.pack(fill=tk.X)
        if recept:
            e_naziv.insert(0, recept.naziv)

        tk.Label(win, text="Sastojci:").pack()
        t_sastojci = tk.Text(win, height=5)
        t_sastojci.pack(fill=tk.X)
        if recept:
            t_sastojci.insert(tk.END, recept.sastojci)

        tk.Label(win, text="Upute:").pack()
        t_upute = tk.Text(win, height=5)
        t_upute.pack(fill=tk.X)
        if recept:
            t_upute.insert(tk.END, recept.upute)

        tk.Label(win, text="Težina:").pack()
        tezina = ttk.Combobox(win, values=["Jednostavno", "Srednje", "Složeno"])
        tezina.set(recept.tezina if recept else "Srednje")
        tezina.pack()

        extra_label = "Kuhinja:" if tip == "Slani" else "Vrijeme:"
        tk.Label(win, text=extra_label).pack()
        e_extra = tk.Entry(win)
        e_extra.pack(fill=tk.X)
        if recept:
            if isinstance(recept, SlaniRecept):
                e_extra.insert(0, recept.kuhinja)
            elif isinstance(recept, SlatkiRecept):
                e_extra.insert(0, recept.vrijeme)

        def spremi():
            naziv = e_naziv.get().strip()
            sastojci = t_sastojci.get("1.0", tk.END).strip()
            upute = t_upute.get("1.0", tk.END).strip()
            extra = e_extra.get().strip()
            tez = tezina.get() or "Srednje"
            if not naziv or not sastojci or not upute or not extra:
                messagebox.showwarning("Upozorenje", "Sva polja moraju biti popunjena!")
                return
            if tip == "Slani":
                novi = SlaniRecept(naziv, sastojci, upute, extra, tez)
            else:
                novi = SlatkiRecept(naziv, sastojci, upute, extra, tez)
            if recept:
                self.baza.obrisi(recept)
            self.baza.dodaj(novi)
            self.update_listbox(status=f"Recept '{naziv}' spremljen.")
            win.destroy()

        ttk.Button(win, text="Spremi", command=spremi).pack(pady=10)

    def dodaj_slani(self):
        self.unos_recepta("Slani")

    def dodaj_slatki(self):
        self.unos_recepta("Slatki")

    def uredi_recept(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberite recept za uređivanje.")
            return
        prikaz = self.listbox.get(sel[0])
        for r in self.baza.recepti:
            if str(r) == prikaz:
                self.unos_recepta(r.tip(), r)
                break

    def obrisi_recept(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberite recept za brisanje.")
            return
        prikaz = self.listbox.get(sel[0])
        for r in self.baza.recepti:
            if str(r) == prikaz:
                if messagebox.askyesno("Brisanje", f"Obrisati recept '{r.naziv}'?"):
                    self.baza.obrisi(r)
                    self.update_listbox(status=f"Recept '{r.naziv}' obrisan.")
                break

    def toggle_omiljen(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberite recept.")
            return
        prikaz = self.listbox.get(sel[0])
        for r in self.baza.recepti:
            if str(r) == prikaz:
                r.omiljen = not r.omiljen
                self.update_listbox(status=f"Promijenjena omiljenost: {r.naziv}")
                break

    def prikazi_detalje(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        prikaz = self.listbox.get(sel[0])
        for r in self.baza.recepti:
            if str(r) == prikaz:
                tekst = f"Naziv: {r.naziv}\nSastojci: {r.sastojci}\nUpute: {r.upute}\nTežina: {r.tezina}"
                if isinstance(r, SlaniRecept):
                    tekst += f"\nKuhinja: {r.kuhinja}"
                else:
                    tekst += f"\nVrijeme: {r.vrijeme}"
                tekst += f"\nOmiljen: {'Da' if r.omiljen else 'Ne'}"
                messagebox.showinfo("Detalji recepta", tekst)
                break

    # spremi
    def spremlji(self):
        f = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML datoteke", "*.xml")])
        if not f:
            return
        try:
            self.baza.spremi_xml(f)
            self.update_listbox(status="Podaci spremljeni.")
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def ucitaj(self):
        f = filedialog.askopenfilename(filetypes=[("XML datoteke", "*.xml")])
        if not f:
            return
        try:
            self.baza.ucitaj_xml(f)
            self.update_listbox(status="Podaci učitani.")
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def o_aplikaciji(self):
        win = tk.Toplevel(self.root)
        win.title("O aplikaciji")
        logo = tk.PhotoImage(file="logo.png")
        logo = logo.subsample(5,5)
        lbl = tk.Label(win, image=logo)
        lbl.image = logo
        lbl.pack()
        tk.Label(win, text="Kuharica 2.0\nAutor: Antonia Tušćan").pack()
        

#startapp
if __name__ == "__main__":
    root = tk.Tk()
    app = KuharicaApp(root)
    root.mainloop()
