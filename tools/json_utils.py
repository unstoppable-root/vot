try:
    import orjson
except ImportError:  # pragma: no cover - fallback to builtin json
    orjson = None
import json


def json_dumps(data) -> str:
    """Serialize Python object to JSON string."""
    if orjson:
        return orjson.dumps(data, option=orjson.OPT_NON_STR_KEYS).decode()
    return json.dumps(data, ensure_ascii=False)


def json_loads(data: str):
    """Deserialize JSON string to Python object."""
    if orjson:
        return orjson.loads(data)
    return json.loads(data)
