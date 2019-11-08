import gzip
import asyncio
import inspect
import typing

from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.concurrency import run_in_threadpool


class GzipRequest(Request):
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = await super().body()
            if "gzip" in str(self.headers.getlist("Content-Encoding")):
                body = gzip.decompress(body)
            self._body = body
        return self._body



def custom_request_response(func: typing.Callable) -> ASGIApp:
    """
    Takes a function or coroutine `func(request) -> response`,
    and returns an ASGI application.
    """
    is_coroutine = asyncio.iscoroutinefunction(func)

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        request = GzipRequest(scope, receive=receive, send=send)
        if is_coroutine:
            response = await func(request)
        else:
            response = await run_in_threadpool(func, request)
        await response(scope, receive, send)

    return app


class GzipRoute(Route):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if inspect.isfunction(self.endpoint) or inspect.ismethod(self.endpoint):
            self.app = custom_request_response(self.endpoint)

class GzipRouter(Router):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)       
         
    def add_route(
        self,
        path: str,
        endpoint: typing.Callable,
        methods: typing.List[str] = None,
        name: str = None,
        include_in_schema: bool = True,
    ) -> None:
        route = GzipRoute(
            path,
            endpoint=endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )
        self.routes.append(route)