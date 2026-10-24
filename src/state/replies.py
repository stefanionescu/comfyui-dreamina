"""The parts of the Dreamina CLI's success replies the extension reads; the records ignore unknown fields."""

from pydantic import Field

from . import Json, Reply


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
        type: The flag's value type, such as `string` or `integer`.
        default: The value the CLI uses when the call leaves out the flag.
        constraints: The flag's rule as the schema writes it, such as normal|pro or 1..100.

    """

    name: str
    type: str = ''
    default: Json = None
    constraints: str = ''


class SchemaCommand(Reply):
    """One command and the commands under it.

    Attributes:
        name: The command's own word, such as video.
        flags: Its flags.
        subcommands: The commands under it.

    """

    name: str
    flags: tuple[SchemaFlag, ...] = ()
    subcommands: tuple['SchemaCommand', ...] = ()


class SchemaReply(Reply):
    """The CLI's command tree.

    Attributes:
        schema_version: The schema's format.
        subcommands: The top-level commands.

    """

    schema_version: str = Field(alias='schemaVersion')
    subcommands: tuple[SchemaCommand, ...]


class AuthState(Reply):
    """Whether a sign-in finished.

    Attributes:
        logged_in: True once the person signs in.

    """

    logged_in: bool = Field(alias='loggedIn')


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

    device_code: str = Field(alias='deviceCode', repr=False)
    user_code: str = Field(alias='userCode')
    verification_uri: str = Field(alias='verificationUri')
    verification_uri_complete: str | None = Field(default=None, alias='verificationUriComplete')
    poll_seconds: int = Field(alias='pollSeconds')
    expires_at: str | None = Field(default=None, alias='expiresAt')


class AuthReply(Reply):
    """The reply of auth status, auth login, and auth wait.

    Attributes:
        logged_in: auth status's answer.
        status: auth login's and auth wait's state word, such as logged_in.
        state: Whether the sign-in finished.
        challenge: The device sign-in to approve.

    """

    logged_in: bool | None = Field(default=None, alias='loggedIn')
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

    user_id: int = Field(alias='userId', repr=False)
    is_vip: bool | None = Field(default=None, alias='isVip')
    vip_level: str | None = Field(default=None, alias='vipLevel')


class CanvasProject(Reply):
    """One canvas.

    Attributes:
        project_id: The canvas ID.
        web_url: The canvas's page on Dreamina.

    """

    project_id: str = Field(alias='projectId')
    web_url: str = Field(alias='webUrl')


class CanvasReply(Reply):
    """The reply of canvas create.

    Attributes:
        project: The canvas made, or found again for the same ID.

    """

    project: CanvasProject


class CanvasListReply(Reply):
    """One page of canvas ls.

    Attributes:
        items: The canvases on this page.
        next_cursor: The cursor of the next page.
        has_more: Whether another page follows.

    """

    items: tuple[CanvasProject, ...] = ()
    next_cursor: str | None = Field(default=None, alias='nextCursor')
    has_more: bool = Field(default=False, alias='hasMore')


class UploadReply(Reply):
    """The reply of resource upload.

    Attributes:
        resource_id: The resource ID, echoed.
        media_type: The type Dreamina gave the file.

    """

    resource_id: str = Field(alias='resourceId')
    media_type: str = Field(alias='mediaType')


class DownloadReply(Reply):
    """The reply of resource download.

    Attributes:
        resource_id: The resource ID.
        path: Where the CLI wrote the file; never read, because the pack reads its own path.
        size: The file's size in bytes.
        sha256: The file's SHA-256, in hexadecimal.

    """

    resource_id: str = Field(alias='resourceId')
    path: str
    size: int
    sha256: str


class Voice(Reply):
    """One voice of a speech model.

    Attributes:
        voice_name: The name the voice-name flag takes.

    """

    voice_name: str = Field(alias='voiceName')


class ModelVoices(Reply):
    """One page of a model's voices.

    Attributes:
        items: The voices on this page.
        has_more: Whether another page follows.
        next_offset: The offset of the next page.
        total_count: How many voices the catalog holds.

    """

    items: tuple[Voice, ...] = ()
    has_more: bool = Field(alias='hasMore')
    next_offset: int = Field(alias='nextOffset')
    total_count: int = Field(alias='totalCount')


class VoicePage(Reply):
    """The reply of voice list.

    Attributes:
        models: Each model's page, by canonical name.

    """

    models: dict[str, ModelVoices]


__all__ = [
    'AccountReply',
    'AuthChallenge',
    'AuthReply',
    'AuthState',
    'CanvasListReply',
    'CanvasProject',
    'CanvasReply',
    'DownloadReply',
    'ModelVoices',
    'SchemaCommand',
    'SchemaFlag',
    'SchemaReply',
    'UploadReply',
    'VersionReply',
    'Voice',
    'VoicePage',
]
