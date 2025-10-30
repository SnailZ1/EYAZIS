Команды для запуска:

Построить индекс:   
python main.py --build-index

Запустить веб-интерфейс:   
python main.py --web

Тестирование:   
python main.py --test

Все вместе:  
python main.py --build-index --web 

Все вместе с использованием word2vec эмбеддингов:
python main.py --build-index --web --use-word2vec

Для использования других моделей нужно переписать путь
--word2vec-path=<путь к модели>

