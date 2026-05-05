import logging
import logging.handlers
from pathlib import Path

from pythonjsonlogger.json import JsonFormatter


class HumanFormatter(logging.Formatter):
    LEVEL_COLORS = {
        "DEBUG": "\033[37m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        ts = self.formatTime(record, "%H:%M:%S")
        level = f"{record.levelname:<8}"
        color = self.LEVEL_COLORS.get(record.levelname, "")

        event = getattr(record, "event", None)
        item_id = getattr(record, "item_id", None)
        actor = getattr(record, "actor", None)

        parts = [record.getMessage()]
        if event:
            parts = [event]
        if item_id:
            parts.append(item_id)
        if actor:
            parts.append(f"actor={actor}")

        body = "  ".join(parts)
        return f"{ts}  {color}{level}{self.RESET}  {body}"


def setup_logging() -> None:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    json_formatter = JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
    )

    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setFormatter(json_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(HumanFormatter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(file_handler)
    root.addHandler(stream_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
