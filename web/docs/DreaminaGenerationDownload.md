# Generation: Download

Downloads what Dreamina made for a run after the run stopped: you canceled
it, ComfyUI restarted, or it took longer than the request timeout. Dreamina
keeps working on a run it accepted, and bills it. This node bills nothing.

## Inputs

| Input        | What it takes                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------- |
| `generation` | A run started on this server, shown as the start of its ID, its model, and its start time in UTC. |

## Outputs

| Output       | What it carries                                        |
| ------------ | ------------------------------------------------------ |
| `images`     | Every image the run made.                              |
| `video`      | Every video the run made.                              |
| `audio`      | Every audio file the run made.                         |
| `references` | What the run made, for the next Dreamina node.         |
| `result`     | The run's canvas node as Dreamina returns it, as JSON. |

## Use

1. Choose the run in `generation`. Press R to list runs started after the
   page loaded.
2. Connect the output you need, such as `video` to **Save Video**.
3. Select **Run**.

A run leaves the list once a node downloads its outputs, or when Dreamina
cannot find it. An upscale shows `upscale` as its model. Outputs the run did
not make stop the nodes connected to them. Example:
**video-04-recover-a-video**.

[Dreamina Canvas CLI](https://dreamina.capcut.com/canvas-cli)
