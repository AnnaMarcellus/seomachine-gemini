# SEO Machine - Gemini CLI Edition

A specialized Gemini CLI workspace for creating long-form, SEO-optimized blog content. Converted from the original Claude Code SEO Machine by TheCraigHewitt.

## What This Is

SEO Machine ab Gemini CLI pe bhi chalega. Same powerful Python analysis pipeline, Gemini ke saath.

## Setup

```bash
# 1. Python dependencies install karo
pip install -r data_sources/requirements.txt

# 2. Environment configure karo
cp .env.example .env
# .env file mein apni API keys daalo

# 3. Context files customize karo
# context/ folder mein apni company info fill karo
```

## Gemini CLI Configuration

### Installation
```bash
npm install -g @google/gemini-cli
```

### Project Setup
```bash
gemini config set project.name "seomachine"
gemini config set project.instructions "$(cat .gemini/instructions.md)"
```

## Usage

### Research
```bash
gemini --prompt="research: content marketing strategies for B2B SaaS"
```

### Write Article
```bash
gemini --prompt="write: content marketing strategies for B2B SaaS"
```

### Optimize Existing Content
```bash
gemini --prompt="optimize: drafts/my-article.md"
```

## Directory Structure

```
.
├── .gemini/              # Gemini CLI specific files
│   ├── instructions.md   # Main system instructions
│   ├── prompts/          # Command prompts
│   └── tools/            # Tool definitions
├── data_sources/         # Python analysis modules (unchanged)
│   ├── modules/
│   ├── cache/
│   └── config/
├── context/              # Brand voice, style guide, etc.
└── workspace/            # Content output
    ├── topics/
    ├── research/
    ├── drafts/
    └── published/
```

## Key Differences from Claude Code Version

| Feature | Claude Code | Gemini CLI |
|---------|-------------|------------|
| Commands | `/research topic` | `gemini --prompt="research: topic"` |
| File Context | `@context/brand-voice.md` | Automatic context loading |
| Agents | Agent files | System prompt personas |
| Context Window | 200K tokens | 1M+ tokens |

## Customization

### Brand Voice Setup

`context/brand-voice.md` ko apni company ke according edit karo.

### Adding New Commands

`.gemini/prompts/` mein nayi prompt files add karo:

```bash
# Example: .gemini/prompts/my-command.txt
You are an SEO specialist. Given a topic, analyze...
```

## Python Analysis Modules

Ye modules AI-agnostic hain - Claude ya Gemini dono ke saath kaam karein ge:

- **keyword_analyzer.py** — Keyword density aur distribution analysis
- **seo_quality_rater.py** — 0-100 SEO score calculation
- **content_length_comparator.py** — SERP competitor word count compare
- **readability_scorer.py** — Flesch scores aur grade levels
- **search_intent_analyzer.py** — Query intent classification

## API Integrations

- **Google Analytics 4** — Traffic aur engagement data
- **Google Search Console** — Rankings aur impressions
- **DataForSEO** — SERP positions aur keyword metrics

.env file mein apni API credentials configure karo.

## Workflow

1. **Research** → `gemini --prompt="research: [topic]"`
2. **Write** → `gemini --prompt="write: [topic]"`
3. **Analyze** → Python modules auto-run karte hain
4. **Optimize** → `gemini --prompt="optimize: [file]"`
5. **Publish** → WordPress REST API se publish

## Credits

Original SEO Machine by [TheCraigHewitt](https://github.com/TheCraigHewitt/seomachine)
Gemini CLI conversion by Cody
