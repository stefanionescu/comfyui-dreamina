"""The parts of the Dreamina CLI's replies about canvas nodes and the runs, elements, and upscales on them.

The records ignore unknown fields.
"""

from pydantic import Field

from . import Json, Reply
from .cli import Validation


class NodeResource(Reply):
    """One resource of a canvas node.

    Attributes:
        resource_id: The resource ID.
        type: image, video, or audio.
        status: The resource's status, such as success.
        submit_id: The run that made it.

    """

    resource_id: str = Field(alias='resourceId')
    type: str
    status: str
    submit_id: str | None = Field(default=None, alias='submitId')


class NodeView(Reply):
    """The parts of a canvas node the pack reads.

    Attributes:
        node_id: The node ID.
        title: The title of the node.
        resources: The resources of the node, in its order.

    """

    node_id: str = Field(alias='nodeId')
    title: str | None = None
    resources: tuple[NodeResource, ...] = ()


class RunSubmission(Reply):
    """The submission a run call made.

    Attributes:
        submit_id: The run's submit ID.
        state: The submission's state on acceptance, such as accepted.

    """

    submit_id: str = Field(alias='submitId')
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

    resource_id: str = Field(alias='resourceId')
    state: str
    status_code: int | None = Field(default=None, alias='serviceCode')
    required_action: str | None = Field(default=None, alias='requiredAction')


class Submission(Reply):
    """An operation's submission.

    Attributes:
        state: The submission's state, such as `completed` or `absent`.

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

    status_code: int | None = Field(default=None, alias='serviceCode')
    message: str = ''
    reason: str | None = None
    required_action: str | None = Field(default=None, alias='requiredAction')
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
    submission_error: SubmissionError | None = Field(default=None, alias='submissionError')


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


class ElementReply(Reply):
    """The reply of node create element and of an import with node create image --resource-id.

    Attributes:
        node: The saved node.

    """

    node: NodeView


class UpscaleError(Reply):
    """Why Dreamina refused one image of an upscale.

    Attributes:
        status_code: Dreamina's code for the refusal.
        message: Dreamina's text, shown cleaned.

    """

    status_code: int | None = Field(default=None, alias='serviceCode')
    message: str = ''


class UpscaleItem(Reply):
    """One image of an upscale.

    Attributes:
        source_node_id: The image node upscaled.
        submit_id: The upscale's submit ID for this image.
        node_id: The new node that holds the upscaled image; None when Dreamina refused it.
        resource_ids: The new resources.
        state: The item's state, such as ACCEPTED.
        error: Why Dreamina refused it.

    """

    source_node_id: str = Field(alias='sourceNodeId')
    submit_id: str = Field(alias='submitId')
    node_id: str | None = Field(default=None, alias='nodeId')
    resource_ids: tuple[str, ...] = Field(default=(), alias='resourceIds')
    state: str
    error: UpscaleError | None = None


class UpscaleReply(Reply):
    """The reply of node upscale image.

    Attributes:
        items: One item per image, matched to the sources by source node ID.

    """

    items: tuple[UpscaleItem, ...] = ()


__all__ = [
    'ElementReply',
    'NodeResource',
    'NodeShowItem',
    'NodeShowReply',
    'NodeView',
    'OperationReply',
    'OperationResource',
    'RunReply',
    'RunSubmission',
    'Submission',
    'SubmissionError',
    'UpscaleError',
    'UpscaleItem',
    'UpscaleReply',
]
