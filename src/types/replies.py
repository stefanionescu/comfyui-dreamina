"""The parts of the Dreamina CLI's success replies the extension reads; unknown fields are ignored."""

from . import Reply
from pydantic import Field


class VersionReply(Reply):
    """The installed release.

    Attributes:
        version: The release, such as 1.0.3.

    """

    version: str


class SchemaFlag(Reply):
    """One flag of a command.

    Attributes:
        name: The flag's name without its dashes.

    """

    name: str


class SchemaCommand(Reply):
    """One command and the commands under it.

    Attributes:
        name: The command's own word, such as video.
        flags: Its flags.
        subcommands: The commands under it.

    """

    name: str
    flags: tuple[SchemaFlag, ...] = ()
    subcommands: tuple["SchemaCommand", ...] = ()


class SchemaReply(Reply):
    """The CLI's command tree.

    Attributes:
        schema_version: The schema's format.
        subcommands: The top-level commands.

    """

    schema_version: str = Field(alias="schemaVersion")
    subcommands: tuple[SchemaCommand, ...]


class AuthState(Reply):
    """Whether a sign-in finished.

    Attributes:
        logged_in: True once the account is signed in.

    """

    logged_in: bool = Field(alias="loggedIn")


class AuthChallenge(Reply):
    """A device sign-in the person approves in a browser.

    Attributes:
        device_code: The code auth wait follows; it never leaves the server.
        user_code: The code the person checks on the approval page.
        verification_uri: The approval page.
        verification_uri_complete: The approval page with the code filled in.
        poll_seconds: How often the CLI checks for approval.
        expires_at: When the challenge ends, in ISO 8601.

    """

    device_code: str = Field(alias="deviceCode", repr=False)
    user_code: str = Field(alias="userCode")
    verification_uri: str = Field(alias="verificationUri")
    verification_uri_complete: str | None = Field(default=None, alias="verificationUriComplete")
    poll_seconds: int = Field(alias="pollSeconds")
    expires_at: str | None = Field(default=None, alias="expiresAt")


class AuthReply(Reply):
    """The reply of auth status, auth login, and auth wait.

    Attributes:
        logged_in: auth status's answer.
        status: auth login's and auth wait's state word, such as logged_in.
        state: Whether the sign-in finished.
        challenge: The device sign-in to approve.

    """

    logged_in: bool | None = Field(default=None, alias="loggedIn")
    status: str | None = None
    state: AuthState | None = None
    challenge: AuthChallenge | None = None


class AccountReply(Reply):
    """The signed-in account.

    Attributes:
        user_id: The account's ID, used only for the cache token and never kept.
        is_vip: Whether the account has a paid plan.
        vip_level: The plan's name, such as standard.

    """

    user_id: int = Field(alias="userId", repr=False)
    is_vip: bool | None = Field(default=None, alias="isVip")
    vip_level: str | None = Field(default=None, alias="vipLevel")


__all__ = [
    "AccountReply",
    "AuthChallenge",
    "AuthReply",
    "AuthState",
    "SchemaCommand",
    "SchemaFlag",
    "SchemaReply",
    "VersionReply",
]
