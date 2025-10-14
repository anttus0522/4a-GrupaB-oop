import tkinter as tk

class Ucenik:
    def __init__(self, ime, prezime, razred): 
        self.ime = ime
        self.prezime = prezime
        self.razred = razred

    def __str__(self): 
        return f"{self.prezime} {self.ime} {self.razred}"

ucenik1 = Ucenik('Pero', 'Perić', '4.a')
print(ucenik1)

class EvidencijaApp:
    def __init__(self, root): 
        self.root = root

        self.root.title("Evidencija učenika")
        self.root.geometry("500x400")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        unos_frame = tk.Frame(self.root, padx=10, pady=10)
        unos_frame.grid(row=0, column=0, sticky="EW")
        unos_frame.config(bg="red")

        prikaz_frame = tk.Frame(self.root, padx=10, pady=10)
        prikaz_frame.grid(row=1, column=0, sticky="NSEW") 

        prikaz_frame.columnconfigure(0, weight=1)
        prikaz_frame.rowconfigure(0, weight=1)

        tk.Label(unos_frame, text="Ime:").grid(row=0, column=0, padx=5, pady=5, sticky="W")
        self.ime_entry = tk.Entry(unos_frame)
        self.ime_entry.grid(row=0, column=1, padx=5, pady=5, sticky="EW")

        tk.Label(unos_frame, text="Prezime:").grid(row=1, column=0, padx=5, pady=5, sticky="W")
        self.prezime_entry = tk.Entry(unos_frame)
        self.prezime_entry.grid(row=1, column=1, padx=5, pady=5, sticky="EW")

        tk.Label(unos_frame, text="Razred:").grid(row=2, column=0, padx=5, pady=5, sticky="W")
        self.razred_entry = tk.Entry(unos_frame)
        self.razred_entry.grid(row=2, column=1, padx=5, pady=5, sticky="EW")

        self.dodaj_gumb = tk.Button(unos_frame, text="Dodaj učenika", command=self.dodaj_ucenika)
        self.dodaj_gumb.grid(row=3, column=0, padx=5, pady=10)
        self.dodaj_gumb.config(bg="lightgreen")

        self.spremi_gumb = tk.Button(unos_frame, text="Spremi izmjene", command=self.spremi_izmjene)
        self.spremi_gumb.grid(row=3, column=1, padx=5, pady=10, sticky="W")
        self.spremi_gumb.config(bg="lightblue")


        self.listbox = tk.Listbox(prikaz_frame)
        self.listbox.grid(row=0, column=0, sticky="NSEW")


        scrollbar = tk.Scrollbar(prikaz_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Faza 3
        self.ucenici = []
        self.odabrani_ucenik_index = None


        self.listbox.bind("<<ListboxSelect>>", self.odaberi_ucenika)

    def dodaj_ucenika(self):
        ime = self.ime_entry.get()
        prezime = self.prezime_entry.get()
        razred = self.razred_entry.get()

        if not ime or not prezime or not razred:
            return  

        ucenik = Ucenik(ime, prezime, razred) 
        self.ucenici.append(ucenik)
        self.osvjezi_prikaz()

        self.ime_entry.delete(0, tk.END)
        self.prezime_entry.delete(0, tk.END)
        self.razred_entry.delete(0, tk.END)

    def osvjezi_prikaz(self):
        self.listbox.delete(0, tk.END)
        for ucenik in self.ucenici:
            self.listbox.insert(tk.END, ucenik)

    def odaberi_ucenika(self, event):
        odabrani_indeksi = self.listbox.curselection()
        if not odabrani_indeksi:
            return
        self.odabrani_ucenik_index = odabrani_indeksi[0]
        ucenik = self.ucenici[self.odabrani_ucenik_index]

        self.ime_entry.delete(0, tk.END)
        self.ime_entry.insert(0, ucenik.ime)

        self.prezime_entry.delete(0, tk.END)
        self.prezime_entry.insert(0, ucenik.prezime)

        self.razred_entry.delete(0, tk.END)
        self.razred_entry.insert(0, ucenik.razred)

    def spremi_izmjene(self):
        if self.odabrani_ucenik_index is None:
            return

        ime = self.ime_entry.get()
        prezime = self.prezime_entry.get()
        razred = self.razred_entry.get()

        ucenik = self.ucenici[self.odabrani_ucenik_index]
        ucenik.ime = ime
        ucenik.prezime = prezime
        ucenik.razred = razred

        self.osvjezi_prikaz()

        self.ime_entry.delete(0, tk.END)
        self.prezime_entry.delete(0, tk.END)
        self.razred_entry.delete(0, tk.END)

        self.odabrani_ucenik_index = None 

if __name__ == "__main__":
    root = tk.Tk()
    app = EvidencijaApp(root)
    root.mainloop()

        




        
