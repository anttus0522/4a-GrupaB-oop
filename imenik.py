import sqlite3



def inicijalizacija():
    konekcija = sqlite3.connect("Imenik.db")
    kursor = konekcija.cursor()

    sql_naredba = """
    CREATE TABLE IF NOT EXISTS Kontakti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ime_prezime TEXT NOT NULL,
        broj_mobitela TEXT NOT NULL
    );
    """

    kursor.execute(sql_naredba)
    konekcija.commit()
    konekcija.close()



def unesi_kontakt():
    ime = input("Unesi ime i prezime: ")
    broj = input("Unesi broj mobitela: ")

    conn = sqlite3.connect("Imenik.db")
    cur = conn.cursor()

    sql = "INSERT INTO Kontakti (ime_prezime, broj_mobitela) VALUES (?, ?)"
    cur.execute(sql, (ime, broj))

    conn.commit()
    conn.close()

    print("Kontakt je uspješno dodan!")


def ispisi_kontakte():
    print("\n--- KONTAKTI ---")

    conn = sqlite3.connect("Imenik.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM Kontakti")
    svi_kontakti = cur.fetchall()

    print(f"{'ID':<5} | {'IME I PREZIME':<25} | {'BROJ'}")
    print("-" * 45)

    for red in svi_kontakti:
        print(f"{red[0]:<5} | {red[1]:<25} | {red[2]}")

    conn.close()


def obrisi_kontakt():
    ispisi_kontakte()
    id_za_brisanje = input("\nUnesi ID kontakta za brisanje: ")

    conn = sqlite3.connect("Imenik.db")
    cur = conn.cursor()

    sql = "DELETE FROM Kontakti WHERE id = ?"
    cur.execute(sql, (id_za_brisanje,))

    if cur.rowcount > 0:
        print("Kontakt je obrisan.")
    else:
        print("Ne postoji kontakt s tim ID-em.")

    conn.commit()
    conn.close()



def izbornik():
    while True:
        print("\n--- IZBORNIK ---")
        print("1. Unos novog kontakta")
        print("2. Ispis svih kontakata")
        print("3. Brisanje kontakta")
        print("4. Izlaz")

        izbor = input("Odaberi opciju (1-4): ")

        if izbor == "1":
            unesi_kontakt()
        elif izbor == "2":
            ispisi_kontakte()
        elif izbor == "3":
            obrisi_kontakt()
        elif izbor == "4":
            print("Izlaz iz programa. Doviđenja!")
            break
        else:
            print("Nevažeći odabir. Pokušaj ponovno.")


inicijalizacija()
izbornik()
