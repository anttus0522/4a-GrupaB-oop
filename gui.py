import tkinter as tk
from tkinter import messagebox
import requests

BASE_URL = "http://127.0.0.1:5000"


user_id = None
books = []
displayed_books = []
book_ids = []


BG = "#F6F1FF"
CARD = "#FFFFFF"
PRIMARY = "#8B5CF6"
ACCENT = "#F472B6"
TEXT = "#2E2E2E"
GOOD = "#16A34A"
READING = "#2563EB"
PLAN = "#F43F5E"
CARD_BORDER = "#D8B4FE"


FONT_TITLE = ("Segoe UI Semibold", 20)
FONT_SUBTITLE = ("Segoe UI", 12)
FONT_BODY = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)
FONT_MONO = ("Courier New", 12)


root = tk.Tk()
root.title("📚 BookTakeover")
root.geometry("900x750")
root.configure(bg=BG)


login_frame = tk.Frame(root, bg=CARD, padx=30, pady=30)
login_frame.pack(expand=True)

tk.Label(login_frame, text="📚 BookTakeover",
         font=("Segoe UI", 20, "bold"),
         bg=CARD).pack(pady=10)

entry = tk.Entry(login_frame, font=("Segoe UI", 12))
entry.pack(pady=10)


main_frame = tk.Frame(root, bg=BG)


sidebar = tk.Frame(main_frame, bg="#EDE7FF", width=200)
content = tk.Frame(main_frame, bg=BG)


header = tk.Label(content, text="""
╔══════════════════════╗
   📚 BookTakeover
╚══════════════════════╝
""", font=("Courier", 12), bg=BG)


search_var = tk.StringVar()
search_entry = tk.Entry(content, textvariable=search_var,
                        font=FONT_BODY, width=34, bd=2, relief="groove")

search_btn = tk.Button(content, text="Pretraži", bg=ACCENT, fg="white",
                       font=FONT_SUBTITLE, relief="flat", activebackground="#ec4899")


listbox = tk.Listbox(
    content,
    width=62,
    height=15,
    font=FONT_BODY,
    selectbackground=PRIMARY,
    bd=2,
    relief="sunken"
)


btn_frame = tk.Frame(content, bg=BG)

rate_btn = tk.Button(btn_frame, text="⭐ Ocijeni", bg=ACCENT, fg="white", width=15,
                     relief="flat", activebackground="#ec4899")
status_btn = tk.Button(btn_frame, text="📖 Status", bg=PRIMARY, fg="white", width=15,
                       relief="flat", activebackground="#7c3aed")



def show_server_error(message):
    messagebox.showerror("Greška", f"Ne mogu se spojiti na server:\n{message}")


def login():
    global user_id

    name = entry.get().strip()

    if not name:
        messagebox.showwarning("Info", "Unesi ime")
        return

    try:
        r = requests.post(f"{BASE_URL}/login", json={"name": name}, timeout=5)
        r.raise_for_status()
        user_id = r.json()["user_id"]

        login_frame.pack_forget()

        
        main_frame.pack(fill="both", expand=True)
        sidebar.pack(side="left", fill="y")
        content.pack(side="right", fill="both", expand=True)

        load_books()

    except requests.exceptions.RequestException as exc:
        show_server_error(str(exc))



def load_books():
    global books, displayed_books, book_ids

    try:
        response = requests.get(f"{BASE_URL}/books", timeout=5)
        response.raise_for_status()
        books = response.json()
        displayed_books = books

        listbox.delete(0, tk.END)
        book_ids = []

        for b in displayed_books:
            listbox.insert(
                tk.END,
                f"{b['title']} — {b['author']}  ⭐ {round(b['average_rating'],1)}"
            )
            book_ids.append(b["id"])

    except requests.exceptions.RequestException as exc:
        show_server_error(str(exc))



def search_books():
    global displayed_books, book_ids

    q = search_var.get().strip().lower()
    displayed_books = [
        b for b in books
        if q in b["title"].lower() or q in b["author"].lower()
    ] if q else books

    listbox.delete(0, tk.END)
    book_ids = []

    for b in displayed_books:
        listbox.insert(
            tk.END,
            f"{b['title']} — {b['author']}  ⭐ {round(b['average_rating'],1)}"
        )
        book_ids.append(b["id"])

    if not displayed_books:
        listbox.insert(tk.END, "Nema rezultata za zadani upit.")


search_btn.config(command=search_books)


