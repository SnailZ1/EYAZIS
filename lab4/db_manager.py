
import sqlite3
import os

class DBManager:
    def __init__(self, db_path="dictionary.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных и таблицы словаря"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dictionary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_en TEXT UNIQUE NOT NULL,
                word_ru TEXT NOT NULL,
                pos_tag TEXT,
                frequency INTEGER DEFAULT 1
            )
        ''')
        conn.commit()
        conn.close()

    def get_word(self, word_en):
        """Получить перевод слова и информацию о нем"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT word_ru, pos_tag, frequency FROM dictionary WHERE word_en = ?', (word_en.lower(),))
        result = cursor.fetchone()
        conn.close()
        return result

    def add_word(self, word_en, word_ru, pos_tag):
        """Добавить новое слово или обновить частоту существующего"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем наличие
        cursor.execute('SELECT frequency FROM dictionary WHERE word_en = ?', (word_en.lower(),))
        row = cursor.fetchone()
        
        if row:
            # Обновляем частоту
            new_freq = row[0] + 1
            cursor.execute('UPDATE dictionary SET frequency = ? WHERE word_en = ?', (new_freq, word_en.lower()))
        else:
            # Вставляем новое
            cursor.execute('INSERT INTO dictionary (word_en, word_ru, pos_tag, frequency) VALUES (?, ?, ?, 1)', 
                           (word_en.lower(), word_ru, pos_tag))
        
        conn.commit()
        conn.close()

    def update_word_translation(self, word_en, new_ru, new_pos):
        """Ручное обновление перевода"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE dictionary SET word_ru = ?, pos_tag = ? WHERE word_en = ?', 
                       (new_ru, new_pos, word_en.lower()))
        conn.commit()
        conn.close()

    def get_all_words(self):
        """Получить все слова для отображения в таблице"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT word_en, word_ru, pos_tag, frequency FROM dictionary ORDER BY frequency DESC')
        results = cursor.fetchall()
        conn.close()
        return results
