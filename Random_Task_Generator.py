import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

data_file = Random_Task_Generator.json
class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator - Чижов Юрий")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Предопределённые задачи
        self.default_tasks = [
            {"name": "Прочитать статью по Python", "type": "учёба"},
            {"name": "Сделать зарядку 15 минут", "type": "спорт"},
            {"name": "Закончить отчёт для работы", "type": "работа"},
            {"name": "Изучить новый фреймворк", "type": "учёба"},
            {"name": "Пробежка 3 км", "type": "спорт"},
            {"name": "Провести встречу с командой", "type": "работа"},
            {"name": "Решить задачу на алгоритмы", "type": "учёба"},
            {"name": "Отжимания 30 раз", "type": "спорт"},
            {"name": "Создать презентацию", "type": "работа"}
        ]
        
        # Загружаем пользовательские задачи
        self.custom_tasks = []
        
        # История сгенерированных задач
        self.history = []
        
        # Файл для сохранения данных
        self.data_file = "task_history.json"
        
        # Загрузка данных из файла
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление списка типов для фильтрации
        self.update_filter_types()
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========== Секция генерации ==========
        gen_frame = ttk.LabelFrame(main_frame, text="Генерация задачи", padding="10")
        gen_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.generate_btn = ttk.Button(gen_frame, text="🎲 Сгенерировать задачу", command=self.generate_task)
        self.generate_btn.pack(pady=5)
        
        self.current_task_label = ttk.Label(gen_frame, text="Нажмите кнопку для генерации", font=("Arial", 12, "bold"))
        self.current_task_label.pack(pady=5)
        
        # ========== Секция добавления новой задачи ==========
        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую задачу", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_frame, text="Название задачи:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.new_task_entry = ttk.Entry(add_frame, width=40)
        self.new_task_entry.grid(row=0, column=1, padx=(0, 10), pady=5)
        
        ttk.Label(add_frame, text="Тип задачи:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.task_type_var = tk.StringVar(value="учёба")
        type_combo = ttk.Combobox(add_frame, textvariable=self.task_type_var, values=["учёба", "спорт", "работа"], width=20)
        type_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        add_btn = ttk.Button(add_frame, text="➕ Добавить задачу", command=self.add_custom_task)
        add_btn.grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # ========== Секция фильтрации ==========
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация истории", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Фильтр по типу:").pack(side=tk.LEFT, padx=(0, 10))
        self.filter_var = tk.StringVar(value="все")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, width=15)
        self.filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_combo.bind("<<ComboboxSelected>>", self.apply_filter)
        
        clear_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filter)
        clear_filter_btn.pack(side=tk.LEFT)
        
        clear_history_btn = ttk.Button(filter_frame, text="🗑 Очистить историю", command=self.clear_history)
        clear_history_btn.pack(side=tk.RIGHT)
        
        # ========== Секция истории ==========
        history_frame = ttk.LabelFrame(main_frame, text="История задач", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаём Treeview для отображения истории
        columns = ("№", "Дата", "Задача", "Тип")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        
        self.tree.heading("№", text="№")
        self.tree.heading("Дата", text="Дата и время")
        self.tree.heading("Задача", text="Задача")
        self.tree.heading("Тип", text="Тип")
        
        self.tree.column("№", width=40)
        self.tree.column("Дата", width=130)
        self.tree.column("Задача", width=280)
        self.tree.column("Тип", width=80)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Обновляем отображение истории
        self.update_history_display()
    
    def update_filter_types(self):
        """Обновление списка типов в фильтре"""
        all_types = set()
        for task in self.default_tasks + self.custom_tasks:
            all_types.add(task["type"])
        types_list = sorted(list(all_types))
        self.filter_combo["values"] = ["все"] + types_list
        if self.filter_var.get() not in self.filter_combo["values"]:
            self.filter_var.set("все")
    
    def generate_task(self):
        """Генерация случайной задачи из всех доступных"""
        all_tasks = self.default_tasks + self.custom_tasks
        
        if not all_tasks:
            messagebox.showwarning("Нет задач", "Добавьте хотя бы одну задачу перед генерацией!")
            return
        
        selected_task = random.choice(all_tasks)
        
        # Добавляем в историю с временной меткой
        history_entry = {
            "task_name": selected_task["name"],
            "task_type": selected_task["type"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(history_entry)
        
        # Обновляем отображение
        self.current_task_label.config(text=f"✅ {selected_task['name']} ({selected_task['type']})")
        self.update_history_display()
        self.save_data()
    
    def add_custom_task(self):
        """Добавление новой пользовательской задачи с валидацией"""
        task_name = self.new_task_entry.get().strip()
        task_type = self.task_type_var.get()
        
        # Валидация: не пустая строка
        if not task_name:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return
        
        # Проверка на дубликат (опционально)
        all_task_names = [t["name"] for t in self.default_tasks + self.custom_tasks]
        if task_name in all_task_names:
            messagebox.showwarning("Предупреждение", "Такая задача уже существует!")
            return
        
        self.custom_tasks.append({"name": task_name, "type": task_type})
        self.update_filter_types()
        self.new_task_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", f"Задача '{task_name}' добавлена!")
        self.save_data()
    
    def apply_filter(self, event=None):
        """Применение фильтра по типу"""
        self.update_history_display()
    
    def clear_filter(self):
        """Сброс фильтра"""
        self.filter_var.set("все")
        self.update_history_display()
    
    def clear_history(self):
        """Очистка всей истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.update_history_display()
            self.save_data()
            self.current_task_label.config(text="История очищена")
    
    def update_history_display(self):
        """Обновление отображения истории с учётом фильтра"""
        # Очищаем текущий список
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered_history = self.history.copy()
        filter_type = self.filter_var.get()
        
        if filter_type != "все":
            # Фильтруем задачи по типу (нужно найти тип задачи из источника)
            filtered_history = []
            for entry in self.history:
                # Находим тип задачи
                task_type = self.get_task_type(entry["task_name"])
                if task_type == filter_type:
                    filtered_history.append(entry)
        
        # Отображаем отфильтрованную историю
        for idx, entry in enumerate(filtered_history, 1):
            task_type = self.get_task_type(entry["task_name"])
            self.tree.insert("", tk.END, values=(
                idx,
                entry["timestamp"],
                entry["task_name"],
                task_type
            ))
    
    def get_task_type(self, task_name):
        """Получение типа задачи по её названию"""
        all_tasks = self.default_tasks + self.custom_tasks
        for task in all_tasks:
            if task["name"] == task_name:
                return task["type"]
        return "неизвестно"
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        data = {
            "custom_tasks": self.custom_tasks,
            "history": self.history
        }
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.custom_tasks = data.get("custom_tasks", [])
                    self.history = data.get("history", [])
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
                self.custom_tasks = []
                self.history = []

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()