def rate_book():
    sel = listbox.curselection()
    if not sel or not book_ids:
        messagebox.showwarning("Info", "Odaberi knjigu")
        return

    book_id = book_ids[sel[0]]

    popup = tk.Toplevel(root)
    popup.title("Ocijeni knjigu")
    popup.configure(bg=BG)

    tk.Label(popup, text="Ocijeni (1–10 → polovične ocjene)",
             bg=BG).pack(pady=10)

    scale = tk.Scale(popup, from_=1, to=10,
                     orient="horizontal", bg=BG)
    scale.pack()

    def submit():
        rating = scale.get() / 2

        try:
            response = requests.post(f"{BASE_URL}/rate", json={
                "user_id": user_id,
                "book_id": book_id,
                "rating": rating
            }, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            show_server_error(str(exc))
            return

        popup.destroy()
        load_books()

    tk.Button(popup, text="Spremi",
              bg=PRIMARY, command=submit).pack(pady=10)


rate_btn.config(command=rate_book)


def add_book():
    popup = tk.Toplevel(root)
    popup.title("Dodaj knjigu")
    popup.configure(bg=BG)

    tk.Label(popup, text="Naslov", bg=BG, font=FONT_BODY).pack(pady=(10, 0))
    title_entry = tk.Entry(popup, font=FONT_BODY, width=40)
    title_entry.pack(padx=10, pady=5)

    tk.Label(popup, text="Autor", bg=BG, font=FONT_BODY).pack(pady=(10, 0))
    author_entry = tk.Entry(popup, font=FONT_BODY, width=40)
    author_entry.pack(padx=10, pady=5)

    def submit():
        title = title_entry.get().strip()
        author = author_entry.get().strip()

        if not title or not author:
            messagebox.showwarning("Upozorenje", "Unesite naslov i autora knjige.")
            return

        try:
            response = requests.post(f"{BASE_URL}/add_book", json={
                "title": title,
                "author": author
            }, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            show_server_error(str(exc))
            return

        popup.destroy()
        load_books()

    tk.Button(popup, text="Dodaj knjigu",
              bg=PRIMARY, fg="white", font=FONT_SUBTITLE,
              relief="flat", command=submit).pack(pady=15)



def set_status():
    sel = listbox.curselection()
    if not sel or not book_ids:
        messagebox.showwarning("Info", "Odaberi knjigu")
        return

    book_id = book_ids[sel[0]]

    popup = tk.Toplevel(root)
    popup.configure(bg=BG)

    status = tk.StringVar(value="plan")

    tk.Radiobutton(popup, text="📌 Plan",
                   variable=status, value="plan", bg=BG, font=FONT_BODY).pack(anchor="w", pady=2)
    tk.Radiobutton(popup, text="📖 Čita se",
                   variable=status, value="reading", bg=BG, font=FONT_BODY).pack(anchor="w", pady=2)
    tk.Radiobutton(popup, text="✅ Završeno",
                   variable=status, value="completed", bg=BG, font=FONT_BODY).pack(anchor="w", pady=2)

    def save():
        try:
            response = requests.post(f"{BASE_URL}/user_book", json={
                "user_id": user_id,
                "book_id": book_id,
                "status": status.get()
            }, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            show_server_error(str(exc))
            return
        popup.destroy()

    tk.Button(popup, text="Spremi",
              bg=PRIMARY, command=save).pack()


status_btn.config(command=set_status)


def my_library():
    popup = tk.Toplevel(root)
    popup.configure(bg=BG)

    try:
        response = requests.get(f"{BASE_URL}/user_book/{user_id}", timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        show_server_error(str(exc))
        return

    if not data:
        tk.Label(popup, text="Nema knjiga", bg=BG).pack()
        return

    for item in data:
        color = PLAN
        status_text = item["status"]
        if item["status"] == "reading":
            color = READING
            status_text = "Čita se"
        elif item["status"] == "completed":
            color = GOOD
            status_text = "Završeno"

        tk.Label(popup,
                 text=f"{item['title']} → {status_text}",
                 fg=color,
                 bg=BG, font=FONT_BODY).pack(anchor="w", pady=2)



def show_about():
    popup = tk.Toplevel(root)
    popup.title("O aplikaciji")
    popup.configure(bg=BG)

    tk.Label(popup, text="📚 BookTakeover", font=("Segoe UI Semibold", 14), bg=BG).pack(padx=20, pady=(20, 10), anchor="w")
    tk.Label(popup, text="Autor: Antonia Tušćan\nVerzija: 1.0\nDatum: 2026\nTehnologije: Python, Flask, SQLite, Tkinter\n\nOpis: Aplikacija za upravljanje knjižnicom, ocjenjivanje knjiga i praćenje statusa čitanja.",
             bg=BG, justify="left", font=FONT_BODY).pack(padx=20, pady=(0, 20), anchor="w")



tk.Button(sidebar, text="📚 Knjige",
          bg=PRIMARY, fg="white", font=FONT_BODY,
          relief="flat", command=load_books).pack(fill="x", pady=(20, 5), padx=10)

tk.Button(sidebar, text="➕ Dodaj knjigu",
          bg=ACCENT, fg="white", font=FONT_BODY,
          relief="flat", command=add_book).pack(fill="x", pady=5, padx=10)

tk.Button(sidebar, text="📖 Moja knjižnica",
          bg=PRIMARY, fg="white", font=FONT_BODY,
          relief="flat", command=my_library).pack(fill="x", pady=5, padx=10)

tk.Button(sidebar, text="ℹ O aplikaciji",
          bg=ACCENT, fg="white", font=FONT_BODY,
          relief="flat", command=show_about).pack(fill="x", pady=5, padx=10)



header.pack(pady=10)
search_entry.pack(pady=5)
search_btn.pack(pady=5)
listbox.pack(pady=10)

btn_frame.pack(pady=10)
rate_btn.grid(row=0, column=0, padx=5)
status_btn.grid(row=0, column=1, padx=5)



tk.Button(login_frame, text="Prijava",
          bg=PRIMARY, fg="white", font=FONT_SUBTITLE,
          relief="flat", command=login).pack(pady=10)



root.mainloop()
