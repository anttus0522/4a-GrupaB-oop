import tkinter as tk
import csv

class Kontakt:
    def __init__(self, ime, email, telefon):
        self.ime = ime
        self.email = email
        self.telefon = telefon

    def __str__(self):
        return f"{self.ime} - {self.email} {self.telefon}"

class ImenikApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Imenik kontakata")
        self.root.geometry("500x400")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        unos_frame = tk.Frame(self.root, padx=10, pady=10)
        unos_frame.grid(row=0, column=0, sticky="EW")

        prikaz_frame = tk.Frame(self.root, padx=10, pady=10)
        prikaz_frame.grid(row=1, column=0, sticky="NSEW")

        prikaz_frame.columnconfigure(0, weight=1)
        prikaz_frame.rowconfigure(0, weight=1)

        gumbi_frame = tk.Frame(self.root, padx=10, pady=10)
        gumbi_frame.grid(row=2, column=0, sticky="EW")

        tk.Label(unos_frame, text="Ime i prezime:").grid(row=0, column=0, sticky="W")
        self.ime_entry = tk.Entry(unos_frame)
        self.ime_entry.grid(row=0, column=1, padx=5, pady=5, sticky="EW")

        tk.Label(unos_frame, text="Email:").grid(row=1, column=0, sticky="W")
        self.email_entry = tk.Entry(unos_frame)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5, sticky="EW")

        tk.Label(unos_frame, text="Telefon:").grid(row=2, column=0, sticky="W")
        self.telefon_entry = tk.Entry(unos_frame)
        self.telefon_entry.grid(row=2, column=1, padx=5, pady=5, sticky="EW")

        tk.Button(unos_frame, text="Dodaj kontakt", command=self.dodaj_kontakt).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        self.listbox = tk.Listbox(prikaz_frame)
        self.listbox.grid(row=0, column=0, sticky="NSEW")

        scrollbar = tk.Scrollbar(prikaz_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.listbox.config(yscrollcommand=scrollbar.set)

        tk.Button(gumbi_frame, text="Spremi kontakte", command=self.spremi_kontakte).grid(
            row=0, column=0, padx=5, pady=5
        )
        tk.Button(gumbi_frame, text="Učitaj kontakte", command=self.ucitaj_kontakte).grid(
            row=0, column=1, padx=5, pady=5
        )

        self.kontakti = []

        self.ucitaj_kontakte()

    def dodaj_kontakt(self):
        ime = self.ime_entry.get().strip()
        email = self.email_entry.get().strip()
        telefon = self.telefon_entry.get().strip()

        if not ime or not email or not telefon:
            return

        kontakt = Kontakt(ime, email, telefon)
        self.kontakti.append(kontakt)
        self.osvjezi_prikaz()

        self.ime_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.telefon_entry.delete(0, tk.END)

    def osvjezi_prikaz(self):
        self.listbox.delete(0, tk.END)
        for kontakt in self.kontakti:
            self.listbox.insert(tk.END, kontakt)

    def spremi_kontakte(self):
        with open("kontakti.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for kontakt in self.kontakti:
                writer.writerow([kontakt.ime, kontakt.email, kontakt.telefon])

    def ucitaj_kontakte(self):
        try:
            with open("kontakti.csv", "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                self.kontakti = [Kontakt(ime, email, telefon) for ime, email, telefon in reader]
                self.osvjezi_prikaz()
        except FileNotFoundError:
            self.kontakti = []


if __name__ == "__main__":
    root = tk.Tk()
    app = ImenikApp(root)
    root.mainloop()

