import json
import numpy as np
from datetime import datetime
from decimal import Decimal

class CustomJSONEncoder(json.JSONEncoder):
    """Кастомный JSON энкодер для обработки специальных типов данных"""
    
    def default(self, obj):
        # Обрабатываем numpy типы
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.int32, np.int64, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        # Обрабатываем другие типы
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        # Для всех остальных типов используем стандартную обработку
        return super().default(obj)

def safe_jsonify(data):
    """Безопасная сериализация данных в JSON"""
    return json.dumps(data, cls=CustomJSONEncoder, ensure_ascii=False)

def safe_json_response(data):
    """Создает безопасный JSON response для Flask"""
    from flask import Response
    return Response(
        safe_jsonify(data),
        mimetype='application/json; charset=utf-8'
    )