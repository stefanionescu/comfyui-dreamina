"""Describe a workflow as nodes, links, groups, and the subgraphs it places."""

from __future__ import annotations

import uuid
from types import MappingProxyType
from typing import TYPE_CHECKING
from dataclasses import dataclass

from scripts.workflows.page.config import INPUT_COLOUR

if TYPE_CHECKING:
    from collections.abc import Mapping

    from scripts.types import WidgetValue

NO_VALUES: Mapping[str, WidgetValue] = MappingProxyType({})
NAMESPACE = uuid.UUID('05f62da6-1302-4067-b6d8-e83cf4a52f83')


@dataclass(frozen=True, slots=True)
class Node:
    """One node, with the widget values that differ from its defaults; a bypassed node ships switched off.

    Attributes:
        key: The name that links and groups use for the node inside its workflow or subgraph.
        kind: The name ComfyUI registers the node under, or the name of a subgraph.
        values: The widget values that differ from the defaults, by input name.
        title: The title the page shows; an empty one keeps the node's own.
        is_paid: Whether the page draws the node in the colours of a paid request.
        is_bypassed: Whether the node ships bypassed.

    """

    key: str
    kind: str
    values: Mapping[str, WidgetValue] = NO_VALUES
    title: str = ''
    is_paid: bool = False
    is_bypassed: bool = False


@dataclass(frozen=True, slots=True)
class Group:
    """One titled frame around columns of nodes, with a note above it that says what the group does.

    Attributes:
        title: The title of the frame, which no other group of the workflow has.
        columns: The node keys, one tuple per column from left to right, each from top to bottom.
        colour: The colour of the frame.
        note: The text of the note above the frame.

    """

    title: str
    columns: tuple[tuple[str, ...], ...]
    colour: str = INPUT_COLOUR
    note: str = ''


@dataclass(frozen=True, slots=True)
class Subgraph:
    """A reusable graph placed as one node; each link runs from `node.output` to `node.input`.

    Attributes:
        name: The name of the subgraph, which a node's kind uses to place it and which names its blueprint file.
        nodes: The nodes inside the subgraph.
        links: The links between the inner nodes.
        columns: The keys of the inner nodes, one tuple per column.
        inputs: The exposed inputs, each as its name and the inner `node.input` it feeds.
        outputs: The exposed outputs, each as its name and the inner `node.output` it reads.
        description: The text ComfyUI shows for the blueprint.
        previews: The previews shown on the placed node, each as a node key and a preview name.

    """

    name: str
    nodes: tuple[Node, ...]
    links: tuple[tuple[str, str], ...]
    columns: tuple[tuple[str, ...], ...] = ()
    inputs: tuple[tuple[str, str], ...] = ()
    outputs: tuple[tuple[str, str], ...] = ()
    description: str = ''
    # The previews shown on the placed node, as `node key` and preview name.
    previews: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class Workflow:
    """One shipped workflow; each link runs from `node.output` to `node.input`.

    Attributes:
        slug: The name of the workflow's file, without the extension.
        nodes: The nodes on the page.
        links: The links between those nodes.
        stacks: The groups, one tuple per stack. Stacks sit side by side, and the groups of a stack sit one under
            the other.
        subgraphs: The subgraphs the workflow defines.

    """

    slug: str
    nodes: tuple[Node, ...]
    links: tuple[tuple[str, str], ...]
    stacks: tuple[tuple[Group, ...], ...]
    subgraphs: tuple[Subgraph, ...] = ()


__all__ = ['NAMESPACE', 'NO_VALUES', 'Group', 'Node', 'Subgraph', 'Workflow']
