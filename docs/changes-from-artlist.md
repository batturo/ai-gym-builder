# Changes from the Artlist version

The creative brief (workout menu, character, locked comic style, eight-panel storyboard, narration rules) is unchanged. The platform and tool steps were rewritten for Claude + Higgsfield.

| Area | Artlist version (ChatGPT) | Higgsfield version (Claude) |
|---|---|---|
| Host | ChatGPT | Claude (Project, Skill, or chat) |
| Provider | Artlist MCP; Higgsfield forbidden | Higgsfield MCP; Artlist and others forbidden |
| Model discovery | `list_models`, `get_model_config` | Higgsfield video model catalog (`models_explore`); read the model's durations, resolutions, aspect ratios, audio and `medias[].roles` |
| Destination | Ask for a project only on `project_required` | `get_preferences`; `create_project` and reuse `default_folder_id` when auto-create is on or requested |
| Uploading references | Artlist upload tools, upload panel fallback | `media_upload` → PUT → `media_confirm`; `media_upload_widget` (alone in its turn) when Claude can't read the file |
| Reference role | Reference array, not first/last frames | `image` role (per catalog), never `start_image` / `end_image` |
| Cost approval | Only if `generate_video` returns `confirmation_required`, then `confirmCost: true` | Always quote with `estimate_video_cost` first and wait for explicit approval in a new message |
| Balance choice | n/a | Leave `use_unlim` unset; if `unlim_choice` comes back, ask which balance to use |
| Following the job | `get_generation_status` | `jobs_wait` (≤ 15 s per call) on the same job ID |
| Delivery | Artlist result and download tool | `show_generation_by_ids` / `job_display`, plus the download link if the job returns one |
| Verification | Inspect the result | Same, plus an explicit note that Claude usually can't watch or hear the video |
| Default images | Attached to the ChatGPT conversation | Attached to the chat or stored in Claude Project knowledge |
