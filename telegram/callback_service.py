import json

from returns.pipeline import flow
from returns.pointfree import bind
from returns.result import ResultE, Failure

from telegram import telegram, telegram_repo, callback_repo


def validation_service(update: telegram.Update) -> ResultE[telegram.CalbackData]:
    return flow(
        update,
        telegram_repo.answer_callback,
        callback_repo.validate_update,
        bind(callback_repo.validate_callback),
        bind(callback_repo.validate_data),
    )


def match_service(data: telegram.CalbackData):
    if data["t"] == "O":
        if data["a"] == 1:
            pass
        elif data["a"] == -1:
            pass
    return Failure(f"Operation not supported {json.dumps(data)}")
