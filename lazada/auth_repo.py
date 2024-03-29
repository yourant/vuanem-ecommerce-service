import time

import requests
from returns.result import safe

from lazada import lazada, lazada_repo

auth_request = lazada_repo.build_lazada_request("https://api.lazada.com/rest")


@safe
def get_access_token() -> lazada.AccessToken:
    return lazada_repo.LAZADA.get(["state.access_token"]).get("state.access_token")


@safe
def update_access_token(token: lazada.AccessToken) -> lazada.AccessToken:
    lazada_repo.LAZADA.set({"state": {"access_token": token}}, merge=True)
    return token


@safe
def refresh_token(
    session: requests.Session,
    token: lazada.AccessToken,
) -> lazada.AccessToken:
    with session.send(
        auth_request(
            "/auth/token/refresh",
            {"refresh_token": token["refresh_token"]},
        )
    ) as r:
        res = r.json()
    return {
        **res,  # type: ignore
        "expires_at": int(time.time()) + int(res["expires_in"]),
    }
