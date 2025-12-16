# -*- coding: utf-8 -*-
"""Вкладка распознавания с пакетной обработкой, предпросмотром и аналитикой."""

from __future__ import annotations

import threading
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from config import DEFAULT_SETTINGS
from gui.results_panel import ResultsPanel
from recognition_engine import RecognitionEngine


class DragDropFrame(ctk.CTkFrame):
    """Простая зона перетаскивания; при отсутствии поддержки открывает диалог выбора."""

    def __init__(self, master, on_files_dropped, **kwargs):
        super().__init__(master, corner_radius=12, **kwargs)
        self.on_files_dropped = on_files_dropped
        self.label = ctk.CTkLabel(self, text="Перетащите PDF сюда\nили нажмите для выбора")
        self.label.pack(expand=True, fill="both", padx=10, pady=10)
        self.configure(fg_color="#1f2933")

        try:
            self.drop_target_register("DND_Files")
            self.dnd_bind("<<Drop>>", self._handle_drop)
        except Exception:
            # tkdnd может отсутствовать — просто используем выбор по нажатию
            pass

        self.bind("<Button-1>", lambda _: self._open_dialog())

    def _open_dialog(self):
        selected = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if selected:
            self.on_files_dropped([Path(path) for path in selected])

    def _handle_drop(self, event):
        files = self.master.splitlist(event.data)
        pdfs = [Path(file) for file in files if file.lower().endswith(".pdf")]
        if pdfs:
            self.on_files_dropped(pdfs)


