"""
Графический интерфейс для системы автоматического реферирования
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from pathlib import Path

from summarizer import SentenceExtractor, KeywordExtractor
from ostis_integration import SCsGenerator, SemanticLinker
from knowledge_base import KNOWLEDGE_BASE


class SummarizerGUI:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Система автоматического реферирования документов")
        self.root.geometry("1200x800")
        
        # Инициализация компонентов
        self.sentence_extractor = SentenceExtractor()
        self.keyword_extractor = KeywordExtractor()
        self.scs_generator = SCsGenerator()
        self.semantic_linker = SemanticLinker(KNOWLEDGE_BASE)
        
        # Данные
        self.current_file = None
        self.current_text = ""
        self.current_summary = None
        self.current_keywords = None
        self.current_keyword_tree = None
        self.current_language = None
        self.current_domain = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Создание виджетов интерфейса"""
        
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Button(top_frame, text="📂 Загрузить документ", 
                  command=self.load_document).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(top_frame, text="🔍 Создать реферат", 
                  command=self.generate_summary).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(top_frame, text="💾 Сохранить", 
                  command=self.save_summary).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(top_frame, text="🖨️ Печать", 
                  command=self.print_summary).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(top_frame, text="📄 Открыть оригинал", 
                  command=self.open_original).pack(side=tk.LEFT, padx=5)
        
        # Разделитель
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Панель настроек
        settings_frame = ttk.Frame(self.root, padding="10")
        settings_frame.pack(fill=tk.X)
        
        ttk.Label(settings_frame, text="Предметная область:").pack(side=tk.LEFT, padx=5)
        self.domain_var = tk.StringVar(value="medical")
        ttk.Radiobutton(settings_frame, text="Медицина", 
                       variable=self.domain_var, value="medical").pack(side=tk.LEFT)
        ttk.Radiobutton(settings_frame, text="Искусство", 
                       variable=self.domain_var, value="art").pack(side=tk.LEFT)
        
        ttk.Label(settings_frame, text="  |  Количество предложений:").pack(side=tk.LEFT, padx=5)
        self.num_sentences_var = tk.IntVar(value=10)
        ttk.Spinbox(settings_frame, from_=5, to=20, 
                   textvariable=self.num_sentences_var, width=5).pack(side=tk.LEFT)
        
        # Разделитель
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Основная область с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вкладка: Исходный текст
        self.original_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.original_tab, text="📄 Исходный документ")
        
        self.original_text = scrolledtext.ScrolledText(
            self.original_tab, wrap=tk.WORD, font=("Arial", 11)
        )
        self.original_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка: Реферат
        self.summary_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_tab, text="📝 Реферат")
        
        self.summary_text = scrolledtext.ScrolledText(
            self.summary_tab, wrap=tk.WORD, font=("Arial", 11)
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка: Ключевые слова
        self.keywords_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.keywords_tab, text="🔑 Ключевые слова")
        
        self.keywords_text = scrolledtext.ScrolledText(
            self.keywords_tab, wrap=tk.WORD, font=("Arial", 11)
        )
        self.keywords_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка: SC-код
        self.scs_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.scs_tab, text="🔗 SC-код (OSTIS)")
        
        self.scs_text = scrolledtext.ScrolledText(
            self.scs_tab, wrap=tk.WORD, font=("Courier New", 10)
        )
        self.scs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Статус-бар
        self.status_bar = ttk.Label(self.root, text="Готов к работе", 
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def load_document(self):
        """Загрузка документа"""
        filename = filedialog.askopenfilename(
            title="Выберите документ",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.current_text = f.read()
            
            self.current_file = filename
            self.original_text.delete(1.0, tk.END)
            self.original_text.insert(1.0, self.current_text)
            
            self.status_bar.config(text=f"Загружен: {os.path.basename(filename)}")
            
            # Автоматически определяем язык
            lang = self.sentence_extractor.text_processor.detect_language(self.current_text)
            self.current_language = lang
            
            messagebox.showinfo("Успех", 
                              f"Документ загружен!\nОпределен язык: {lang.upper()}")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
    
    def generate_summary(self):
        """Генерация реферата"""
        if not self.current_text:
            messagebox.showwarning("Предупреждение", 
                                 "Сначала загрузите документ!")
            return
        
        try:
            self.status_bar.config(text="Генерация реферата...")
            self.root.update()
            
            # Получаем параметры
            num_sentences = self.num_sentences_var.get()
            self.current_domain = self.domain_var.get()
            
            # Генерируем реферат
            self.current_summary = self.sentence_extractor.extract_summary(
                self.current_text, num_sentences
            )
            
            self.current_language = self.current_summary['language']
            
            # Извлекаем ключевые слова
            self.current_keywords = self.keyword_extractor.extract_keywords(
                self.current_text, 
                self.current_language,
                self.current_domain,
                top_n=20
            )
            
            # Улучшаем ключевые слова с помощью семантических связей
            self.current_keywords = self.semantic_linker.enhance_keywords_with_semantics(
                self.current_keywords,
                self.current_language,
                self.current_domain
            )
            
            # Строим дерево ключевых слов
            self.current_keyword_tree = self.keyword_extractor.build_keyword_tree(
                self.current_keywords,
                self.current_language,
                self.current_domain
            )
            
            # Отображаем реферат
            self._display_summary()
            
            # Отображаем ключевые слова
            self._display_keywords()
            
            # Генерируем SC-код
            self._generate_scs()
            
            self.status_bar.config(text="Реферат успешно создан!")
            self.notebook.select(self.summary_tab)
            
            messagebox.showinfo("Успех", 
                              f"Реферат создан!\n"
                              f"Предложений: {len(self.current_summary['sentences'])}\n"
                              f"Ключевых слов: {len(self.current_keywords)}")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при генерации реферата:\n{e}")
            self.status_bar.config(text="Ошибка!")
    
    def _display_summary(self):
        """Отображение реферата"""
        self.summary_text.delete(1.0, tk.END)
        
        # Заголовок
        header = f"РЕФЕРАТ\n"
        header += f"Документ: {os.path.basename(self.current_file) if self.current_file else 'Без имени'}\n"
        header += f"Язык: {self.current_language.upper()}\n"
        header += f"Предметная область: {self.current_domain}\n"
        header += f"Количество предложений: {len(self.current_summary['sentences'])}\n"
        header += "=" * 80 + "\n\n"
        
        self.summary_text.insert(tk.END, header)
        
        # Предложения
        for idx, sentence in enumerate(self.current_summary['sentences'], 1):
            self.summary_text.insert(tk.END, f"{idx}. {sentence}\n\n")
    
    def _display_keywords(self):
        """Отображение ключевых слов"""
        self.keywords_text.delete(1.0, tk.END)
        
        # Заголовок
        header = f"КЛЮЧЕВЫЕ СЛОВА\n"
        header += "=" * 80 + "\n\n"
        self.keywords_text.insert(tk.END, header)
        
        # Иерархическое дерево
        if self.current_keyword_tree.get('groups'):
            self.keywords_text.insert(tk.END, "ИЕРАРХИЯ ТЕРМИНОВ:\n\n")
            
            for main_term, related in self.current_keyword_tree['groups'].items():
                self.keywords_text.insert(tk.END, f"▸ {main_term.upper()}\n")
                for rel in related:
                    self.keywords_text.insert(tk.END, f"  • {rel}\n")
                self.keywords_text.insert(tk.END, "\n")
        
        # Остальные ключевые слова
        if self.current_keyword_tree.get('root'):
            self.keywords_text.insert(tk.END, "\nДРУГИЕ КЛЮЧЕВЫЕ СЛОВА:\n\n")
            for kw in self.current_keyword_tree['root']:
                self.keywords_text.insert(tk.END, f"• {kw}\n")
        
        # Список всех ключевых слов с весами
        self.keywords_text.insert(tk.END, f"\n\n{'=' * 80}\n")
        self.keywords_text.insert(tk.END, "ВСЕ КЛЮЧЕВЫЕ СЛОВА (с весами TF-IDF):\n\n")
        
        for idx, (keyword, score) in enumerate(self.current_keywords[:20], 1):
            self.keywords_text.insert(tk.END, f"{idx:2d}. {keyword:20s} ({score:.4f})\n")
    
    def _generate_scs(self):
        """Генерация SC-кода"""
        if not self.current_summary:
            return
        
        filename = os.path.basename(self.current_file) if self.current_file else "document.txt"
        
        scs_code = self.scs_generator.generate_document_scs(
            filename,
            self.current_text,
            self.current_summary,
            self.current_keywords,
            self.current_keyword_tree,
            self.current_language,
            self.current_domain
        )
        
        self.scs_text.delete(1.0, tk.END)
        self.scs_text.insert(1.0, scs_code)
    
    def save_summary(self):
        """Сохранение реферата"""
        if not self.current_summary:
            messagebox.showwarning("Предупреждение", 
                                 "Сначала создайте реферат!")
            return
        
        # Предлагаем сохранить в несколько файлов
        base_name = filedialog.asksaveasfilename(
            title="Сохранить реферат",
            defaultextension=".txt",
            filetypes=[("Текстовый файл", "*.txt")]
        )
        
        if not base_name:
            return
        
        try:
            # Убираем расширение
            base_path = Path(base_name).with_suffix('')
            
            # Сохраняем текстовый реферат
            txt_path = base_path.with_suffix('.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(self.summary_text.get(1.0, tk.END))
            
            # Сохраняем ключевые слова
            kw_path = base_path.with_name(base_path.name + '_keywords.txt')
            with open(kw_path, 'w', encoding='utf-8') as f:
                f.write(self.keywords_text.get(1.0, tk.END))
            
            # Сохраняем SC-код
            scs_path = base_path.with_suffix('.scs')
            with open(scs_path, 'w', encoding='utf-8') as f:
                f.write(self.scs_text.get(1.0, tk.END))
            
            messagebox.showinfo("Успех", 
                              f"Реферат сохранен:\n"
                              f"• {txt_path.name}\n"
                              f"• {kw_path.name}\n"
                              f"• {scs_path.name}")
            
            self.status_bar.config(text=f"Сохранено: {txt_path.name}")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")
    
    def print_summary(self):
        """Печать реферата"""
        if not self.current_summary:
            messagebox.showwarning("Предупреждение", 
                                 "Сначала создайте реферат!")
            return
        
        # В реальной системе здесь была бы интеграция с принтером
        # Для демонстрации просто показываем диалог
        messagebox.showinfo("Печать", 
                          "Функция печати:\n"
                          "Реферат будет отправлен на печать\n"
                          "(в демо-версии не реализовано)")
    
    def open_original(self):
        """Открытие исходного документа"""
        if not self.current_file:
            messagebox.showwarning("Предупреждение", 
                                 "Документ не загружен!")
            return
        
        try:
            # Открываем файл в системном редакторе
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(self.current_file)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', self.current_file])
            else:  # Linux
                subprocess.call(['xdg-open', self.current_file])
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")


def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = SummarizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
