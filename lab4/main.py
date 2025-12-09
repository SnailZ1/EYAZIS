
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from nlp_engine import NLPEngine
from db_manager import DBManager
import os

class TranslationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система машинного перевода")
        self.geometry("1200x800")
        
        self.nlp = NLPEngine()
        self.db = DBManager()
        
        # Данные состояния
        self.last_results = None
        self.current_sentences = []
        
        self._build_menu()
        self._build_tabs()
        
    def _build_menu(self):
        menubar = tk.Menu(self)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть файл...", command=self.load_file)
        file_menu.add_command(label="Сохранить результаты...", command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)
        
        menubar.add_cascade(label="Файл", menu=file_menu)
        self.config(menu=menubar)

    def _build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 1. Вкладка Перевода
        self.tab_translate = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_translate, text="Перевод")
        self._build_translate_tab()
        
        # 2. Вкладка Статистики слов
        self.tab_stats = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_stats, text="Статистика слов")
        self._build_stats_tab()
        
        # 3. Вкладка Синтаксиса
        self.tab_syntax = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_syntax, text="Синтаксис")
        self._build_syntax_tab()
        
        # 4. Вкладка Словаря БД
        self.tab_dict = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dict, text="Словарь БД")
        self._build_dict_tab()

    def _build_translate_tab(self):
        paned = tk.PanedWindow(self.tab_translate, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая часть
        left_frame = ttk.Frame(paned)
        
        l_header = ttk.Frame(left_frame)
        l_header.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(l_header, text="Исходный текст (English)").pack(side=tk.LEFT)
        ttk.Button(l_header, text="Загрузить из TXT", command=self.load_file).pack(side=tk.RIGHT)
        
        self.source_text = tk.Text(left_frame, wrap=tk.WORD, width=40)
        self.source_text.pack(fill=tk.BOTH, expand=True)
        paned.add(left_frame)
        
        # Правая часть
        right_frame = ttk.Frame(paned)
        ttk.Label(right_frame, text="Перевод (Russian)").pack(anchor="w")
        self.target_text = tk.Text(right_frame, wrap=tk.WORD, width=40)
        self.target_text.pack(fill=tk.BOTH, expand=True)
        paned.add(right_frame)
        
        # Панель управления снизу
        ctrl_frame = ttk.Frame(self.tab_translate)
        ctrl_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_translate = ttk.Button(ctrl_frame, text="ПЕРЕВЕСТИ", command=self.run_translation)
        self.btn_translate.pack(side=tk.RIGHT)
        
        self.lbl_stats = ttk.Label(ctrl_frame, text="Статистика: слов 0 / переведено 0")
        self.lbl_stats.pack(side=tk.LEFT)

    def _build_stats_tab(self):
        columns = ("word", "trans", "tag", "desc", "count")
        self.stats_tree = ttk.Treeview(self.tab_stats, columns=columns, show="headings")
        self.stats_tree.heading("word", text="Word")
        self.stats_tree.heading("trans", text="Translation")
        self.stats_tree.heading("tag", text="POS Tag")
        self.stats_tree.heading("desc", text="Description")
        self.stats_tree.heading("count", text="Freq (in text)")
        
        self.stats_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _build_syntax_tab(self):
        frame = ttk.Frame(self.tab_syntax)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(frame, text="Выберите предложение:").pack(anchor="w")
        self.sent_combo = ttk.Combobox(frame, state="readonly")
        self.sent_combo.pack(fill=tk.X)
        self.sent_combo.bind("<<ComboboxSelected>>", self.on_sentence_select)
        
        ttk.Label(frame, text="Дерево синтаксического разбора:").pack(anchor="w", pady=(10,0))
        self.tree_output = tk.Text(frame, wrap=tk.NONE, font=("Consolas", 10))
        self.tree_output.pack(fill=tk.BOTH, expand=True)

    def _build_dict_tab(self):
        # Панель инструментов: Обновить, Редактировать
        toolbar = ttk.Frame(self.tab_dict)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Обновить список", command=self.refresh_dict).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Редактировать выделенное", command=self.edit_dict_entry).pack(side=tk.LEFT, padx=5)
        
        columns = ("en", "ru", "tag", "freq")
        self.dict_tree = ttk.Treeview(self.tab_dict, columns=columns, show="headings")
        self.dict_tree.heading("en", text="English")
        self.dict_tree.heading("ru", text="Russian")
        self.dict_tree.heading("tag", text="POS")
        self.dict_tree.heading("freq", text="Global Freq")
        
        self.dict_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.refresh_dict()

    # --- Actions ---
    
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path:
            try:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        text = f.read()
                except UnicodeDecodeError:
                    with open(path, 'r', encoding='cp1251') as f: # Fallback
                        text = f.read()
                
                self.source_text.delete("1.0", tk.END)
                self.source_text.insert(tk.END, text)
            except Exception as e:
                messagebox.showerror("Ошибка загрузки файла", f"Не удалось прочитать файл:\n{e}")

    def run_translation(self):
        text = self.source_text.get("1.0", tk.END).strip()
        if not text:
            return
            
        self.btn_translate.config(state="disabled", text="Обработка...")
        # Запускаем в потоке, так как перевод может быть долгим
        threading.Thread(target=self._process_text_thread, args=(text,), daemon=True).start()

    def _process_text_thread(self, text):
        try:
            results = self.nlp.process_text(text)
            self.after(0, self._update_ui_with_results, results)
        except Exception as e:
            self.after(0, messagebox.showerror, "Ошибка", str(e))
            self.after(0, self.btn_translate.config, {"state": "normal", "text": "ПЕРЕВЕСТИ"})

    def _update_ui_with_results(self, results):
        self.last_results = results
        self.current_sentences = results['sentences']
        
        # Обновляем текст перевода
        self.target_text.delete("1.0", tk.END)
        self.target_text.insert(tk.END, results['full_translation'])
        
        # Обновляем статистику
        self.lbl_stats.config(text=f"Всего слов: {results['total_words']} | Переведено: {results['translated_count']}")
        
        # Таблица статистики
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        
        for item in results['word_stats']:
            self.stats_tree.insert("", tk.END, values=(
                item['word'], item['trans'], item['tag'], item['desc'], item['count']
            ))
            
        # Комбобокс предложений
        self.sent_combo['values'] = self.current_sentences
        if self.current_sentences:
            self.sent_combo.current(0)
            self.on_sentence_select(None)
            
        # Обновляем словарь (могли добавиться новые слова)
        self.refresh_dict()
        
        self.btn_translate.config(state="normal", text="ПЕРЕВЕСТИ")
        messagebox.showinfo("Готово", "Перевод завершен!")

    def on_sentence_select(self, event):
        sent = self.sent_combo.get()
        if sent:
            tree_str = self.nlp.get_syntax_tree(sent)
            self.tree_output.delete("1.0", tk.END)
            self.tree_output.insert(tk.END, tree_str)

    def refresh_dict(self):
        # Очистить
        for item in self.dict_tree.get_children():
            self.dict_tree.delete(item)
        # Заполнить
        words = self.db.get_all_words()
        for w in words:
            self.dict_tree.insert("", tk.END, values=w)

    def edit_dict_entry(self):
        selected = self.dict_tree.selection()
        if not selected:
            return
        
        item = self.dict_tree.item(selected[0])
        values = item['values'] # en, ru, tag, freq
        word_en = values[0]
        curr_ru = values[1]
        curr_tag = values[2]
        
        # Simple Dialog for editing
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Редактирование: {word_en}")
        
        tk.Label(edit_win, text="Перевод:").pack()
        e_ru = tk.Entry(edit_win)
        e_ru.insert(0, curr_ru)
        e_ru.pack()
        
        tk.Label(edit_win, text="POS Tag:").pack()
        e_tag = tk.Entry(edit_win)
        e_tag.insert(0, curr_tag)
        e_tag.pack()
        
        def save():
            new_ru = e_ru.get()
            new_tag = e_tag.get()
            self.db.update_word_translation(word_en, new_ru, new_tag)
            self.refresh_dict()
            edit_win.destroy()
            
        tk.Button(edit_win, text="Сохранить", command=save).pack()

    def save_results(self):
        if not self.last_results:
            messagebox.showwarning("Внимание", "Нет данных для сохранения. Сначала выполните перевод.")
            return
            
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("=== ИСХОДНЫЙ ТЕКСТ ===\n")
                    f.write(self.source_text.get("1.0", tk.END).strip() + "\n\n")
                    
                    f.write("=== ПЕРЕВОД ===\n")
                    f.write(self.last_results['full_translation'] + "\n\n")
                    
                    f.write("=== СТАТИСТИКА ===\n")
                    f.write(f"Всего слов: {self.last_results['total_words']}\n")
                    f.write(f"Переведено: {self.last_results['translated_count']}\n\n")
                    
                    f.write("=== СПИСОК СЛОВ (Частотный) ===\n")
                    f.write(f"{'WORD':<20} | {'TRANS':<20} | {'TAG':<5} | {'COUNT'}\n")
                    f.write("-" * 60 + "\n")
                    for item in self.last_results['word_stats']:
                        f.write(f"{item['word']:<20} | {item['trans']:<20} | {item['tag']:<5} | {item['count']}\n")
                        
                messagebox.showinfo("Успех", "Результаты сохранены!")
            except Exception as e:
                messagebox.showerror("Ошибка сохранения", str(e))

if __name__ == "__main__":
    app = TranslationApp()
    app.mainloop()
