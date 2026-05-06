import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x500")

        self.records = []
        self.filename = "weather_data.json"

        self.load_from_file()

        # Поля ввода
        input_frame = tk.LabelFrame(root, text="Новая запись", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="e")
        self.date_entry = tk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="e")
        self.temp_entry = tk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Описание:").grid(row=0, column=4, sticky="e")
        self.desc_entry = tk.Entry(input_frame, width=25)
        self.desc_entry.grid(row=0, column=5, padx=5)

        self.precip_var = tk.BooleanVar()
        self.precip_check = tk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var)
        self.precip_check.grid(row=0, column=6, padx=5)

        self.add_btn = tk.Button(input_frame, text="Добавить запись", command=self.add_record)
        self.add_btn.grid(row=0, column=7, padx=10)

        # Фильтры
        filter_frame = tk.LabelFrame(root, text="Фильтры", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0)
        self.filter_date_entry = tk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)
        tk.Button(filter_frame, text="Применить фильтр даты", command=self.filter_by_date).grid(row=0, column=2, padx=5)

        tk.Label(filter_frame, text="Фильтр по температуре (> °C):").grid(row=0, column=3)
        self.filter_temp_entry = tk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=4, padx=5)
        tk.Button(filter_frame, text="Применить фильтр темп.", command=self.filter_by_temp).grid(row=0, column=5, padx=5)

        tk.Button(filter_frame, text="Сбросить фильтры", command=self.load_records_to_table).grid(row=0, column=6, padx=10)

        # Таблица для отображения
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        self.tree.column("date", width=120)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=250)
        self.tree.column("precipitation", width=80)

        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_records_to_table()

        # Кнопки сохранения/загрузки
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_frame, text="Сохранить в JSON", command=self.save_to_file).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Загрузить из JSON", command=self.load_from_file_and_refresh).pack(side="left", padx=5)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_record(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        if not date or not temp or not desc:
            messagebox.showerror("Ошибка", "Все поля (дата, температура, описание) должны быть заполнены")
            return

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        try:
            temp_val = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        self.records.append({
            "date": date,
            "temperature": temp_val,
            "description": desc,
            "precipitation": precip
        })

        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

        self.load_records_to_table()
        messagebox.showinfo("Успех", "Запись добавлена")

    def load_records_to_table(self, records_to_show=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if records_to_show is None:
            records_to_show = self.records

        for rec in records_to_show:
            precip_str = "Да" if rec["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(
                rec["date"],
                rec["temperature"],
                rec["description"],
                precip_str
            ))

    def filter_by_date(self):
        filter_date = self.filter_date_entry.get().strip()
        if not filter_date:
            messagebox.showwarning("Предупреждение", "Введите дату для фильтрации")
            return

        if not self.validate_date(filter_date):
            messagebox.showerror("Ошибка", "Неверный формат даты фильтра")
            return

        filtered = [rec for rec in self.records if rec["date"] == filter_date]
        self.load_records_to_table(filtered)

    def filter_by_temp(self):
        temp_thresh = self.filter_temp_entry.get().strip()
        if not temp_thresh:
            messagebox.showwarning("Предупреждение", "Введите порог температуры")
            return

        try:
            thresh_val = float(temp_thresh)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        filtered = [rec for rec in self.records if rec["temperature"] > thresh_val]
        self.load_records_to_table(filtered)

    def save_to_file(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {self.filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_file(self):
        if not os.path.exists(self.filename):
            self.records = []
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                self.records = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")
            self.records = []

    def load_from_file_and_refresh(self):
        self.load_from_file()
        self.load_records_to_table()
        messagebox.showinfo("Успех", "Данные загружены из JSON")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()