from shopee import shopee_service, data_repo
from netsuite import netsuite_service
from telegram import telegram


def shopee_controller(request) -> dict:
    return (
        shopee_service.get_orders_service()
        .bind(
            netsuite_service.prepare_orders_service(
                data_repo.persist_order,  # type: ignore
                shopee_service.prepared_order_builder,
                telegram.SHOPEE_CHANNEL,
            )
        )
        .map(lambda x: {"controller": "shopee", "results": x})
        .unwrap()
    )
