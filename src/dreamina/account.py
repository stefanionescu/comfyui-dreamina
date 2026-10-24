"""Sign in, sign out, and read the account through the Dreamina CLI, keeping the device code on the server."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Literal
import asyncio
from datetime import UTC, datetime, timedelta

from .cli import parse_reply, send_command
from .failures import build_failure
from ..state.errors import ErrorCode, DreaminaError
from ..state.replies import AuthReply, AccountReply
from ..config.dreamina import SIGN_IN_SECONDS, ACCOUNT_TIMEOUTS, SIGN_IN_FAILURES
from ..config.messages.run import CLI_FAILED
from ..config.messages.settings import SIGN_IN_CODE_MISSING

if TYPE_CHECKING:
    from collections.abc import Callable

    from ..state import Json
    from ..state.replies import AuthChallenge

# Where a pending sign-in stands: waiting for approval, past its expiry, or stopped by an error.
type SignInPhase = Literal['waiting', 'expired', 'failed']


async def _create_sign_in() -> AuthChallenge | None:
    """Start a device sign-in and return its challenge; None when the CLI is already signed in."""
    result = await send_command(('auth', 'login'), ACCOUNT_TIMEOUTS['NETWORK'])
    if not result.reply.ok:
        raise build_failure(result, CLI_FAILED)
    reply = parse_reply(result.reply.payload, AuthReply)
    if reply.challenge is None and (reply.state is None or not reply.state.logged_in):
        raise DreaminaError(ErrorCode.AUTHENTICATION, SIGN_IN_CODE_MISSING)
    return reply.challenge


def _read_expiry(challenge: AuthChallenge) -> datetime:
    """Return when a challenge ends, in UTC; SIGN_IN_SECONDS from now when the CLI gives no readable time."""
    default_expiry = datetime.now(UTC) + timedelta(seconds=SIGN_IN_SECONDS)
    try:
        expires_at = datetime.fromisoformat(challenge.expires_at) if challenge.expires_at else default_expiry
    except ValueError:
        return default_expiry
    return expires_at.astimezone(UTC) if expires_at.tzinfo is not None else expires_at.replace(tzinfo=UTC)


async def _wait_for_sign_in(challenge: AuthChallenge, expires_at: datetime) -> bool:
    """Wait for the person's approval; True once approved, False once the challenge expired.

    When a wait reaches its own timeout, the loop sends it again with the same device code. The timeout is a Go
    duration, because the CLI refuses a bare number. Only error codes decide, never the message text.
    """
    while (remaining := math.ceil((expires_at - datetime.now(UTC)).total_seconds())) > 0:
        arguments = ('auth', 'wait', '--device-code', challenge.device_code, '--timeout', f'{remaining}s')
        result = await send_command(arguments, remaining + ACCOUNT_TIMEOUTS['WAIT_MARGIN'])
        code = result.reply.error.code if result.reply.error is not None else None
        if result.reply.ok or code == SIGN_IN_FAILURES['EXPIRED']:
            return result.reply.ok
        if code != SIGN_IN_FAILURES['WAIT_TIMEOUT']:
            raise build_failure(result, CLI_FAILED)
    return False


async def is_signed_in() -> bool:
    """Whether the CLI holds a sign-in, read on this computer without calling Dreamina."""
    result = await send_command(('auth', 'status'), ACCOUNT_TIMEOUTS['LOCAL'])
    if not result.reply.ok:
        raise build_failure(result, CLI_FAILED)
    return parse_reply(result.reply.payload, AuthReply).logged_in is True


async def read_account() -> AccountReply:
    """Read the signed-in account from Dreamina; a signed-out CLI raises the sign-in error."""
    result = await send_command(('auth', 'account'), ACCOUNT_TIMEOUTS['NETWORK'])
    if not result.reply.ok:
        raise build_failure(result, CLI_FAILED)
    return parse_reply(result.reply.payload, AccountReply)


async def delete_sign_in() -> None:
    """Sign the CLI out on this computer."""
    result = await send_command(('auth', 'logout'), ACCOUNT_TIMEOUTS['LOCAL'])
    if not result.reply.ok:
        raise build_failure(result, CLI_FAILED)


class SignInState:
    """The one pending sign-in, kept in memory on the server loop.

    An asyncio lock makes a new sign-in and a reset take turns across their awaits; no other thread touches it. The
    state keeps the only reference to its wait task, and stopping the task kills its auth wait child.
    """

    def __init__(self, reset_account: Callable[[], None]) -> None:
        """Keep the account token's reset, which runs once the person approves a sign-in."""
        self._reset_account = reset_account
        self._lock = asyncio.Lock()
        self._task: asyncio.Task[None] | None = None
        self._challenge: AuthChallenge | None = None
        self._expires_at: datetime | None = None
        self._state: SignInPhase | None = None
        self._message: str | None = None

    async def _delete_wait(self) -> None:
        """Cancel the running wait, if any, and wait for it to end."""
        task, self._task = self._task, None
        if task is not None:
            task.cancel()
            await asyncio.wait((task,))

    def _reset_challenge(self) -> None:
        """Forget the challenge, its state, and its message."""
        self._challenge = None
        self._expires_at = None
        self._state = None
        self._message = None

    async def _wait_for_approval(self, challenge: AuthChallenge, expires_at: datetime) -> None:
        """Follow a sign-in to its end, renewing the account token once the person approves it; a cancel propagates."""
        try:
            is_approved = await _wait_for_sign_in(challenge, expires_at)
        except DreaminaError as error:
            self._state, self._message = 'failed', str(error)
            return
        if is_approved:
            self._reset_challenge()
            self._reset_account()
        else:
            self._state = 'expired'

    async def create_challenge(self) -> None:
        """Replace any pending sign-in with a new one and wait for its approval in the background."""
        async with self._lock:
            await self._delete_wait()
            self._reset_challenge()
            challenge = await _create_sign_in()
            if challenge is not None:
                self._challenge = challenge
                self._expires_at = _read_expiry(challenge)
                self._state = 'waiting'
                self._task = asyncio.create_task(self._wait_for_approval(challenge, self._expires_at))

    async def reset(self) -> None:
        """Stop the pending sign-in and forget it."""
        async with self._lock:
            await self._delete_wait()
            self._reset_challenge()

    def build_status(self) -> dict[str, Json] | None:
        """Describe the pending sign-in for Dreamina Settings, never with its device code; None when there is none."""
        challenge, expires_at = self._challenge, self._expires_at
        if challenge is None or expires_at is None:
            return None
        is_expired = self._state == 'waiting' and datetime.now(UTC) >= expires_at
        return {
            'state': 'expired' if is_expired else self._state,
            'user_code': challenge.user_code,
            'verification_url': challenge.verification_uri_complete or challenge.verification_uri,
            'expires_at': expires_at.isoformat(timespec='seconds'),
            'message': self._message if self._state == 'failed' else None,
        }


__all__ = ['SignInState', 'delete_sign_in', 'is_signed_in', 'read_account']
