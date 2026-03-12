# SEO Machine - Gemini CLI Edition

**Version:** 1.0.0-gemini  
**Based on:** SEO Machine Original (Claude Code Edition)  
**Optimized for:** Google Gemini CLI

## What's Different

This version is specifically adapted for use with **Google Gemini CLI** (`@google/gemini-cli`).

### Changes from Original
- `.claude/` → `.gemini/` folder structure
- `CLAUDE.md` → `.gemini/instructions.md` (Gemini system prompt)
- Updated README for Gemini CLI workflow
- Same powerful Python modules (AI-agnostic)

### Requirements
```bash
npm install -g @google/gemini-cli
pip install -r data_sources/requirements.txt
```

### Quick Start
```bash
# Setup
cp .env.example .env
# Edit .env with your API keys

# Use with Gemini CLI
gemini --prompt="research: your topic here"
```

---

**Full documentation:** See README.md

**Source:** Converted from [TheCraigHewitt/seomachine](https://github.com/TheCraigHewitt/seomachine)