class RecognitionTab(ctk.CTkFrame):
    """Интерфейс основного процесса распознавания."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = RecognitionEngine()
        self.selected_files: list[Path] = []
        self.results = []
        self._processing_thread: threading.Thread | None = None

        self._build_layout()

    # Компоновка -----------------------------------------------------------------
    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Левая панель управления
        control_panel = ctk.CTkFrame(self, corner_radius=12)
        control_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        control_panel.grid_columnconfigure(0, weight=1)

        DragDropFrame(
            control_panel, on_files_dropped=self._add_files, height=150
        ).grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkButton(control_panel, text="Выбрать папку", command=self._select_folder).grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky="ew"
        )
        ctk.CTkButton(control_panel, text="Очистить список", command=self._clear_files).grid(
            row=2, column=0, padx=10, pady=(0, 10), sticky="ew"
        )

        self.file_listbox = ctk.CTkTextbox(control_panel, height=150)
        self.file_listbox.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self.progress = ctk.CTkProgressBar(control_panel)
        self.progress.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(control_panel, text="Готово")
        self.status_label.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="w")

        self.mode_var = ctk.StringVar(value="single")
        switch = ctk.CTkSwitch(
            control_panel,
            text="Режим сравнения",
            variable=self.mode_var,
            onvalue="compare",
            offvalue="single",
        )
        switch.grid(row=6, column=0, padx=10, pady=(0, 10), sticky="w")

        ctk.CTkButton(
            control_panel, text="Запустить распознавание", command=self._start_processing
        ).grid(row=7, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkButton(
            control_panel, text="Экспорт результатов", command=self._export_results
        ).grid(row=8, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Правая панель с результатами и графиками
        right_panel = ctk.CTkFrame(self, corner_radius=12)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        self.results_panel = ResultsPanel(right_panel)
        self.results_panel.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        # таблица
        columns = ("file", "method", "language", "score")
        self.table = ttk.Treeview(right_panel, columns=columns, show="headings", height=6)
        for col, title in zip(columns, ["Файл", "Метод", "Язык", "Счёт"]):
            self.table.heading(col, text=title)
            self.table.column(col, anchor="center")
        self.table.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.table.tag_configure("frequency", background="#102a43")
        self.table.tag_configure("short_words", background="#0f3b2e")
        self.table.tag_configure("neural", background="#1d3557")

        # график matplotlib
        self.figure = Figure(figsize=(5, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Вероятности методов")
        self.canvas = FigureCanvasTkAgg(self.figure, master=right_panel)
        self.canvas.get_tk_widget().grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # панель предпросмотра
        preview_frame = ctk.CTkFrame(right_panel)
        preview_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(preview_frame, text="Предпросмотр текста").grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 0)
        )
        self.preview_box = ctk.CTkTextbox(preview_frame, height=120)
        self.preview_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Работа с файлами --------------------------------------------------------
    def _add_files(self, files: list[Path]):
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
        self._refresh_file_list()

    def _select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            folder_path = Path(folder)
            pdfs = sorted(folder_path.glob("*.pdf"))[: DEFAULT_SETTINGS["batch_limit"]]
            self._add_files(pdfs)

    def _clear_files(self):
        self.selected_files.clear()
        self.results = []
        self._refresh_file_list()
        for item in self.table.get_children():
            self.table.delete(item)
        self.results_panel.populate([])
        self._update_chart([])
        self.preview_box.delete("0.0", "end")

    def _refresh_file_list(self):
        self.file_listbox.delete("0.0", "end")
        for file in self.selected_files:
            self.file_listbox.insert("end", f"{file.name}\n")

    # Обработка -------------------------------------------------------------
    def _start_processing(self):
        if not self.selected_files:
            messagebox.showinfo("Нет файлов", "Добавьте хотя бы один PDF")
            return
        if self._processing_thread and self._processing_thread.is_alive():
            messagebox.showinfo("Обработка", "Процесс уже запущен")
            return

        self.progress.set(0)
        self.status_label.configure(text="Обработка...")
        self._processing_thread = threading.Thread(target=self._process_files, daemon=True)
        self._processing_thread.start()

    def _process_files(self):
        results = []
        total = len(self.selected_files)

        for idx, pdf in enumerate(self.selected_files, start=1):
            try:
                result = self.engine.analyze_file(pdf)
                results.append(result)
                self.after(0, self._update_ui_with_result, result)
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("Ошибка", str(exc)))
            finally:
                progress = idx / total
                self.after(0, lambda value=progress: self.progress.set(value))

        self.results = results
        if results and DEFAULT_SETTINGS["auto_save_history"]:
            self.engine.append_history(results)
            self.after(0, lambda: messagebox.showinfo("Готово", "Обработка завершена"))
        self.after(0, lambda: self.status_label.configure(text="Готово"))

    def _update_ui_with_result(self, result):
        self.preview_box.delete("0.0", "end")
        preview_text = result.preview_text.strip()[: DEFAULT_SETTINGS["preview_max_chars"]]
        self.preview_box.insert(
            "0.0", f"{result.file_path.name}\n\n{preview_text}"
        )

        self.results_panel.populate(result.method_results)
        self._update_table(result)
        self._update_chart(result.method_results)

    def _update_table(self, result):
        for method in result.method_results:
            self.table.insert(
                "",
                "end",
                values=(result.file_path.name, method.method, method.language, f"{method.score:.3f}"),
                tags=(method.method,),
            )

    def _update_chart(self, method_results):
        self.ax.clear()
        if method_results:
            methods = [m.method for m in method_results]
            scores = [m.score for m in method_results]
            colors = ["#1E88E5", "#26A69A", "#00ACC1"]
            self.ax.bar(methods, scores, color=colors[: len(scores)])
            self.ax.set_ylim(0, 1)
        self.ax.set_ylabel("Score")
        self.ax.set_title("Вероятности методов")
        self.canvas.draw_idle()

    # Экспорт -----------------------------------------------------------------
    def _export_results(self):
        if not self.results:
            messagebox.showinfo("Нет данных", "Сначала выполните распознавание")
            return
        file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx"), ("PDF", "*.pdf")],
        )
        if not file:
            return
        try:
            self.engine.export_results(self.results, Path(file))
            messagebox.showinfo("Экспорт завершён", f"Файл сохранён: {file}")
        except Exception as exc:
            messagebox.showerror("Ошибка экспорта", str(exc))

