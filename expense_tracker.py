import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("700x550")
        
        self.expenses = self.load_data()
        self.categories = ["Еда", "Транспорт", "Развлечения", "Одежда", "Здоровье", "ЖКХ", "Другое"]
        
        self.create_widgets()
        self.update_table()

    def create_widgets(self):
        # --- Фрейм добавления расхода ---
        add_frame = tk.LabelFrame(self.root, text="Добавить расход", padx=10, pady=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(add_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_amount = tk.Entry(add_frame)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.combo_category = ttk.Combobox(add_frame, values=self.categories, state="readonly")
        self.combo_category.grid(row=0, column=3, padx=5, pady=5)
        self.combo_category.current(0)

        tk.Label(add_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.entry_date = tk.Entry(add_frame)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.grid(row=0, column=5, padx=5, pady=5)

        btn_add = tk.Button(add_frame, text="Добавить расход", command=self.add_expense)
        btn_add.grid(row=1, column=0, columnspan=6, pady=10)

        # --- Фрейм фильтрации ---
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация и период", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category = ttk.Combobox(filter_frame, values=["Все"] + self.categories, state="readonly")
        self.filter_category.current(0)
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="С (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_start = tk.Entry(filter_frame)
        self.filter_date_start.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="По (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.filter_date_end = tk.Entry(filter_frame)
        self.filter_date_end.grid(row=0, column=5, padx=5, pady=5)

        btn_filter = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        btn_filter.grid(row=1, column=0, columnspan=3, pady=5, sticky="e")
        
        btn_reset = tk.Button(filter_frame, text="Сбросить фильтр", command=self.update_table)
        btn_reset.grid(row=1, column=3, columnspan=3, pady=5, sticky="w")

        # --- Итого за период ---
        self.lbl_total = tk.Label(self.root, text="Сумма за выбранный период: 0.00", font=("Arial", 12, "bold"))
        self.lbl_total.pack(pady=5)

        # --- Таблица ---
        columns = ("amount", "category", "date")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def validate_date(self, date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_expense(self):
        amount_str = self.entry_amount.get()
        category = self.combo_category.get()
        date_str = self.entry_date.get()

        # Валидация суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Сумма должна быть положительным числом.")
            return

        # Валидация даты
        if not self.validate_date(date_str):
            messagebox.showerror("Ошибка ввода", "Дата должна быть в формате ГГГГ-ММ-ДД.")
            return

        expense = {"amount": amount, "category": category, "date": date_str}
        self.expenses.append(expense)
        self.save_data()
        self.update_table()
        
        self.entry_amount.delete(0, tk.END)

    def apply_filter(self):
        cat_filter = self.filter_category.get()
        start_str = self.filter_date_start.get()
        end_str = self.filter_date_end.get()

        filtered_expenses = self.expenses

        if cat_filter != "Все":
            filtered_expenses = [e for e in filtered_expenses if e["category"] == cat_filter]

        if start_str:
            if self.validate_date(start_str):
                filtered_expenses = [e for e in filtered_expenses if e["date"] >= start_str]
            else:
                messagebox.showerror("Ошибка", "Неверный формат начальной даты.")
                return
                
        if end_str:
            if self.validate_date(end_str):
                filtered_expenses = [e for e in filtered_expenses if e["date"] <= end_str]
            else:
                messagebox.showerror("Ошибка", "Неверный формат конечной даты.")
                return

        self.update_table(filtered_expenses)

    def update_table(self, data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        display_data = data if data is not None else self.expenses
        total_sum = 0.0

        for exp in display_data:
            self.tree.insert("", tk.END, values=(exp["amount"], exp["category"], exp["date"]))
            total_sum += exp["amount"]

        self.lbl_total.config(text=f"Сумма за выбранный период: {total_sum:.2f}")

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
