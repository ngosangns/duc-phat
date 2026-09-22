# Integration Pattern — How Other Skills Use vietnamese-writer

`vietnamese-writer` is a **foundational language layer** (Layer 0 in the 7-layer Vietnamese writing architecture). It does not produce content — it enables other skills to produce native-quality Vietnamese content by switching the model's reasoning language.

## When to Reference This Skill

Any Hermes skill that produces Vietnamese content should reference `vietnamese-writer`:

| If your skill... | Then... |
|---|---|
| Writes Vietnamese content of any kind | Add `vietnamese-writer` to `related_skills`, recommend preloading it |
| Has its own Vietnamese writing quality rules | Consider removing them and pointing to `vietnamese-writer` instead |
| Is about brand voice in Vietnamese (e.g., `le-j-write`) | Preload `vietnamese-writer` first, then apply brand voice on top |
| Is about a Vietnamese content pipeline (e.g., `hermes-fb-content-pipeline`) | Load `vietnamese-writer` for the generation phase of the pipeline |

## Loading Order

```
1. vietnamese-writer        ← language activation (thinking switch + self-review)
2. [domain skill]           ← topic structure, fact-checking, audience
3. [brand voice skill]      ← tone, vocabulary, narrative patterns (if applicable)
```

Example:

```bash
hermes --skills vietnamese-writer,le-j-write
```

Or in a pipeline: load `vietnamese-writer` before the generation step, so the model's reasoning is in Vietnamese before it receives domain instructions.

## What vietnamese-writer Provides

| Feature | What it does |
|---------|-------------|
| **Activation gate** | Self-detects Vietnamese tasks; inert for non-Vietnamese work |
| **Thinking-language switch** | Forces internal reasoning into Vietnamese |
| **5-phase protocol** | Detect → Activate → Structure → Generate → Self-Review |
| **Self-review checklist** | 5 questions checked in Vietnamese — catches English-reasoning drift |
| **Context efficiency** | ~600 words. Other loaded skills don't need to carry their own language rules |

## What vietnamese-writer Does NOT Provide

- **Topic structure** — use domain skills
- **Brand voice** — use brand skills (e.g., `le-j-write-social`)
- **Post-generation polish** — use `humanizer`

## Verification That It's Working

Run this test to confirm the model is thinking in Vietnamese:

```bash
hermes chat -q "viết 2 câu về cà phê. Trước khi viết, hãy cho biết bạn đang dùng ngôn ngữ gì để suy nghĩ." --skills vietnamese-writer
```

Expected response: the model will explain it's thinking **in Vietnamese** (confirmed empirically — see session from Dec 2026).

To see raw thinking tokens (if the provider exposes them):

```bash
hermes chat -q "viết 3 câu quảng bá cho quán cà phê" --skills vietnamese-writer --verbose 2>&1 | grep "\[thinking\]"
```

Expected: initial English detection (1-3 tokens), then ALL subsequent thinking in Vietnamese.

## Case Study

For the full story of how and why `vietnamese-writer` was built — the first-principles analysis, the build-test-iterate cycle, and the empirical results — see:

- EN: `src/content/cases/vietnamese-writer-agent.md` (thanhan.dev)
- VI: `src/content/cases/vietnamese-writer-agent-vi.md` (thanhan.dev)

## Session History

Created: June 2026
Tested: DeepSeek v4 Flash via OpenCode Go
Evidence: `[thinking]` logs confirm Vietnamese reasoning after detection phase
