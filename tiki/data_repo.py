from typing import Optional, Callable
import os

from requests import Session
from authlib.integrations.requests_client import OAuth2Session

from returns.result import ResultE, safe
from google.cloud import firestore

from tiki import tiki
from tiki.tiki_repo import TIKI

BASE_URL = "https://api.tiki.vn/integration"
QUEUE_CODE = (
    "6cd68367-3bde-4aac-a24e-258bc907d68b"
    if os.getenv("PYTHON_ENV") == "prod"
    else "f0c586e1-fb27-4d73-90bb-bcfe31464dba"
)
ORDER = TIKI.collection("Order")


def get_events(
    session: OAuth2Session,
) -> Callable[[Optional[str]], ResultE[tiki.EventRes]]:
    @safe
    def _get(ack_id: Optional[str] = None) -> tiki.EventRes:
        with session.post(
            f"{BASE_URL}/v1/queues/{QUEUE_CODE}/events/pull", json={"ack_id": ack_id}
        ) as r:
            data = r.json()
        return data["ack_id"], data["events"]

    return _get


@safe
def get_ack_id() -> str:
    return TIKI.get(["state.ack.ack_id"]).get("state.ack.ack_id")


@safe
def update_ack_id(ack_id: str) -> str:
    TIKI.set(
        {
            "state": {
                "ack": {
                    "ack_id": ack_id,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                }
            }
        },
        merge=True,
    )
    return ack_id


def extract_order(event: tiki.Event) -> str:
    return event["payload"]["order_code"]


def get_order(session: Session) -> Callable[[str], ResultE[tiki.Order]]:
    @safe
    def _get(order_id: str) -> tiki.Order:
        with session.get(
            f"{BASE_URL}/v2/orders/{order_id}",
            params={"include": "items.fees"},
        ) as r:
            data = r.json()
        return {
            "id": data["id"],
            "code": data["code"],
            "items": [
                {
                    "product": {
                        "name": item["product"]["name"],
                        "seller_product_code": item["product"]["seller_product_code"],
                    },
                    "seller_income_detail": {
                        "item_qty": item["seller_income_detail"]["item_qty"],
                        "sub_total": item["seller_income_detail"]["sub_total"],
                    },
                }
                for item in data["items"]
            ],
            "shipping": {
                "address": {
                    "full_name": data["shipping"]["address"]["full_name"],
                    "street": data["shipping"]["address"]["street"],
                    "ward": data["shipping"]["address"]["ward"],
                    "district": data["shipping"]["address"]["district"],
                    "phone": data["shipping"]["address"]["phone"],
                },
            },
        }

    return _get


@safe
def persist_tiki_order(order: tiki.Order) -> tiki.Order:
    doc_ref = ORDER.document()
    doc_ref.create({"order": order, "updated_at": firestore.SERVER_TIMESTAMP})
    return order
