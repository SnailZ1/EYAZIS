# -*- coding: utf-8 -*-

from pathlib import Path
from collections import Counter
import logging
import joblib
import pdfplumber

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV


DATA_DIR = Path("samples")
MODEL_PATH = Path("assets/lang_mlp.joblib")

CHUNK_SIZE = 500        # длина фрагмента
MIN_CHUNK_LEN = 150     # минимальная длина
NGRAM_RANGE = (3, 5)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> str:
    logger.info(f"Чтение PDF: {pdf_path.name}")
    pages = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    pages.append(text)
                else:
                    logger.warning(f"Пустая страница {i + 1} в {pdf_path.name}")

    except Exception as e:
        logger.error(f"Ошибка чтения {pdf_path}: {e}")

    return "\n".join(pages)


def split_into_chunks(text: str) -> list[str]:
    chunks = []

    for i in range(0, len(text), CHUNK_SIZE):
        chunk = text[i : i + CHUNK_SIZE]
        if len(chunk) >= MIN_CHUNK_LEN:
            chunks.append(chunk)

    return chunks


def load_data():
    texts = []
    labels = []

    for lang in ["ru", "de"]:
        folder = DATA_DIR / f"train_{lang}"
        logger.info(f"Загрузка данных из {folder}")

        for pdf_file in folder.glob("*.pdf"):
            text = extract_text_from_pdf(pdf_file)

            if not text.strip():
                logger.warning(f"PDF без текста: {pdf_file.name}")
                continue

            chunks = split_into_chunks(text)
            logger.info(
                f"{pdf_file.name}: получено {len(chunks)} фрагментов"
            )

            for chunk in chunks:
                texts.append(chunk)
                labels.append(lang)

    logger.info(f"Всего обучающих примеров: {len(texts)}")
    logger.info(f"Распределение классов: {Counter(labels)}")

    return texts, labels


def main():
    logger.info("=== Запуск обучения модели ===")

    X, y = load_data()

    if len(set(y)) < 2:
        raise RuntimeError("Недостаточно классов для обучения")

    class_counts = Counter(y)
    min_class_size = min(class_counts.values())

    logger.info(f"Минимальный размер класса: {min_class_size}")

    use_calibration = min_class_size >= 3

    logger.info(f"Calibration: {use_calibration}")

    mlp = MLPClassifier(
        hidden_layer_sizes=(100, 50),
        activation="relu",
        solver="adam",
        max_iter=50,
        alpha=1e-3,
        random_state=42,
        verbose=True,
    )

    if use_calibration:
        classifier = CalibratedClassifierCV(
            estimator=mlp,
            method="sigmoid",
            cv=3,
        )
    else:
        classifier = mlp

    pipeline = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="char",
                    ngram_range=NGRAM_RANGE,
                    max_features=50_000,
                ),
            ),
            ("scaler", StandardScaler(with_mean=False)),
            ("clf", classifier),
        ]
    )

    logger.info("Начало обучения модели...")
    pipeline.fit(X, y)
    logger.info("Обучение завершено")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    logger.info(f"Модель сохранена: {MODEL_PATH}")


if __name__ == "__main__":
    main()
