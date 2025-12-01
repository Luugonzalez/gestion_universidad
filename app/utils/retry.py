import time
import logging
from functools import wraps

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry con delay exponencial para operaciones externas."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logging.error(
                            f"[RETRY] Falló definitivamente después de {max_attempts} intentos en {func.__name__}: {e}"
                        )
                        raise
                    wait = delay * (2 ** (attempt - 1))
                    logging.warning(
                        f"[RETRY] Intento {attempt} falló en {func.__name__}. "
                        f"Reintentando en {wait}s. Error: {e}"
                    )
                    time.sleep(wait)
                    attempt += 1
        return wrapper
    return decorator
