# Vietnamese Writer — Hermes Skill

A Hermes Agent skill that forces LLMs to think in Vietnamese before generating Vietnamese content. Solves "dịch thô" — Vietnamese words arranged in English syntax — by switching the model's internal reasoning language from English to Vietnamese.

## The Problem

LLMs are trained on ~90%+ English data. When asked to generate Vietnamese, they default to English reasoning and "translate" at the output layer. The result: Vietnamese glyphs with English bones. Correct words, wrong rhythm. This is called *dịch thô* — raw translation.

No amount of prompt engineering fixes this because the structural decisions are already made before the first Vietnamese token is generated.

## The Fix

A 5-phase protocol (~600 words) that:
1. Detects the task as Vietnamese — self-gating, inert for non-Vietnamese work
2. Switches the model's thinking language to Vietnamese — before any planning starts
3. Structures the outline using Vietnamese discourse patterns (topic-comment flow)
4. Generates with quality signals — 5-dimension reference table + 8 banned AI patterns
5. Self-reviews in Vietnamese — 5 questions, zero output-level English contamination

## Installation

```bash
# Install via hermes skills hub (if published):
hermes skills install vietnamese-writer

# Or manually:
curl -fsSL https://raw.githubusercontent.com/thanhan-a17/vietnamese-writer-skill/main/install.sh | bash
```

## Usage

```bash
# Preload the skill and write in Vietnamese
hermes --skills vietnamese-writer

# Or load mid-session
/skill vietnamese-writer
```

The skill self-activates when it detects a Vietnamese writing task. For English tasks, it stays inert.

## Verification

```bash
hermes chat -q "viết 2 câu về cà phê. Trước khi viết, hãy cho biết bạn đang dùng ngôn ngữ gì để suy nghĩ." --skills vietnamese-writer
```

Expected: the model will confirm it's thinking in Vietnamese.

See the full case study at [thanhan.dev](https://thanhan.dev).

## Repository Structure

```
SKILL.md              # The Hermes skill (source of truth)
README.md             # This file
install.sh            # Install script
references/
  integration-pattern.md  # How other skills use vietnamese-writer
```

## Case Study

For the full story — first-principles analysis, build-test-iterate cycle, and empirical results:
- [English case study](https://thanhan.dev/en/cases/vietnamese-writer-agent)
- [Vietnamese case study](https://thanhan.dev/vi/cases/vietnamese-writer-agent-vi)

## License

MIT
