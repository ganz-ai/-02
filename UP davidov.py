import sqlite3
import tkinter as tk
from tkinter import Tk
from tkinter import *
from tkinter import ttk, messagebox
import keyboard
from datetime import datetime

korzina = {}
id_tekushego_polzovatelya = None
rol_tekushego_polzovatelya = None
login_tekushego_polzovatelya = None
okno_korziny = None

okno_avtoriz = Tk()
okno_avtoriz.title("Авторизация")
okno_avtoriz.geometry("500x400")
okno_avtoriz.configure(bg="azure2")
frame = Frame(okno_avtoriz, background="azure2", width=300)
frame.pack(side=LEFT, fill=BOTH, expand=True)

def sohranit():
    login = pole_logina.get().strip()
    parol = pole_parolya.get().strip()
    rol = "покупатель"

    if not login or not parol:
        messagebox.showwarning("Внимание", "Заполните все поля")
        return

    conn = sqlite3.connect('Davidov2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ID_polzovatela FROM Polzovateli WHERE login = ?", (login,))
    if cursor.fetchone():
        messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")
        conn.close()
        return
    try:
        cursor.execute("INSERT INTO Polzovateli (login, parol, roli) VALUES (?, ?, ?)", (login, parol, rol))
        conn.commit()
        messagebox.showinfo("Успех", "Регистрация успешно завершена!")
        okno_reg.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка", str(e))
    finally:
        conn.close()

def registratsiya():
    global pole_logina, pole_parolya, okno_reg
    okno_reg = tk.Tk()
    okno_reg.title("Регистрация")
    okno_reg.geometry("350x200")
    okno_reg.configure(bg="azure2")
    frame = ttk.Frame(okno_reg, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    ttk.Label(frame, text="Логин:").grid(row=1, column=0, sticky=tk.W, pady=5)
    pole_logina = ttk.Entry(frame, width=30)
    pole_logina.grid(row=1, column=1, pady=5, padx=0)
    ttk.Label(frame, text="Пароль:").grid(row=2, column=0, sticky=tk.W, pady=5)
    pole_parolya = ttk.Entry(frame, show="*", width=30)
    pole_parolya.grid(row=2, column=1, pady=5, padx=0)
    knopka_reg = ttk.Button(frame, text="Регистрация", command=sohranit)
    knopka_reg.grid(row=3, column=0, columnspan=2, pady=10)
    knopka_nazad = ttk.Button(frame, text="Назад", command=lambda: (okno_reg.destroy(), okno_avtoriz.deiconify()))
    knopka_nazad.grid(row=4, column=0, columnspan=2, pady=5)

    okno_reg.mainloop()

def izmenit_rol(derevo):
    vybrannoe = derevo.selection()
    if not vybrannoe:
        messagebox.showwarning("Внимание", "Выберите пользователя")
        return

    id_polzovatelya = derevo.item(vybrannoe[0])['values'][0]
    if id_polzovatelya == id_tekushego_polzovatelya:
        messagebox.showerror("Ошибка", "Нельзя изменить свою роль")
        return

    okno_roli = tk.Toplevel()
    okno_roli.title("Изменение роли")
    okno_roli.geometry("300x200")
    okno_roli.configure(bg="azure2")
    tk.Label(okno_roli, text="Новая роль:", bg="azure2").pack(pady=10)
    peremennaya_roli = tk.StringVar(value="покупатель")
    spisok_rolej = ttk.Combobox(okno_roli, textvariable=peremennaya_roli, values=["покупатель", "сотрудник", "менеджер", "администратор"], state="readonly")
    spisok_rolej.pack(pady=10)

    def sohranit_rol():
        novaya_rol = peremennaya_roli.get()
        conn = sqlite3.connect('Davidov2.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE Polzovateli SET roli = ? WHERE id_polzovatela = ?", (novaya_rol, id_polzovatelya))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Роль изменена")
        okno_roli.destroy()
        obnovit_polzovatelej(derevo)
    tk.Button(okno_roli, text="Сохранить", command=sohranit_rol).pack(pady=10)

def udalit_polzovatelya(derevo):
    vybrannoe = derevo.selection()
    if not vybrannoe:
        messagebox.showwarning("Внимание", "Выберите пользователя")
        return

    id_polzovatelya = derevo.item(vybrannoe[0])['values'][0]
    if id_polzovatelya == id_tekushego_polzovatelya:
        messagebox.showerror("Ошибка", "Нельзя удалить самого себя")
        return

    if messagebox.askyesno("Подтверждение", "Удалить этого пользователя?"):
        conn = sqlite3.connect('Davidov2.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Polzovateli WHERE id_polzovatela = ?", (id_polzovatelya,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Пользователь удален")
        obnovit_polzovatelej(derevo)

def obnovit_polzovatelej(derevo):
    for element in derevo.get_children():
        derevo.delete(element)
    conn = sqlite3.connect('Davidov2.db')
    cursor = conn.cursor()
    for znacheniya in cursor.execute("SELECT id_polzovatela, login, parol, roli FROM Polzovateli"):
        derevo.insert("", END, values=znacheniya)
    conn.close()

def dobavit_tovar(derevo):
    okno_dobavleniya = tk.Toplevel()
    okno_dobavleniya.title("Добавление товара")
    okno_dobavleniya.geometry("400x600")
    okno_dobavleniya.configure(bg="azure2")
    nadpisi = ["Артикул:", "Название:", "Айди категории:", "Цена:", "Марка авто:", "Модель авто:", "Статус:", "Описание:"]
    polya_vvoda = {}

    for i, nadpis in enumerate(nadpisi):
        tk.Label(okno_dobavleniya, text=nadpis, bg="azure2").pack(pady=5)
        pole = tk.Entry(okno_dobavleniya, width=40)
        pole.pack(pady=5)
        polya_vvoda[nadpis] = pole
    polya_vvoda["Статус:"].insert(0, "В наличии")

    def sohranit_tovar():
        znacheniya = []
        for nadpis in nadpisi:
            val = polya_vvoda[nadpis].get().strip()
            if not val and nadpis != "Описание:":
                messagebox.showwarning("Внимание", f"Заполните поле {nadpis}")
                return
            znacheniya.append(val)
        conn = sqlite3.connect('Davidov2.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO Tovari (artikul, Nazvanie, id_kategorii, cena, marka_avto, model_avto, status, opisanie) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                           (znacheniya[0], znacheniya[1], znacheniya[2], znacheniya[3], znacheniya[4], znacheniya[5], znacheniya[6], znacheniya[7]))
            conn.commit()
            messagebox.showinfo("Успех", "Товар добавлен")
            okno_dobavleniya.destroy()
            obnovit_tovary(derevo)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            conn.close()
    tk.Button(okno_dobavleniya, text="Сохранить", command=sohranit_tovar, bg="green", fg="white").pack(pady=20)

def redaktirovat_tovar(derevo):
    vybrannoe = derevo.selection()
    if not vybrannoe:
        messagebox.showwarning("Внимание", "Выберите товар")
        return

    id_tovara = derevo.item(vybrannoe[0])['values'][0]
    conn = sqlite3.connect('Davidov2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tovari WHERE id_tovara = ?", (id_tovara,))
    tovar = cursor.fetchone()
    conn.close()

    okno_redaktirovaniya = tk.Toplevel()
    okno_redaktirovaniya.title("Редактирование товара")
    okno_redaktirovaniya.geometry("400x600")
    okno_redaktirovaniya.configure(bg="azure2")
    nadpisi = ["Артикул:", "Название:", "Айди категории:", "Цена:", "Марка авто:", "Модель авто:", "Описание:", "Статус:"]
    polya_vvoda = {}

    for i, nadpis in enumerate(nadpisi):
        tk.Label(okno_redaktirovaniya, text=nadpis, bg="azure2").pack(pady=5)
        pole = tk.Entry(okno_redaktirovaniya, width=40)
        pole.insert(0, str(tovar[i + 1]) if tovar[i + 1] else "")
        pole.pack(pady=5)
        polya_vvoda[nadpis] = pole

    def obnovit_tovar():
        znacheniya = []
        for nadpis in nadpisi:
            val = polya_vvoda[nadpis].get().strip()
            znacheniya.append(val)
        conn = sqlite3.connect('Davidov2.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE Tovari SET artikul=?, Nazvanie=?, id_kategorii=?, cena=?, marka_avto=?, model_avto=?, opisanie=?, status=? WHERE id_tovara=?""", (*znacheniya, id_tovara))
            conn.commit()
            messagebox.showinfo("Успех", "Товар обновлен")
            okno_redaktirovaniya.destroy()
            obnovit_tovary(derevo)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            conn.close()
    tk.Button(okno_redaktirovaniya, text="Обновить", command=obnovit_tovar, bg="orange", fg="white").pack(pady=20)

def udalit_tovar(derevo):
    vybrannoe = derevo.selection()
    if not vybrannoe:
        messagebox.showwarning("Внимание", "Выберите товар")
        return

    if messagebox.askyesno("Подтверждение", "Удалить этот товар?"):
        id_tovara = derevo.item(vybrannoe[0])['values'][0]
        conn = sqlite3.connect('Davidov2.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Tovari WHERE id_tovara = ?", (id_tovara,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Товар удален")
        obnovit_tovary(derevo) 

def obnovit_tovary(derevo):
    for element in derevo.get_children():
        derevo.delete(element)
    conn = sqlite3.connect('Davidov2.db')
    cursor = conn.cursor()
    for znacheniya in cursor.execute("SELECT * FROM Tovari"):
        derevo.insert("", END, values=znacheniya)
    conn.close()

def dobavit_v_korzinu(derevo):
    vybrannoe = derevo.selection()
    if not vybrannoe:
        messagebox.showwarning("Внимание", "Выберите товар")
        return

    znacheniya = derevo.item(vybrannoe[0])['values']
    id_tovara = znacheniya[0]
    artikul = znacheniya[1]
    nazvanie_tovara = znacheniya[2]
    cena_tovara = znacheniya[3]
    status_tovara = znacheniya[6]
    if status_tovara and status_tovara.lower() == "в наличии":
        if id_tovara in korzina:
            korzina[id_tovara]['kolichestvo'] += 1
            messagebox.showinfo("Успех", f"Товар '{nazvanie_tovara}' добавлен в корзину (теперь {korzina[id_tovara]['kolichestvo']} шт.)")
        else:
            korzina[id_tovara] = {
                'id_tovara': id_tovara,
                'nazvanie': nazvanie_tovara,
                'cena': cena_tovara,
                'kolichestvo': 1
            }
            messagebox.showinfo("Успех", f"Товар '{nazvanie_tovara}' добавлен в корзину")
    else:
        messagebox.showwarning("Внимание", f"Товар '{nazvanie_tovara}' недоступен для заказа\nСтатус товара: '{status_tovara}'")

def pokazat_korzinu(glavnoe_okno, derevo):
    global okno_korziny
    if not korzina:
        messagebox.showinfo("Корзина", "Корзина пуста")
        return

    if okno_korziny is not None and okno_korziny.winfo_exists():
        okno_korziny.destroy()
    okno_korziny = tk.Toplevel()
    okno_korziny.title("Корзина")
    okno_korziny.geometry("800x600")
    okno_korziny.configure(bg="azure2")
    tk.Label(okno_korziny, text="МОЯ КОРЗИНА", font=("Arial", 16, "bold"), bg="azure2").pack(pady=10)
    ramka_korziny = ttk.Frame(okno_korziny, padding="10")
    ramka_korziny.pack(fill=BOTH, expand=True)
    stolbtsy = ('id_tovara', 'nazvanie', 'cena', 'kolichestvo', 'summa')
    derevo_korziny = ttk.Treeview(ramka_korziny, columns=stolbtsy, show="headings")
    derevo_korziny.pack(fill=BOTH, expand=True)
    derevo_korziny.heading("id_tovara", text="ID товара")
    derevo_korziny.heading("nazvanie", text="Название")
    derevo_korziny.heading("cena", text="Цена")
    derevo_korziny.heading("kolichestvo", text="Кол-во")
    derevo_korziny.heading("summa", text="Сумма")

    derevo_korziny.column("id_tovara", width=80)
    derevo_korziny.column("nazvanie", width=250)
    derevo_korziny.column("cena", width=100)
    derevo_korziny.column("kolichestvo", width=80)
    derevo_korziny.column("summa", width=100)

    obshchaya_summa = 0
    for id_tovara, element in korzina.items():
        summa = element['cena'] * element['kolichestvo']
        obshchaya_summa += summa
        derevo_korziny.insert("", END, values=(
        id_tovara, element['nazvanie'], f"{element['cena']} Руб", element['kolichestvo'], f"{summa} Руб"))
    ramka_itogo = tk.Frame(okno_korziny, bg="azure2")
    ramka_itogo.pack(fill=tk.X, pady=10)
    tk.Label(ramka_itogo, text=f"ИТОГО: {obshchaya_summa} Руб", font=("Arial", 14, "bold"), fg="red", bg="azure2").pack(
        pady=5)

    def udalit_iz_korziny():
        vybrannoe = derevo_korziny.selection()
        if not vybrannoe:
            messagebox.showwarning("Внимание", "Выберите товар для удаления")
            return

        values = derevo_korziny.item(vybrannoe[0])['values']
        id_tovara = values[0]
        if id_tovara in korzina:
            del korzina[id_tovara]
            messagebox.showinfo("Успех", f"Товар '{values[1]}' удален из корзины")
            pokazat_korzinu(glavnoe_okno, derevo)
    ramka_knopok_korziny = tk.Frame(okno_korziny, bg="azure2")
    ramka_knopok_korziny.pack(fill=tk.X, pady=5)
    tk.Button(ramka_knopok_korziny, text="Удалить выбранный", command=udalit_iz_korziny, bg="#e74c3c", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    tk.Button(ramka_knopok_korziny, text="Оформить заказ", command=lambda: oformit_zakaz(okno_korziny, glavnoe_okno, derevo), bg="#2ecc71", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(ramka_knopok_korziny, text="Обновить", command=lambda: pokazat_korzinu(glavnoe_okno, derevo), bg="#3498db", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

def oformit_zakaz(okno_korziny, glavnoe_okno, derevo):
    global korzina

    if not korzina:
        messagebox.showwarning("Внимание", "Корзина пуста")
        return

    if id_tekushego_polzovatelya is None:
        messagebox.showerror("Ошибка", "Пользователь не авторизован")
        return

    conn = sqlite3.connect('Davidov2.db')
    cursor = conn.cursor()
    artikuly = []
    for id_tovara, element in korzina.items():
        cursor.execute("SELECT artikul, status FROM Tovari WHERE id_tovara = ?", (id_tovara,))
        result = cursor.fetchone()
        if result:
            artikuly.append((id_tovara, result[0], result[1]))

    nedostupnye_tovary = []
    for id_tovara, artikul, status in artikuly:
        if status.lower() != "в наличии":
            nedostupnye_tovary.append(korzina[id_tovara]['nazvanie'])
            del korzina[id_tovara]

    if nedostupnye_tovary:
        messagebox.showwarning("Внимание", f"Следующие товары больше не в наличии и удалены из корзины:\n{', '.join(nedostupnye_tovary)}")
        if not korzina:
            okno_korziny.destroy()
            return
        pokazat_korzinu(glavnoe_okno, derevo)
        return

    try:
        for id_tovara, element in korzina.items():
            kolichestvo = element['kolichestvo']
            cena = element['cena']
            cursor.execute("""INSERT INTO Zakazi (id_polzovatela, kolichestvo, id_tovara, cena) VALUES (?, ?, ?, ?)""", (id_tekushego_polzovatelya, kolichestvo, id_tovara, cena))
        conn.commit()

        obshchaya_summa = 0
        for element in korzina.values():
            obshchaya_summa += element['cena'] * element['kolichestvo']

        tekst_zakaza = "=" * 35 + "\n"
        tekst_zakaza += "         ВАШ ЗАКАЗ\n"
        tekst_zakaza += "=" * 35 + "\n\n"

        for element in korzina.values():
            summa = element['cena'] * element['kolichestvo']
            tekst_zakaza += f"{element['nazvanie']}\n"
            tekst_zakaza += f"  {element['kolichestvo']} шт. x {element['cena']} Руб = {summa} Руб\n\n"
        tekst_zakaza += "-" * 35 + "\n"
        tekst_zakaza += f"ИТОГО К ОПЛАТЕ: {obshchaya_summa} Руб\n"
        tekst_zakaza += "=" * 35 + "\n"
        tekst_zakaza += "Спасибо за покупку!\n"
        tekst_zakaza += "Ждем вас снова в Шинчики!"

        messagebox.showinfo("ЗАКАЗ ОФОРМЛЕН", tekst_zakaza)
        korzina.clear()
        okno_korziny.destroy()
        messagebox.showinfo("Успех", "Заказ успешно оформлен и сохранен в базе данных!")

    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось сохранить заказ: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def obnovit_tovary_dlya_pokupatelya(derevo):
    for element in derevo.get_children():
        derevo.delete(element)

    conn = sqlite3.connect('Davidov2.db')
    cursor = conn.cursor()
    for znacheniya in cursor.execute("""SELECT id_tovara, artikul, Nazvanie, cena, marka_avto, model_avto, status, opisanie FROM Tovari """):
        derevo.insert("", END, values=znacheniya)
    conn.close()

def avtorizatsiya():
    global pole_vvoda_logina, pole_vvoda_parolya, id_tekushego_polzovatelya, rol_tekushego_polzovatelya, login_tekushego_polzovatelya
    login = pole_vvoda_logina.get()
    parol = pole_vvoda_parolya.get()

    if not login or not parol:
        messagebox.showerror("Внимание!", "Заполните все поля")
        return

    conn = sqlite3.connect('Davidov2.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT id_polzovatela, login, roli FROM Polzovateli WHERE login = ? AND parol = ?""", (login, parol))
    polzovatel = cursor.fetchone()
    conn.close()
    if polzovatel:
        id_tekushego_polzovatelya, login_tekushego_polzovatelya, rol_tekushego_polzovatelya = polzovatel
        messagebox.showinfo("Успех", f"Добро пожаловать, {login_tekushego_polzovatelya}")
        okno_avtoriz.withdraw()
        glavnoe_okno = tk.Tk()
        glavnoe_okno.title("Магазин автозапчастей Шинчики")
        glavnoe_okno.attributes("-fullscreen", True)
        glavnoe_okno.configure(bg="azure2")

        def exit_fullscreen(event=None):
            glavnoe_okno.attributes("-fullscreen", False)
        glavnoe_okno.bind("<Escape>", exit_fullscreen)
        verhnyaya_panel = tk.Frame(glavnoe_okno, bg="azure2")
        verhnyaya_panel.pack(fill=tk.X, pady=(5, 0))
        zagolovok = tk.Label(verhnyaya_panel, text="МАГАЗИН АВТОЗАПЧАСТЕЙ ШИНЧИКИ", font=("Arial", 20, "bold"), fg="black", bg="azure2")
        zagolovok.pack(pady=10)

        if rol_tekushego_polzovatelya == "администратор":
            tekst = f"День добрый, администратор"
        elif rol_tekushego_polzovatelya in ["менеджер", "сотрудник"]:
            tekst = f"Время работать: {login_tekushego_polzovatelya}"
        else:
            tekst = f"Добро пожаловать в магазин, {login_tekushego_polzovatelya}"

        informatsiya = tk.Label(verhnyaya_panel, text=tekst, font=("Arial", 14), fg="gray", bg="azure2")
        informatsiya.pack(pady=5)
        ttk.Separator(glavnoe_okno, orient='horizontal').pack(fill=tk.X, pady=5)
        ramka = ttk.Frame(glavnoe_okno, padding="20")
        ramka.pack(fill=tk.BOTH, expand=True)
        if rol_tekushego_polzovatelya == "администратор":
            stolbtsy = ('id', 'login', 'password', 'role')
            derevo = ttk.Treeview(ramka, columns=stolbtsy, show="headings")
            derevo.pack(fill=BOTH, expand=True)
            derevo.heading("id", text="Айди пользователя")
            derevo.heading("login", text="Логин")
            derevo.heading("password", text="Пароль")
            derevo.heading("role", text="Роль")
            ramka_knopok = tk.Frame(glavnoe_okno, bg="azure2")
            ramka_knopok.pack(fill=tk.X, pady=5)
            tk.Button(ramka_knopok, text="Изменить роль", command=lambda: izmenit_rol(derevo), bg="cornflower blue", fg="white").pack(side=LEFT, padx=5)
            tk.Button(ramka_knopok, text="Удалить пользователя", command=lambda: udalit_polzovatelya(derevo), bg="red", fg="white").pack(side=LEFT, padx=5)
            tk.Button(ramka_knopok, text="Обновить", command=lambda: obnovit_polzovatelej(derevo)).pack(side=LEFT, padx=5)
            obnovit_polzovatelej(derevo)

        elif rol_tekushego_polzovatelya in ["менеджер", "сотрудник"]:
            stolbtsy = ('id_tovara', 'artikul', 'Nazvanie', 'id_kategorii', 'cena', 'marka_avto', 'model_avto', 'opisanie', 'status')
            derevo = ttk.Treeview(ramka, columns=stolbtsy, show="headings")
            derevo.pack(fill=BOTH, expand=True)
            derevo.heading("id_tovara", text="Айди товара")
            derevo.heading("artikul", text="Артикул")
            derevo.heading("Nazvanie", text="Название")
            derevo.heading("id_kategorii", text="Айди категории")
            derevo.heading("cena", text="Цена")
            derevo.heading("marka_avto", text="Марка авто")
            derevo.heading("model_avto", text="Модель авто")
            derevo.heading("opisanie", text="Описание")
            derevo.heading("status", text="Статус")
            ramka_knopok = tk.Frame(glavnoe_okno, bg="azure2")
            ramka_knopok.pack(fill=tk.X, pady=5)
            tk.Button(ramka_knopok, text="Добавить товар", command=lambda: dobavit_tovar(derevo), bg="DarkGreen", fg="white").pack(side=LEFT, padx=5)
            tk.Button(ramka_knopok, text="Редактировать", command=lambda: redaktirovat_tovar(derevo), bg="dim gray", fg="white").pack(side=LEFT, padx=5)
            tk.Button(ramka_knopok, text="Удалить", command=lambda: udalit_tovar(derevo), bg="Brown2", fg="white").pack(side=LEFT, padx=5)
            tk.Button(ramka_knopok, text="Обновить", command=lambda: obnovit_tovary(derevo), bg="DarkSlateGrey", fg="white").pack(side=LEFT, padx=5)
            obnovit_tovary(derevo)

        elif rol_tekushego_polzovatelya == "покупатель":
            stolbtsy = ('id_tovara', 'art', 'Nazvanie', 'cena', 'marka_avto', 'model_avto', 'status', 'opisanie')
            derevo = ttk.Treeview(ramka, columns=stolbtsy, show="headings")
            derevo.pack(fill=BOTH, expand=True)
            derevo.heading("id_tovara", text="ID")
            derevo.heading("art", text="Артикул")
            derevo.heading("Nazvanie", text="Название")
            derevo.heading("cena", text="Цена")
            derevo.heading("marka_avto", text="Марка авто")
            derevo.heading("model_avto", text="Модель авто")
            derevo.heading("status", text="Статус")
            derevo.heading("opisanie", text="Описание")

            derevo.column("#1", width=50)
            derevo.column("#2", width=90)
            derevo.column("#3", width=160)
            derevo.column("#4", width=100)
            derevo.column("#5", width=100)
            derevo.column("#6", width=100)
            derevo.column("#7", width=80)
            derevo.column("#8", width=250)

            ramka_knopok = tk.Frame(glavnoe_okno, bg="azure2")
            ramka_knopok.pack(fill=tk.X, pady=5)
            tk.Button(ramka_knopok, text="Добавить в корзину", command=lambda: dobavit_v_korzinu(derevo), bg="#2ecc71", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)
            tk.Button(ramka_knopok, text="Корзина", command=lambda: pokazat_korzinu(glavnoe_okno, derevo), bg="#3498db", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)
            tk.Button(ramka_knopok, text="Обновить", command=lambda: obnovit_tovary_dlya_pokupatelya(derevo), bg="#95a5a6", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)
            obnovit_tovary_dlya_pokupatelya(derevo)

        knopka_vykhoda = tk.Button(glavnoe_okno, text="Выйти из аккаунта", command=lambda: vykhod(glavnoe_okno), bg="red", fg="white", font=("Arial", 11))
        knopka_vykhoda.pack(pady=10)
        glavnoe_okno.protocol("WM_DELETE_WINDOW", lambda: vykhod(glavnoe_okno))
        glavnoe_okno.mainloop()
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

def vykhod(osnovnoe_okno):
    osnovnoe_okno.destroy()
    okno_avtoriz.deiconify()


pole_vvoda_logina = ttk.Entry()
pole_vvoda_logina.place(x=190, y=190)
pole_vvoda_parolya = ttk.Entry()
pole_vvoda_parolya.place(x=190, y=215)
knopka_vkhoda = ttk.Button(text="Вход", command=avtorizatsiya)
knopka_vkhoda.place(x=160, y=240)
knopka_registratsii = ttk.Button(text="Регистрация", command=registratsiya)
knopka_registratsii.place(x=238, y=240)
metka_logina = ttk.Label(text="Логин", background="azure2")
metka_logina.place(x=145, y=188)
metka_parolya = ttk.Label(text="Пароль", background="azure2")
metka_parolya.place(x=140, y=216)
metka_nazvaniya = ttk.Label(text="Шинчики", background="azure2", font=("Arial", 36, "bold italic"))
metka_nazvaniya.place(x=150, y=40)

okno_avtoriz.mainloop()