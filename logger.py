"""Настройка логирования для проекта."""
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s — %(levelname)s — %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)
