import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt


# ---------------- DATABASE ----------------

def create_database():
    try:
        conn = sqlite3.connect("bmi_records.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))


# ---------------- BMI CALCULATION ----------------

def calculate_bmi():
    try:
        name = name_entry.get().strip()
        weight = float(weight_entry.get())
        height = float(height_entry.get())

        if not name:
            messagebox.showerror("Error", "Please enter a name.")
            return

        if weight <= 0 or height <= 0:
            messagebox.showerror(
                "Error",
                "Weight and height must be greater than 0."
            )
            return

        bmi = weight / (height ** 2)

        if bmi < 18.5:
            category = "Underweight"
            result_label.config(fg="orange")

        elif bmi < 25:
            category = "Normal"
            result_label.config(fg="green")

        elif bmi < 30:
            category = "Overweight"
            result_label.config(fg="orange")

        else:
            category = "Obese"
            result_label.config(fg="red")

        result_label.config(
            text=f"BMI: {bmi:.2f} | {category}"
        )

        save_record(name, weight, height, bmi, category)

    except ValueError:
        messagebox.showerror(
            "Input Error",
            "Please enter valid numeric values."
        )


# ---------------- SAVE RECORD ----------------

def save_record(name, weight, height, bmi, category):
    try:
        conn = sqlite3.connect("bmi_records.db")
        cursor = conn.cursor()

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO bmi_records
            (name, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, weight, height, bmi, category, date))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "BMI record saved successfully."
        )

    except sqlite3.Error as e:
        messagebox.showerror(
            "Database Error",
            f"Unable to save record:\n{e}"
        )


# ---------------- SHOW HISTORY ----------------

def show_history():
    name = name_entry.get().strip()

    if not name:
        messagebox.showerror("Error", "Please enter a name.")
        return

    try:
        conn = sqlite3.connect("bmi_records.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT date, weight, height, bmi, category
            FROM bmi_records
            WHERE name = ?
            ORDER BY date
        """, (name,))

        records = cursor.fetchall()
        conn.close()

        if not records:
            messagebox.showinfo(
                "History",
                f"No records found for {name}."
            )
            return

        history_window = tk.Toplevel(root)
        history_window.title(f"BMI History - {name}")
        history_window.geometry("650x350")

        columns = ("Date", "Weight", "Height", "BMI", "Category")

        table = ttk.Treeview(
            history_window,
            columns=columns,
            show="headings"
        )

        for column in columns:
            table.heading(column, text=column)
            table.column(column, width=120)

        for record in records:
            table.insert("", tk.END, values=record)

        table.pack(fill=tk.BOTH, expand=True)

    except sqlite3.Error as e:
        messagebox.showerror(
            "Database Error",
            f"Unable to read records:\n{e}"
        )


# ---------------- BMI TREND GRAPH ----------------

def show_graph():
    name = name_entry.get().strip()

    if not name:
        messagebox.showerror("Error", "Please enter a name.")
        return

    try:
        conn = sqlite3.connect("bmi_records.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT date, bmi
            FROM bmi_records
            WHERE name = ?
            ORDER BY date
        """, (name,))

        records = cursor.fetchall()
        conn.close()

        if not records:
            messagebox.showinfo(
                "Graph",
                f"No BMI records found for {name}."
            )
            return

        dates = [record[0] for record in records]
        bmi_values = [record[1] for record in records]

        plt.figure(figsize=(9, 5))

        plt.plot(
            dates,
            bmi_values,
            marker="o"
        )

        plt.axhline(
            y=18.5,
            linestyle="--",
            label="Underweight Limit"
        )

        plt.axhline(
            y=25,
            linestyle="--",
            label="Normal Limit"
        )

        plt.axhline(
            y=30,
            linestyle="--",
            label="Obese Limit"
        )

        plt.title(f"BMI Trend - {name}")
        plt.xlabel("Date")
        plt.ylabel("BMI")

        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

    except sqlite3.Error as e:
        messagebox.showerror(
            "Database Error",
            f"Unable to read records:\n{e}"
        )


# ---------------- GUI ----------------

create_database()

root = tk.Tk()
root.title("BMI Calculator")
root.geometry("500x500")

title_label = tk.Label(
    root,
    text="BMI Calculator",
    font=("Arial", 24, "bold")
)

title_label.pack(pady=20)


name_label = tk.Label(
    root,
    text="Name:",
    font=("Arial", 12)
)

name_label.pack()

name_entry = tk.Entry(
    root,
    width=30,
    font=("Arial", 12)
)

name_entry.pack(pady=5)


weight_label = tk.Label(
    root,
    text="Weight (kg):",
    font=("Arial", 12)
)

weight_label.pack()

weight_entry = tk.Entry(
    root,
    width=30,
    font=("Arial", 12)
)

weight_entry.pack(pady=5)


height_label = tk.Label(
    root,
    text="Height (meters):",
    font=("Arial", 12)
)

height_label.pack()

height_entry = tk.Entry(
    root,
    width=30,
    font=("Arial", 12)
)

height_entry.pack(pady=5)


calculate_button = tk.Button(
    root,
    text="Calculate BMI",
    command=calculate_bmi,
    width=20,
    font=("Arial", 12)
)

calculate_button.pack(pady=15)


result_label = tk.Label(
    root,
    text="BMI: --",
    font=("Arial", 16, "bold")
)

result_label.pack(pady=10)


history_button = tk.Button(
    root,
    text="View History",
    command=show_history,
    width=20,
    font=("Arial", 11)
)

history_button.pack(pady=5)


graph_button = tk.Button(
    root,
    text="View BMI Trend",
    command=show_graph,
    width=20,
    font=("Arial", 11)
)

graph_button.pack(pady=5)


root.mainloop()
