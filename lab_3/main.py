"""
Система автоматического реферирования документов
Вариант №19: sentence extraction + OSTIS
Предметные области: медицина, искусствоведение
Языки: русский, английский
"""

import sys
import argparse
from gui import main as gui_main


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='Система автоматического реферирования документов'
    )
    parser.add_argument('--test-mode', action='store_true',
                       help='Запуск в тестовом режиме')
    parser.add_argument('--cli', action='store_true',
                       help='Запуск в режиме командной строки')
    
    args = parser.parse_args()
    
    if args.test_mode:
        print("Тестовый режим пока не реализован")
        print("Используйте GUI для тестирования")
        return
    
    if args.cli:
        print("CLI режим пока не реализован")
        print("Используйте GUI: python main.py")
        return
    
    # Запускаем GUI
    print("Запуск графического интерфейса...")
    gui_main()


if __name__ == "__main__":
    main()
