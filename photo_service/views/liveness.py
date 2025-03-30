"""Resource module for liveness resources."""

import logging
import os

from aiohttp import web


class Ready(web.View):
    """Class representing ready resource."""

    async def get(self) -> web.Response:
        """Alive function."""
        return web.Response(text="OK")


class Ping(web.View):
    """Class representing ping resource."""

    @staticmethod
    async def get() -> web.Response:
        """Ping route function."""
        return web.Response(text="OK")
