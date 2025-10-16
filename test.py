from documents_processing.collector import DocumentCollector

def get_docs(path: str):

    collector = DocumentCollector()
    documents = collector.collect_documents(path)

    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ СБОРА ДОКУМЕНТОВ")
    print("="*50)
    
    for doc in documents:
        print(f"\n📄 Документ ID: {doc.doc_id}")
        print(f"   Заголовок: {doc.title}")
        print(f"   Тип: {doc.file_type}")
        print(f"   Размер содержимого: {len(doc.content)} символов")
        print(f"   Фрагмент: {doc.get_snippet(80)}")


if __name__ == "__main__":
    get_docs('./docs')