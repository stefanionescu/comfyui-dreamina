"""The parts of the Dreamina CLI's success replies the extension reads; unknown fields are ignored."""

from . import Json, Reply
from pydantic import Field
from .cli import Validation


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


class CanvasProject(Reply):
    """One canvas.

    Attributes:
        project_id: The canvas ID.
        web_url: The canvas's page on Dreamina.

    """

    project_id: str = Field(alias="projectId")
    web_url: str = Field(alias="webUrl")


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
    next_cursor: str | None = Field(default=None, alias="nextCursor")
    has_more: bool = Field(default=False, alias="hasMore")


class NodeResource(Reply):
    """One resource of a canvas node.

    Attributes:
        resource_id: The resource ID.
        type: image, video, or audio.
        status: The resource's status, such as success.
        submit_id: The run that made it.

    """

    resource_id: str = Field(alias="resourceId")
    type: str
    status: str
    submit_id: str | None = Field(default=None, alias="submitId")


class NodeView(Reply):
    """The parts of a canvas node the pack reads.

    Attributes:
        node_id: The node ID.
        title: The node's title.
        resources: The node's resources, in the node's order.

    """

    node_id: str = Field(alias="nodeId")
    title: str | None = None
    resources: tuple[NodeResource, ...] = ()


class RunSubmission(Reply):
    """The submission a run call made.

    Attributes:
        submit_id: The run's submit ID.
        state: The submission's state on acceptance, such as accepted.

    """

    submit_id: str = Field(alias="submitId")
    state: str


class RunReply(Reply):
    """The reply of node create with --run.

    Attributes:
        node: The saved node.
        submission: The run submitted.

    """

    node: NodeView
    submission: RunSubmission


class OperationResource(Reply):
    """One resource of an operation.

    Attributes:
        resource_id: The resource ID.
        state: The resource's state, such as succeeded.
        status_code: Dreamina's code for a failed resource.
        required_action: What Dreamina says must happen next.

    """

    resource_id: str = Field(alias="resourceId")
    state: str
    status_code: int | None = Field(default=None, alias="serviceCode")
    required_action: str | None = Field(default=None, alias="requiredAction")


class Submission(Reply):
    """An operation's submission.

    Attributes:
        state: The submission's state, such as completed or absent.

    """

    state: str


class SubmissionError(Reply):
    """Why a submission failed.

    Attributes:
        status_code: Dreamina's code for the failure.
        message: Dreamina's text, shown cleaned.
        reason: A finer cause.
        required_action: What Dreamina says must happen next.
        validation: The refused value, when Dreamina names one.

    """

    status_code: int | None = Field(default=None, alias="serviceCode")
    message: str = ""
    reason: str | None = None
    required_action: str | None = Field(default=None, alias="requiredAction")
    validation: Validation | None = None


class OperationReply(Reply):
    """The reply of operation wait and operation status.

    Attributes:
        resources: The operation's resources.
        submission: The operation's submission.
        submission_error: Why the submission failed, when it did.

    """

    resources: tuple[OperationResource, ...] = ()
    submission: Submission | None = None
    submission_error: SubmissionError | None = Field(default=None, alias="submissionError")


class NodeShowItem(Reply):
    """One item of node show.

    Attributes:
        node: The whole node as JSON; None for a node Dreamina did not find.

    """

    node: dict[str, Json] | None = None


class NodeShowReply(Reply):
    """The reply of node show.

    Attributes:
        nodes: One item per node asked for.

    """

    nodes: tuple[NodeShowItem, ...] = ()


class UploadReply(Reply):
    """The reply of resource upload.

    Attributes:
        resource_id: The resource ID, echoed.
        media_type: The type Dreamina gave the file.

    """

    resource_id: str = Field(alias="resourceId")
    media_type: str = Field(alias="mediaType")


class DownloadReply(Reply):
    """The reply of resource download.

    Attributes:
        resource_id: The resource ID.
        path: Where the CLI wrote the file; never read, since the pack reads its own path.
        size: The file's size in bytes.
        sha256: The file's SHA-256, in hexadecimal.

    """

    resource_id: str = Field(alias="resourceId")
    path: str
    size: int
    sha256: str


__all__ = [
    "AccountReply",
    "AuthChallenge",
    "AuthReply",
    "AuthState",
    "CanvasListReply",
    "CanvasProject",
    "CanvasReply",
    "DownloadReply",
    "NodeResource",
    "NodeShowItem",
    "NodeShowReply",
    "NodeView",
    "OperationReply",
    "OperationResource",
    "RunReply",
    "RunSubmission",
    "SchemaCommand",
    "SchemaFlag",
    "SchemaReply",
    "Submission",
    "SubmissionError",
    "UploadReply",
    "VersionReply",
]
