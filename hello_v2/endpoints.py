from starlette.responses import UJSONResponse
from starlette.responses import Response
from starlette.requests import Request
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.routing import Route, Router
from pprint import pprint


import json
import hashlib
import os
import gzip
import asyncio

from starlette.responses import JSONResponse

# import jsonschema


from gzip_router import GzipRouter
import logging

logger = logging.getLogger(__name__)

hello_api = GzipRouter()


@hello_api.route('/', methods=["POST"])
async def my_hello( request ):
    body = await request.body()
    data = json.loads(body)
    print (f"Version 2 Received: {data}")
    return JSONResponse({"code":200, "message": f"Hello 2 {data['name']}"})
