from __future__ import annotations

from typing import Any, Callable, Dict, Literal, TypeVar, Union, overload

from pydantic import BaseModel
from typing_extensions import Self

from ..helpers import handle_exception
from ..http_clients import SyncClient

T = TypeVar("T")


class SyncGoTrueBaseAPI:
    def __init__(
        self,
        *,
        url: str,
        headers: Dict[str, str],
        http_client: Union[SyncClient, None],
    ):
        self._url = url
        self._headers = headers
        self._http_client = http_client or SyncClient()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_t, exc_v, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        self._http_client.aclose()

    @overload
    def _request(
        self,
        method: Literal["GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"],
        path: str,
        *,
        jwt: Union[str, None] = None,
        redirect_to: Union[str, None] = None,
        headers: Union[Dict[str, str], None] = None,
        query: Union[Dict[str, str], None] = None,
        body: Union[Any, None] = None,
        no_resolve_json: Union[bool, None] = None,
        xform: Callable[[Any], T],
    ) -> T:
        ...

    @overload
    def _request(
        self,
        method: Literal["GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"],
        path: str,
        *,
        jwt: Union[str, None] = None,
        redirect_to: Union[str, None] = None,
        headers: Union[Dict[str, str], None] = None,
        query: Union[Dict[str, str], None] = None,
        body: Union[Any, None] = None,
        no_resolve_json: Union[bool, None] = None,
    ) -> None:
        ...

    def _request(
        self,
        method: Literal["GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"],
        path: str,
        *,
        jwt: Union[str, None] = None,
        redirect_to: Union[str, None] = None,
        headers: Union[Dict[str, str], None] = None,
        query: Union[Dict[str, str], None] = None,
        body: Union[Any, None] = None,
        no_resolve_json: Union[bool, None] = None,
        xform: Union[Callable[[Any], T], None] = None,
    ) -> Union[T, None]:
        url = f"{self._url}/{path}"
        headers = {**self._headers, **(headers or {})}
        if jwt:
            headers["Authorization"] = f"Bearer {jwt}"
        query = query or {}
        if redirect_to:
            query["redirect_to"] = redirect_to
        try:
            response = self._http_client.request(
                method,
                url,
                headers=headers,
                params=query,
                json=body.dict() if isinstance(body, BaseModel) else body,
            )
            response.raise_for_status()
            result = response if no_resolve_json else response.json()
            if xform:
                return xform(result)
        except Exception as e:
            raise handle_exception(e)