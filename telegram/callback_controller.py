from typing import Optional, Union
import json

from returns.result import Result, Success, Failure

from telegram import telegram, callback_service
from netsuite import netsuite_service


def service_factory(
    data: telegram.CalbackData,
) -> Result[Optional[str], Union[str, Exception]]:
    if data["t"] == "O":
        if data["a"] == 1:
            return netsuite_service.create_order_service(data["v"])
    return Failure(f"Operation not supported {json.dumps(data)}")


def callback_controller(request_data: telegram.Update) -> dict:
    return (
        callback_service.validation_service(request_data)
        .bind(service_factory)  # type: ignore
        .lash(lambda x: Success(x))
        .map(
            lambda x: {
                "controller": "callback",
                "detail": x,
            }
        )
        .unwrap()
    )