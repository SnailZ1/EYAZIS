# -*- coding: utf-8 -*-
"""Вкладка обучения для пересоздания языковых профилей."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from document_processor import DocumentProcessor
from language_profile import LanguageProfileManager


class TrainingTab(ctk.CTkFrame):
    """Позволяет создавать новые языковые профили на основе своих корпусов."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = LanguageProfileManager()
        self.processor = DocumentProcessor()
        self.selected_folder: Path | None = None
        self.language_var = ctk.StringVar(value="ru")
        self.tokens: list[str] = []

        self._build_layout()

    def _build_layout(self):
        self.grid_columnconfigure((0, 1), weight=1)
        form = ctk.CTkFrame(self, corner_radius=12)
        form.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Язык профиля").grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        ctk.CTkOptionMenu(form, values=["ru", "de"], variable=self.language_var).grid(
            row=1, column=0, padx=10, pady=10, sticky="ew"
        )

        self.folder_entry = ctk.CTkEntry(form, placeholder_text="Папка с PDF")
        self.folder_entry.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        ctk.CTkButton(form, text="Выбрать папку", command=self._select_folder).grid(
            row=3, column=0, padx=10, pady=(0, 10), sticky="ew"
        )

        ctk.CTkButton(form, text="Собрать профиль", command=self._train_profile).grid(
            row=4, column=0, padx=10, pady=10, sticky="ew"
        )

        self.status_label = ctk.CTkLabel(form, text="Ожидание данных")
        self.status_label.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="w")

        # Таблица топ-слов
        table_frame = ctk.CTkFrame(self, corner_radius=12)
        table_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(table_frame, text="Топ-100 слов").grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.table = ttk.Treeview(table_frame, columns=("word", "count"), show="headings")
        self.table.heading("word", text="Слово")
        self.table.heading("count", text="Частота")
        self.table.column("word", anchor="w")
        self.table.column("count", anchor="center")
        self.table.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def _select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = Path(folder)
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)

    def _train_profile(self):
        if not self.selected_folder:
            messagebox.showinfo("Нет данных", "Выберите папку с PDF")
            return
        tokens: list[str] = []
        pdfs = list(self.selected_folder.glob("*.pdf"))
        if not pdfs:
            messagebox.showwarning("Нет файлов", "Папка не содержит PDF")
            return

        for pdf in pdfs:
            try:
                document = self.processor.process(pdf)
                tokens.extend(document.tokens)
            except Exception as exc:
                messagebox.showerror("Ошибка чтения", f"{pdf.name}: {exc}")
                return

        language = self.language_var.get()
        profile = self.manager.build_from_tokens(language, tokens)
        self.status_label.configure(text=f"Профиль {language} сохранён ({len(tokens)} токенов)")
        self._populate_table(profile.frequencies)

    def _populate_table(self, frequencies: dict[str, int]):
        for item in self.table.get_children():
            self.table.delete(item)
        for word, count in list(frequencies.items())[:100]:
            self.table.insert("", "end", values=(word, count))

