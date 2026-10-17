"""Serve the routes of Dreamina Settings: the status, the request limits, sign-in, sign-out, and the CLI install."""

import re
import asyncio
from aiohttp import web
from ..types import Json
from ..config.security import ROUTES
from ..settings.body import read_body
from ..types.parsing import validate_fields
from ..config.dreamina import MINIMUM_VERSION
from ..config.patterns import REVISION_PATTERN
from ..settings.access import build_local_route
from ..settings.store import ConfigurationStore
from ..dreamina.contract import is_current_version
from ..types.errors import ErrorCode, DreaminaError
from ..config.messages.requests import BODY_NOT_ALLOWED
from ..config.messages.requests import SETTINGS_REVISION_REQUIRED
from ..dreamina.installer import save_cli, read_cli_version, download_installer
from ..dreamina.account import SignInState, is_signed_in, read_account, delete_sign_in


REVISION = re.compile(REVISION_PATTERN)


class SettingsRoutes:
    """Register the routes of Dreamina Settings once during the host's extension load phase.

    The status never holds the account's ID, the device code, the CLI's profile or region, an install command, or the
    canvas.
    """

    def __init__(self, configuration: ConfigurationStore, sign_in: SignInState, *, is_multi_user: bool = False) -> None:
        """Bind the settings store, the pending sign-in, and the host's multi-user access policy."""
        self.configuration = configuration
        self.sign_in = sign_in
        self.is_multi_user = is_multi_user

    async def _read_account_status(self, *, is_found: bool) -> dict[str, Json]:
        """Describe the account: signed in or not, and its plan when Dreamina can say.

        A failed status read shows signed out. A failed account read shows signed out only when the sign-in is the
        cause; otherwise the account stays signed in with its plan unknown.
        """
        signed_out: dict[str, Json] = {"signed_in": False, "is_vip": None, "vip_level": None}
        try:
            is_signed = is_found and await is_signed_in()
        except DreaminaError:
            is_signed = False
        if not is_signed:
            return signed_out
        try:
            account = await read_account()
        except DreaminaError as error:
            is_signed = error.code is not ErrorCode.AUTHENTICATION
            return {"signed_in": is_signed, "is_vip": None, "vip_level": None}
        return {"signed_in": True, "is_vip": account.is_vip, "vip_level": account.vip_level}

    async def read_status(self, _request: web.Request) -> dict[str, Json]:
        """Describe the settings, the CLI, the account, and any pending sign-in; every route returns it."""
        status = await asyncio.to_thread(self.configuration.read_status)
        version = await read_cli_version()
        cli: dict[str, Json] = {
            "found": version is not None,
            "version": version,
            "minimum_version": MINIMUM_VERSION,
            "is_current": is_current_version(version),
        }
        state: dict[str, Json] = {
            "cli": cli,
            "account": await self._read_account_status(is_found=version is not None),
            "sign_in": self.sign_in.build_status(),
            "mutation_allowed": not self.is_multi_user,
        }
        return status | state

    async def save_settings(self, request: web.Request) -> dict[str, Json]:
        """Validate a request limits patch, save it against the caller's current revision, and return the status."""
        document = await read_body(request)
        revision = document.get("revision")
        if document.keys() != {"revision", "settings"} or not isinstance(revision, str) or not REVISION.match(revision):
            raise web.HTTPBadRequest(text=SETTINGS_REVISION_REQUIRED)
        await asyncio.to_thread(self.configuration.save_settings, validate_fields(document["settings"]), revision)
        return await self.read_status(request)

    async def create_session(self, request: web.Request) -> dict[str, Json]:
        """Start a new sign-in, replacing any pending one, and return the status with its code and link."""
        if request.can_read_body:
            raise web.HTTPBadRequest(text=BODY_NOT_ALLOWED)
        await self.sign_in.create_challenge()
        return await self.read_status(request)

    async def delete_session(self, request: web.Request) -> dict[str, Json]:
        """Stop any pending sign-in, sign the CLI out, and renew the account token."""
        if request.can_read_body:
            raise web.HTTPBadRequest(text=BODY_NOT_ALLOWED)
        await self.sign_in.reset()
        await delete_sign_in()
        self.configuration.reset_account_token()
        return await self.read_status(request)

    async def save_release(self, request: web.Request) -> dict[str, Json]:
        """Install or update the CLI with the official installer, then return the status with the new release."""
        if request.can_read_body:
            raise web.HTTPBadRequest(text=BODY_NOT_ALLOWED)
        await save_cli(await download_installer())
        return await self.read_status(request)

    def register(self, routes: web.RouteTableDef) -> None:
        """Register the guarded status, request limits, sign-in, sign-out, and install routes."""
        policy = {"is_multi_user": self.is_multi_user}
        routes.get(ROUTES["STATUS"])(build_local_route(self.read_status, is_mutation=False, **policy))
        routes.patch(ROUTES["SETTINGS"])(build_local_route(self.save_settings, is_mutation=True, **policy))
        routes.post(ROUTES["SESSION"])(build_local_route(self.create_session, is_mutation=True, **policy))
        routes.delete(ROUTES["SESSION"])(build_local_route(self.delete_session, is_mutation=True, **policy))
        routes.post(ROUTES["CLI"])(build_local_route(self.save_release, is_mutation=True, **policy))


__all__ = ["SettingsRoutes"]
