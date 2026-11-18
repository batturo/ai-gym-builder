# AI Gym Builder

A Claude prompt that turns a workout choice into a narrated, 30-second, vertical comic-panel workout video, generated with **Seedance 2.5** through the **Higgsfield MCP**.

It is adapted from an earlier ChatGPT + Artlist MCP version. See [docs/changes-from-artlist.md](docs/changes-from-artlist.md) for what changed.

## What it does

1. Asks which workout routine you want (10 presets, or your own).
2. Asks whether to use your own character image or the default graphite fitness mannequin.
3. Writes three exercises, ~60 words of narration and an eight-panel, timestamped storyboard.
4. Quotes the Higgsfield credit cost and waits for your approval.
5. Generates one 30 s, 9:16, 1080p video with native narration, then shows it with a posting title and caption.

## Requirements

- Claude (claude.ai, desktop, or mobile) with the **Higgsfield** connector enabled (Settings → Connectors).
- Higgsfield credits (or free-trial generations) for Seedance 2.5.

## Setup

Pick one:

**Claude Project (simplest)**
1. Create a Project in Claude.
2. Paste [prompts/comic-workout-video-generator.md](prompts/comic-workout-video-generator.md) into the Project instructions.
3. Optional: add your default character images to Project knowledge as `default-front.png` and `default-rear.png`.
4. Start a chat and say "start".

**Claude Skill**
1. Zip the [skills/ai-gym-builder](skills/ai-gym-builder) folder.
2. Upload it in Claude under Settings → Capabilities → Skills.
3. Ask Claude for a comic workout video.

**One-off chat**
Paste the prompt as your first message and attach the character images.

## Default character images

The prompt expects front and rear views of the same character. Put them in [assets/](assets/) (`default-front.png`, `default-rear.png`) and attach them to your Project or chat. Without them, the prompt falls back to a written description of the mannequin.

## Repository layout

```
prompts/comic-workout-video-generator.md   The prompt (paste into Claude)
skills/ai-gym-builder/SKILL.md             Same prompt packaged as a Claude Skill
docs/changes-from-artlist.md               Differences from the Artlist version
assets/                                    Default character images (add your own)
```

## Notes

- Nothing is generated before you approve the quoted credit cost.
- Claude can't watch the finished video, so it reports what it verified (job metadata) separately from what you should check yourself.
- The video is a routine overview, not a complete workout, and avoids results or medical claims.
