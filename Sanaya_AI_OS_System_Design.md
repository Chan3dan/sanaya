# Sanaya AI OS — Complete System Design
### Designed by: Senior AI Architect, Product Designer & Full-Stack Engineer
### Target Hardware: Intel i5 1.60 GHz · 8 GB RAM · Intel UHD 620 · Windows

---

## Table of Contents

1. [Core Vision](#1-core-vision)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Module Responsibilities](#3-module-responsibilities)
4. [AI Abstraction Layer](#4-ai-abstraction-layer)
5. [Memory System Design](#5-memory-system-design)
6. [Voice System](#6-voice-system)
7. [Automation & Plugin Architecture](#7-automation--plugin-architecture)
8. [Technology Stack](#8-technology-stack)
9. [Scalability Roadmap](#9-scalability-roadmap)
10. [Production Folder Structure](#10-production-folder-structure)
11. [Database Schemas](#11-database-schemas)
12. [API Design](#12-api-design)
13. [Security Architecture](#13-security-architecture)
14. [Future Expansion](#14-future-expansion)
15. [Development Strategy](#15-development-strategy)

---

## 1. Core Vision

Sanaya is not a chatbot. It is a **modular AI Operating System** — a personal intelligence layer that runs on your hardware, understands you over time, automates your computer, and evolves continuously without requiring rewrites.

### Design Philosophy

- **Voice-first**: All interactions begin and end with natural speech
- **Memory-centric**: Sanaya's value compounds over time through accumulated understanding
- **Privacy-by-default**: Sensitive data never leaves your machine
- **Modular**: Every capability is an independent, swappable module
- **Provider-agnostic**: The AI brain can be replaced without touching anything else
- **Plugin-driven**: New skills are added by dropping in a Python class

### Core Capabilities (All Phases)

| Capability | Description |
|---|---|
| Wake word | "Hey Sanaya" — always listening, near-zero CPU |
| Natural conversation | Human-like, context-aware, memory-backed dialogue |
| Personal memory | Remembers facts, preferences, and history across sessions |
| Computer automation | Opens apps, manages files, controls the OS |
| Web automation | Controls the browser, fills forms, scrapes data |
| Learning | Adapts to user preferences and patterns over time |
| Multi-device | Expandable to mobile, smart home, and business tools |

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SANAYA AI OS                                │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  │
│  │ Voice Module│  │  AI Module  │  │Memory Module│  │ Security │  │
│  │STT·TTS·Wake │  │LLM·Agents   │  │STM·LTM·Vec  │  │Auth·Keys │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────┬─────┘  │
│         │                │                │               │        │
│  ┌──────▼──────────────────────────────────────────────────▼─────┐ │
│  │              EVENT BUS  (Redis Pub/Sub + Socket.IO)           │ │
│  │         All modules communicate only through events           │ │
│  └──────┬──────────────────────────────────────────────────┬─────┘ │
│         │                │                │               │        │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐  ┌────▼─────┐  │
│  │  Automation │  │Vision Module│  │  Web Module │  │Dashboard │  │
│  │OS·Browser   │  │Screen·OCR   │  │Search·APIs  │  │UI·Config │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘  │
│                                                                     │
│                   ┌─────────────────────────┐                      │
│                   │   AI ABSTRACTION LAYER   │                      │
│                   │  Provider-agnostic API   │                      │
│                   └──────────────┬──────────┘                      │
│                                  │                                  │
│         ┌──────────┬─────────────┼──────────────┬──────────┐       │
│    ┌────▼───┐ ┌────▼───┐ ┌──────▼──┐ ┌─────────▼┐ ┌──────▼─────┐ │
│    │Ollama  │ │OpenAI  │ │ Gemini  │ │  Claude  │ │  Future+   │ │
│    │Local   │ │GPT-4o  │ │Vision   │ │Anthropic │ │  Plug-in   │ │
│    └────────┘ └────────┘ └─────────┘ └──────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Architectural Principles

1. **Event-driven**: No module calls another module directly. All communication is through the Event Bus.
2. **Single responsibility**: Each module does one thing and does it well.
3. **Interface-first**: Every module exposes a stable contract. Internal implementation can change freely.
4. **Local-first**: Prefer local processing. Use cloud only when necessary or explicitly chosen.
5. **Fail gracefully**: If a module crashes, the rest of the system continues operating.

---

## 3. Module Responsibilities

### 3.1 Voice Module

**Purpose**: The only module that deals with audio. Entry and exit point for all human interaction.

**Responsibilities**:
- Run wake word detection continuously in a background thread (~1% CPU)
- On trigger: activate STT, stream audio until silence detected
- Emit `voice.transcription.ready` event with transcribed text
- Listen for `ai.response.ready` events and convert text to speech
- Manage audio device selection and volume

**Key components**:
- `wake_word.py` — OpenWakeWord listener, custom "hey sanaya" model
- `stt.py` — Whisper (local) or Deepgram (cloud) abstraction
- `tts.py` — Coqui TTS (local) or ElevenLabs (cloud) abstraction

**Events emitted**: `voice.wake_word.detected`, `voice.transcription.ready`, `voice.tts.complete`

**Events consumed**: `ai.response.ready`, `voice.config.update`

---

### 3.2 AI Module

**Purpose**: The reasoning brain. Coordinates intent, context, and response generation.

**Responsibilities**:
- Receive transcribed text from event bus
- Classify intent (conversational / automation / web / compound workflow)
- Fetch relevant memory context from Memory Module
- Select AI provider via the Abstraction Layer
- Stream response tokens back to Voice Module
- Emit automation/web events for downstream modules
- Run multi-step agent workflows

**Key components**:
- `intent_classifier.py` — Routes to correct handler
- `context_builder.py` — Assembles memory + conversation history
- `agent_runner.py` — LangChain/LangGraph agent execution
- `response_streamer.py` — Token streaming to voice

**Events emitted**: `ai.response.ready`, `automation.task.requested`, `web.action.requested`, `memory.store.requested`

**Events consumed**: `voice.transcription.ready`, `memory.context.ready`

---

### 3.3 Memory Module

**Purpose**: Sanaya's persistent identity and knowledge store.

**Responsibilities**:
- Manage three memory tiers (short-term, long-term, semantic)
- Respond to context queries with relevant memories
- Run consolidation pipeline (STM → LTM promotion)
- Handle memory encryption and privacy flags
- Allow memory inspection and deletion via Dashboard

**Key components**:
- `manager.py` — Central MemoryManager interface
- `short_term.py` — Redis TTL-based session context
- `long_term.py` — SQLAlchemy-backed persistent facts
- `semantic.py` — ChromaDB vector similarity search
- `consolidator.py` — Nightly STM → LTM compression job

**Events emitted**: `memory.context.ready`, `memory.stored`, `memory.consolidation.complete`

**Events consumed**: `memory.store.requested`, `memory.query.requested`, `memory.delete.requested`

---

### 3.4 Automation Module

**Purpose**: Sanaya's hands — controls the computer and OS.

**Responsibilities**:
- Auto-discover and load plugins from `/plugins` directory
- Route automation commands to appropriate plugin
- Check permissions before executing any action
- Report task status and results
- Support undo for reversible operations

**Key components**:
- `plugin_registry.py` — Auto-discovery and hot-reload loader
- `permission_engine.py` — Pre-execution permission checks
- `task_runner.py` — Async task execution with status tracking
- `plugins/` — Individual skill implementations

**Events emitted**: `automation.task.started`, `automation.task.complete`, `automation.task.failed`

**Events consumed**: `automation.task.requested`

---

### 3.5 Vision Module

**Purpose**: Sanaya's eyes — understands what's on screen.

**Responsibilities**:
- Capture screenshots on demand or continuously
- Run OCR on screen regions
- Analyze screen content with multimodal LLM
- Optionally interface with camera
- Feed visual context to AI Module

**Key components**:
- `screen_capture.py` — MSS-based screenshot capture
- `ocr.py` — Tesseract / EasyOCR abstraction
- `analyzer.py` — Multimodal LLM visual understanding

**Note**: Stub in Phase 1. Fully active from Phase 4.

---

### 3.6 Web Module

**Purpose**: Internet access and browser automation.

**Responsibilities**:
- Manage a persistent headless Playwright browser instance
- Perform structured web scraping
- Connect to external APIs (weather, news, calendar)
- Cache responses to avoid rate limiting
- Handle authentication flows for web services

**Key components**:
- `browser.py` — Playwright controller with session management
- `scraper.py` — BeautifulSoup / Scrapy structured extraction
- `api_connectors/` — Pre-built connectors for common services
- `cache.py` — Redis-backed request cache

---

### 3.7 Security Module

**Purpose**: The gatekeeper — enforces privacy, permissions, and key management.

**Responsibilities**:
- Encrypt/decrypt API keys using Fernet symmetric encryption
- Store master key in OS keychain (Windows Credential Manager)
- Decide local vs cloud routing for every AI request
- Enforce plugin permission manifests
- Handle user authentication to Dashboard

**Key components**:
- `key_manager.py` — Fernet-based API key vault
- `permission_engine.py` — Runtime permission enforcement
- `privacy_router.py` — Local/cloud routing decisions
- `auth.py` — JWT token management for Dashboard

---

### 3.8 Dashboard Module

**Purpose**: The control panel — visual interface for configuration and monitoring.

**Responsibilities**:
- Display conversation history with search
- Show and edit memory contents
- Manage plugin installation and permissions
- Configure AI provider preferences
- Show real-time system health (CPU, RAM, active modules)
- Provide settings for voice, privacy, and automation

**Stack**: React 19 + Vite + TypeScript + Tailwind CSS + Socket.IO

---

## 4. AI Abstraction Layer

This is the most critical architectural decision in the entire system. The rest of Sanaya never imports any AI SDK directly.

### 4.1 Interface Contract

```python
# core/ai/base_provider.py
from abc import ABC, abstractmethod
from typing import AsyncGenerator
from dataclasses import dataclass

@dataclass
class Message:
    role: str          # 'user' | 'assistant' | 'system'
    content: str

@dataclass
class ProviderCapabilities:
    supports_vision: bool
    supports_streaming: bool
    max_context_tokens: int
    cost_per_1k_tokens: float
    is_local: bool

class AIProvider(ABC):
    
    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        options: dict = {}
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens."""
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate embedding vector for semantic memory."""
        ...

    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Return provider capabilities for routing decisions."""
        ...
```

### 4.2 Provider Implementations

```python
# core/ai/providers/ollama_provider.py
import ollama
from core.ai.base_provider import AIProvider, ProviderCapabilities

class OllamaProvider(AIProvider):
    def __init__(self, model: str = "mistral:7b-q4"):
        self.model = model

    async def chat(self, messages, options={}):
        response = ollama.chat(
            model=self.model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            stream=True
        )
        for chunk in response:
            yield chunk['message']['content']

    async def embed(self, text: str) -> list[float]:
        return ollama.embeddings(model="nomic-embed-text", prompt=text)["embedding"]

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_vision=False,
            supports_streaming=True,
            max_context_tokens=8192,
            cost_per_1k_tokens=0.0,
            is_local=True
        )
```

```python
# core/ai/providers/claude_provider.py
import anthropic
from core.ai.base_provider import AIProvider, ProviderCapabilities

class ClaudeProvider(AIProvider):
    def __init__(self):
        self.client = anthropic.Anthropic()  # key from key_manager

    async def chat(self, messages, options={}):
        with self.client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": m.role, "content": m.content} for m in messages]
        ) as stream:
            for text in stream.text_stream:
                yield text

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError("Use Ollama for embeddings")

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_vision=True,
            supports_streaming=True,
            max_context_tokens=200000,
            cost_per_1k_tokens=0.003,
            is_local=False
        )
```

### 4.3 AI Router

```python
# core/ai/router.py
from core.ai.base_provider import AIProvider
from core.security.privacy_router import PrivacyRouter

class AIRouter:
    def __init__(self):
        self.providers = {
            "ollama":  OllamaProvider(),
            "openai":  OpenAIProvider(),
            "gemini":  GeminiProvider(),
            "claude":  ClaudeProvider(),
        }
        self.privacy_router = PrivacyRouter()

    def select_provider(
        self,
        task_type: str,
        privacy_required: bool = False,
        context: dict = {}
    ) -> AIProvider:
        # Privacy always wins
        if privacy_required or self.privacy_router.requires_local(context):
            return self.providers["ollama"]

        routing_map = {
            "vision":             "gemini",
            "complex_reasoning":  "claude",
            "code":               "claude",
            "search_synthesis":   "openai",
            "conversation":       config.DEFAULT_PROVIDER,
        }
        provider_key = routing_map.get(task_type, config.DEFAULT_PROVIDER)
        return self.providers[provider_key]
```

### 4.4 Adding a New Provider (Future-Proof)

To add a new AI provider at any point in the future:

1. Create `core/ai/providers/new_provider.py`
2. Implement the three abstract methods: `chat()`, `embed()`, `get_capabilities()`
3. Add one line to `AIRouter.__init__`: `"newprovider": NewProvider()`
4. Zero changes required anywhere else in the system

---

## 5. Memory System Design

### 5.1 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Memory Manager                    │
│         Retrieval · Compression · Priority          │
└──────────┬──────────────┬──────────────┬────────────┘
           │              │              │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼────────────┐
    │ Short-Term  │ │ Long-Term  │ │  Semantic Memory │
    │   Memory    │ │   Memory   │ │   (Vector Store) │
    │             │ │            │ │                  │
    │  Redis      │ │  SQLite →  │ │  ChromaDB /      │
    │  In-memory  │ │  PostgreSQL│ │  Qdrant          │
    │  TTL: 2hr   │ │  Encrypted │ │  Local · Fast    │
    └──────┬──────┘ └─────┬──────┘ └────┬─────────────┘
           │              │              │
           └──────────────▼──────────────┘
                 Consolidation Pipeline
           (STM → compressed summaries → LTM)
           (Important facts → embedded → Semantic)
```

### 5.2 Short-Term Memory (Redis)

- **Purpose**: Active conversation context for the current session
- **Storage**: Redis in-memory, TTL of 2 hours
- **Contents**: Last N conversation turns, active task state, session variables
- **Access pattern**: Direct key-value lookup, O(1)

```python
# Example STM structure in Redis
{
  "session:abc123": {
    "messages": [
      {"role": "user", "content": "Open my project folder"},
      {"role": "assistant", "content": "Opening your project folder..."}
    ],
    "active_task": "file_browser",
    "context_vars": {"last_opened_file": "report.docx"}
  }
}
```

### 5.3 Long-Term Memory (SQLite → PostgreSQL)

- **Purpose**: Persistent facts, preferences, and task history across all sessions
- **Storage**: SQLite for Phase 1–3, migrate to PostgreSQL at Phase 4+
- **Contents**: User preferences, named facts, task history, learned patterns
- **All content encrypted at rest** using Fernet

### 5.4 Semantic Memory (ChromaDB)

- **Purpose**: Natural language search over accumulated knowledge
- **Storage**: ChromaDB running locally on disk
- **Contents**: Documents the user has shown Sanaya, notes, knowledge base entries
- **Access pattern**: cosine similarity search using sentence-transformer embeddings

```python
# Semantic search example
results = chroma_collection.query(
    query_texts=["what does the user prefer for reports"],
    n_results=5
)
# Returns most semantically similar stored memories
```

### 5.5 Memory Consolidation

A nightly scheduled job runs the consolidation pipeline:

```
Session ends
    → Compress conversation to 3–5 key facts
    → Score each fact for importance (0.0–1.0)
    → Facts above 0.7 → promote to LTM
    → Facts above 0.5 → embed into Semantic store
    → Facts below 0.3 → discard
```

### 5.6 Memory Privacy Rules

| Memory type | Cloud AI allowed | Encryption |
|---|---|---|
| General preferences | Yes | At rest |
| Private facts (user-marked) | No — local only | At rest + in transit |
| Financial / health data | No — local only | Field-level |
| Task history | User choice | At rest |
| Conversation logs | User choice | At rest |

---

## 6. Voice System

### 6.1 Component Comparison

| Component | Free / Local | Premium / Cloud | Recommendation for Phase 1 |
|---|---|---|---|
| Wake word | OpenWakeWord | Picovoice Porcupine ($) | OpenWakeWord — free, customizable |
| STT | Whisper (OpenAI, local) | Deepgram Nova-2, AssemblyAI | Whisper `base` model locally |
| TTS | Coqui XTTS-v2 | ElevenLabs, Azure Neural | Coqui for privacy; ElevenLabs for quality |

### 6.2 Hardware Constraints

On your i5 / 8GB machine:

- **Whisper `base`** (75MB): ~1–2 second transcription latency — acceptable
- **Whisper `small`** (244MB): ~3–4 seconds — use only if accuracy needed
- **Coqui Tacotron2**: Fast TTS, neutral voice quality
- **Coqui XTTS-v2**: Voice cloning capable, ~2–3 second synthesis — acceptable

Do **not** run Whisper `medium` or `large` on 8GB — will cause memory pressure.

### 6.3 Wake Word Training

```bash
# Fine-tune OpenWakeWord to recognise "Hey Sanaya"
# Record 100–200 samples of your voice saying "Hey Sanaya"

python scripts/train_wake_word.py \
  --positive-samples ./data/wakeword/positive/ \
  --negative-samples ./data/wakeword/negative/ \
  --output-model ./data/models/hey_sanaya.onnx
```

### 6.4 Voice Pipeline

```
Microphone input (continuous)
    │
    ▼
OpenWakeWord listener (~1% CPU, always running)
    │ (trigger detected)
    ▼
Audio buffer starts recording
    │ (silence detected)
    ▼
Whisper STT → transcription text
    │
    ▼
event_bus.emit('voice.transcription.ready', {text, session_id})
    │
    ▼  [AI Module processes...]
    │
event_bus.on('ai.response.ready', {text})
    │
    ▼
Coqui TTS → audio synthesis → speaker output
```

---

## 7. Automation & Plugin Architecture

### 7.1 Plugin Base Class

Every automation skill extends this base class:

```python
# core/automation/plugin_base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class PluginManifest:
    name: str
    description: str
    version: str
    author: str
    triggers: list[str]         # Natural language triggers
    permissions: list[str]      # Required permission keys
    supports_undo: bool = False

class SanayaPlugin(ABC):
    manifest: PluginManifest

    @abstractmethod
    async def execute(
        self,
        command: str,
        params: dict,
        context: dict
    ) -> dict:
        """
        Execute the plugin action.
        Returns: {"success": bool, "result": any, "message": str}
        """
        ...

    async def undo(self, execution_id: str) -> bool:
        """Optional: undo the last action."""
        return False

    async def validate(self, params: dict) -> tuple[bool, str]:
        """Validate params before execution."""
        return True, ""
```

### 7.2 Example Plugin

```python
# core/automation/plugins/browser_plugin.py
from playwright.async_api import async_playwright
from core.automation.plugin_base import SanayaPlugin, PluginManifest

class BrowserPlugin(SanayaPlugin):
    manifest = PluginManifest(
        name="browser",
        description="Controls the web browser",
        version="1.0.0",
        author="sanaya-core",
        triggers=["open", "search", "browse", "go to", "navigate"],
        permissions=["browser.open", "browser.navigate"],
        supports_undo=False
    )

    async def execute(self, command: str, params: dict, context: dict) -> dict:
        action = params.get("action")  # 'open_url' | 'search' | 'click'

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            if action == "search":
                query = params.get("query", "")
                await page.goto(f"https://www.google.com/search?q={query}")

            elif action == "open_url":
                await page.goto(params.get("url"))

        return {"success": True, "message": f"Browser action '{action}' completed"}
```

### 7.3 Plugin Auto-Discovery

```python
# core/automation/plugin_registry.py
import importlib
import inspect
from pathlib import Path

class PluginRegistry:
    def __init__(self):
        self.plugins: dict[str, SanayaPlugin] = {}

    def discover(self, plugin_dirs: list[Path]):
        for directory in plugin_dirs:
            for py_file in directory.glob("**/*_plugin.py"):
                module = importlib.import_module(py_file.stem)
                for name, cls in inspect.getmembers(module, inspect.isclass):
                    if issubclass(cls, SanayaPlugin) and cls is not SanayaPlugin:
                        instance = cls()
                        self.plugins[instance.manifest.name] = instance
                        print(f"[Plugin] Loaded: {instance.manifest.name}")

    def find_plugin(self, command: str) -> SanayaPlugin | None:
        command_lower = command.lower()
        for plugin in self.plugins.values():
            if any(t in command_lower for t in plugin.manifest.triggers):
                return plugin
        return None
```

### 7.4 Built-in Plugins (Phase 1–3)

| Plugin | Triggers | Permissions | Phase |
|---|---|---|---|
| `AppLauncherPlugin` | open, launch, start | `os.launch` | 1 |
| `FileManagerPlugin` | find, move, copy, delete, rename | `files.read`, `files.write` | 1 |
| `DocumentReaderPlugin` | read, summarize, extract | `files.read` | 2 |
| `BrowserPlugin` | open, search, go to, navigate | `browser.open` | 1 |
| `ReportGeneratorPlugin` | create report, generate, write | `files.write` | 2 |
| `CalendarPlugin` | schedule, remind, what's on | `calendar.read`, `calendar.write` | 3 |
| `EmailPlugin` | send email, check inbox | `email.read`, `email.send` | 3 |
| `ClipboardPlugin` | copy, paste | `os.clipboard` | 2 |
| `SystemPlugin` | volume, brightness, shutdown | `os.system` | 2 |

---

## 8. Technology Stack

### 8.1 Frontend — Dashboard

```
React 19 + Vite + TypeScript
├── Tailwind CSS           — Utility-first styling
├── Shadcn/UI              — Accessible component library
├── Zustand                — Lightweight global state
├── Socket.IO client       — Real-time event streaming
├── React Query            — Server state management
├── Recharts               — Charts for system health
└── React Router v7        — Client-side routing
```

### 8.2 API Gateway

```
Node.js + Express.js  (MERN-compatible)
├── Socket.IO              — WebSocket server for real-time events
├── JWT (jsonwebtoken)     — Authentication tokens
├── Helmet.js              — Security headers
├── express-rate-limit     — API rate limiting
├── Morgan                 — HTTP request logging
├── Zod                    — Request validation
└── Winston                — Structured logging
```

### 8.3 Core Backend

```
Python 3.12 + FastAPI + asyncio
├── LangChain              — LLM orchestration and agents
├── LangGraph              — Multi-agent workflows (Phase 5)
├── Pydantic v2            — Data validation and settings
├── SQLAlchemy 2.0         — ORM for database access
├── Alembic                — Database migrations
├── Celery + Redis         — Background task queues
├── APScheduler            — Scheduled jobs (consolidation)
├── python-dotenv          — Environment configuration
└── loguru                 — Structured logging
```

### 8.4 Data Storage

```
Phase 1–3: SQLite
Phase 4+:  PostgreSQL 16

Redis 7                    — Short-term memory + event bus + cache
ChromaDB                   — Vector/semantic memory (local)
Qdrant                     — Alternative vector DB (Phase 5, self-hosted)
```

### 8.5 Voice & Vision

```
Wake word:   OpenWakeWord (custom ONNX model)
STT:         faster-whisper (CTranslate2 optimised Whisper)
TTS:         Coqui TTS (tts_models/en/ljspeech/tacotron2)
Screen:      MSS (fast cross-platform screenshot)
OCR:         Tesseract 5 + EasyOCR
Camera:      OpenCV
Vision AI:   LLaVA (local via Ollama) or Gemini Vision (cloud)
```

### 8.6 Automation

```
OS control:       PyAutoGUI + keyboard + mouse
File system:      watchdog + pathlib + shutil
Browser:          Playwright (async)
Documents:        python-docx + openpyxl + PyMuPDF
Report gen:       Jinja2 templates → docx/pdf
```

### 8.7 AI & ML

```
Local AI:         Ollama (Mistral 7B, LLaMA 3, Gemma 2)
Embeddings:       sentence-transformers (all-MiniLM-L6-v2)
                  nomic-embed-text (via Ollama, recommended)
Cloud AI:         openai, anthropic, google-generativeai SDKs
Inference opt:    ONNX Runtime (for wake word + STT optimisation)
```

### 8.8 Security

```
Encryption:       cryptography (Fernet symmetric)
Key storage:      keyring (Windows Credential Manager)
Auth:             python-jwt + bcrypt
Secrets:          python-dotenv (never committed)
```

### 8.9 DevOps & Deployment

```
Containerisation: Docker + Docker Compose (optional, Phase 4+)
Process mgmt:     PM2 (Node) + supervisor (Python)
Environment:      venv (Python) + nvm (Node)
Testing:          pytest + pytest-asyncio (Python) + Vitest (React)
Linting:          ruff (Python) + ESLint + Prettier (JS/TS)
CI/CD:            GitHub Actions (Phase 3+)
```

---

## 9. Scalability Roadmap

### Phase 1 — MVP (6–8 Weeks) ★★☆☆☆

**Goal**: Get Sanaya talking to you. Prove the architecture.

**Features**:
- Wake word detection ("Hey Sanaya")
- Speech-to-text via Whisper base
- Basic conversational AI via Ollama (Mistral 7B)
- Simple automation: open apps, basic file commands
- Text-to-speech via Coqui TTS
- SQLite for conversation history
- Minimal terminal dashboard

**Technologies introduced**:
- Python + FastAPI
- Ollama + Whisper + Coqui
- OpenWakeWord
- SQLite
- PyAutoGUI

**Success criteria**: You can say "Hey Sanaya, open Chrome" and it works.

---

### Phase 2 — Local AI Assistant (2–3 Months) ★★★☆☆

**Goal**: Sanaya remembers you and becomes genuinely useful daily.

**Features**:
- Full memory system (STM + LTM + Semantic)
- User preference learning
- Plugin system with auto-discovery
- File management automation
- Document reading and summarisation
- React dashboard (basic)
- Security module and API key vault

**Technologies introduced**:
- Redis
- ChromaDB
- LangChain
- React + Vite dashboard
- Node.js API gateway
- cryptography (Fernet)

**Success criteria**: Sanaya remembers your preferences from last week and uses them today.

---

### Phase 3 — Advanced Automation (2–3 Months) ★★★☆☆

**Goal**: Sanaya handles multi-step real-world tasks autonomously.

**Features**:
- Full browser automation (Playwright)
- Email reading and composing
- Calendar integration
- Cloud AI providers (OpenAI, Claude, Gemini)
- Multi-step workflow execution
- Report generation (docx, pdf)
- Improved dashboard with memory browser

**Technologies introduced**:
- Playwright
- PostgreSQL (optional upgrade)
- Celery task queue
- LangChain agents
- OAuth integrations

**Success criteria**: "Hey Sanaya, find the emails about the Q3 project, summarise them, and create a report."

---

### Phase 4 — Vision and Screen Understanding (3–4 Months) ★★★★☆

**Goal**: Sanaya can see your screen and reason about it.

**Features**:
- Screen capture and OCR
- Multimodal LLM integration (LLaVA / Gemini Vision)
- UI element detection and interaction
- "What's on my screen?" queries
- Camera input support
- Screen-aware automation

**Technologies introduced**:
- MSS + OpenCV
- EasyOCR
- LLaVA (local) / Gemini Vision (cloud)
- Image processing pipeline

**Success criteria**: "Hey Sanaya, what error is shown on my screen?" — Sanaya reads it and explains.

---

### Phase 5 — Multi-Agent System (4–5 Months) ★★★★☆

**Goal**: Sanaya spawns specialised sub-agents for complex tasks.

**Features**:
- Parallel agent execution
- Specialised agents: Researcher, Planner, Executor, Critic
- React Native mobile companion app
- Agent-to-agent communication
- Long-running background tasks
- Mobile voice interface

**Technologies introduced**:
- LangGraph
- CrewAI
- React Native
- Mobile push notifications
- WebRTC (mobile audio)

**Success criteria**: "Hey Sanaya, research the top 5 competitors in my market and prepare a comparison report" — executes autonomously in 5 minutes.

---

### Phase 6 — Personal AI OS (6–12 Months) ★★★★★

**Goal**: Sanaya is the operating system layer for your entire life.

**Features**:
- Smart home integration (Home Assistant + MQTT)
- IoT device control
- Business assistant mode (CRM, Slack, Notion)
- Cross-device synchronisation
- Self-improvement from feedback
- Kubernetes deployment for team use
- Sanaya as a platform (third-party plugins marketplace)

**Technologies introduced**:
- MQTT broker (Mosquitto)
- Home Assistant API
- Kubernetes (if team deployment)
- Plugin marketplace API
- Advanced ML: RLHF-style preference learning

**Success criteria**: Sanaya coordinates your morning routine across phone, laptop, and home devices without being asked.

---

## 10. Production Folder Structure

```
sanaya/
├── README.md
├── docker-compose.yml              # Full stack local deployment
├── .env.example                    # Template for all env variables
├── .gitignore
│
├── core/                           # Python — the intelligence layer
│   ├── main.py                     # Entry point, starts all modules
│   ├── config.py                   # Pydantic settings (env-backed)
│   ├── event_bus.py                # Redis Pub/Sub wrapper
│   ├── requirements.txt
│   │
│   ├── ai/                         # AI Abstraction Layer
│   │   ├── __init__.py
│   │   ├── base_provider.py        # Abstract AIProvider interface
│   │   ├── router.py               # AIRouter — selects provider
│   │   └── providers/
│   │       ├── ollama_provider.py
│   │       ├── openai_provider.py
│   │       ├── gemini_provider.py
│   │       └── claude_provider.py
│   │
│   ├── voice/                      # Voice Module
│   │   ├── __init__.py
│   │   ├── module.py               # VoiceModule orchestrator
│   │   ├── wake_word.py            # OpenWakeWord listener
│   │   ├── stt.py                  # STT abstraction (Whisper/Deepgram)
│   │   └── tts.py                  # TTS abstraction (Coqui/ElevenLabs)
│   │
│   ├── memory/                     # Memory Module
│   │   ├── __init__.py
│   │   ├── manager.py              # MemoryManager — main interface
│   │   ├── short_term.py           # Redis STM
│   │   ├── long_term.py            # SQLAlchemy ORM-backed LTM
│   │   ├── semantic.py             # ChromaDB vector store
│   │   └── consolidator.py         # STM → LTM nightly pipeline
│   │
│   ├── automation/                 # Automation Module
│   │   ├── __init__.py
│   │   ├── module.py               # AutomationModule orchestrator
│   │   ├── plugin_base.py          # SanayaPlugin abstract class
│   │   ├── plugin_registry.py      # Auto-discovery loader
│   │   ├── task_runner.py          # Async task execution
│   │   └── plugins/
│   │       ├── app_launcher.py
│   │       ├── file_manager.py
│   │       ├── browser_plugin.py
│   │       ├── document_reader.py
│   │       ├── report_generator.py
│   │       ├── calendar_plugin.py
│   │       ├── email_plugin.py
│   │       ├── clipboard_plugin.py
│   │       └── system_plugin.py
│   │
│   ├── vision/                     # Vision Module
│   │   ├── __init__.py
│   │   ├── screen_capture.py       # MSS screenshot capture
│   │   ├── ocr.py                  # Tesseract / EasyOCR abstraction
│   │   └── analyzer.py             # Multimodal LLM integration
│   │
│   ├── web/                        # Web Module
│   │   ├── __init__.py
│   │   ├── browser.py              # Playwright controller
│   │   ├── scraper.py              # BeautifulSoup / Scrapy
│   │   ├── cache.py                # Redis-backed request cache
│   │   └── api_connectors/
│   │       ├── weather.py
│   │       ├── news.py
│   │       ├── calendar_api.py
│   │       └── email_api.py
│   │
│   ├── security/                   # Security Module
│   │   ├── __init__.py
│   │   ├── key_manager.py          # Fernet key vault
│   │   ├── permission_engine.py    # Plugin permission enforcement
│   │   ├── privacy_router.py       # Local vs cloud routing
│   │   └── auth.py                 # JWT management
│   │
│   └── db/                         # Database layer
│       ├── models.py               # SQLAlchemy models
│       ├── session.py              # DB connection management
│       └── migrations/             # Alembic migration files
│
├── api/                            # Node.js API Gateway (Express)
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts                # Express + Socket.IO server
│       ├── routes/
│       │   ├── chat.ts
│       │   ├── memory.ts
│       │   ├── plugins.ts
│       │   └── settings.ts
│       ├── middleware/
│       │   ├── auth.ts             # JWT validation middleware
│       │   ├── rate_limit.ts
│       │   └── error_handler.ts
│       └── socket/
│           └── events.ts           # Real-time event handling
│
├── dashboard/                      # React Frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── store/
│       │   ├── useAppStore.ts      # Zustand global state
│       │   └── useMemoryStore.ts
│       ├── components/
│       │   ├── Chat/
│       │   │   ├── ChatWindow.tsx
│       │   │   ├── MessageBubble.tsx
│       │   │   └── VoiceIndicator.tsx
│       │   ├── Memory/
│       │   │   ├── MemoryBrowser.tsx
│       │   │   └── MemoryCard.tsx
│       │   ├── Plugins/
│       │   │   ├── PluginList.tsx
│       │   │   └── PluginPermissions.tsx
│       │   ├── Settings/
│       │   │   ├── AISettings.tsx
│       │   │   ├── VoiceSettings.tsx
│       │   │   └── PrivacySettings.tsx
│       │   └── SystemHealth/
│       │       ├── StatusBar.tsx
│       │       └── ModuleHealth.tsx
│       └── hooks/
│           ├── useSocket.ts
│           └── useVoiceStatus.ts
│
├── plugins/                        # User-installed custom plugins
│   └── example_custom_plugin.py   # Template for custom skills
│
├── data/                           # Local data (gitignored)
│   ├── chroma/                     # ChromaDB vector database files
│   ├── sqlite/                     # SQLite database file
│   └── models/                     # Downloaded AI models
│       ├── whisper/
│       ├── coqui/
│       └── wake_word/
│
├── scripts/
│   ├── setup.sh                    # One-command bootstrap script
│   ├── setup.bat                   # Windows bootstrap
│   ├── train_wake_word.py          # Fine-tune wake word model
│   ├── download_models.py          # Download required AI models
│   └── migrate.py                  # Database migration runner
│
└── tests/
    ├── unit/
    │   ├── test_ai_router.py
    │   ├── test_memory_manager.py
    │   └── test_plugin_registry.py
    ├── integration/
    │   ├── test_voice_pipeline.py
    │   └── test_automation_flow.py
    └── e2e/
        └── test_full_conversation.py
```

---

## 11. Database Schemas

### 11.1 Memories Table

```sql
CREATE TABLE memories (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    type         TEXT        NOT NULL CHECK (type IN ('fact', 'preference', 'event', 'skill', 'document')),
    content      TEXT        NOT NULL,  -- Fernet encrypted
    summary      TEXT,                  -- Short plain-text description (for indexing only)
    importance   FLOAT       DEFAULT 0.5 CHECK (importance BETWEEN 0.0 AND 1.0),
    is_private   BOOLEAN     DEFAULT FALSE,
    source       TEXT,                  -- 'conversation' | 'document' | 'user_direct'
    last_access  TIMESTAMP,
    access_count INT         DEFAULT 0,
    created_at   TIMESTAMP   DEFAULT NOW(),
    updated_at   TIMESTAMP   DEFAULT NOW(),
    tags         TEXT[]      DEFAULT '{}'
);

CREATE INDEX idx_memories_type     ON memories(type);
CREATE INDEX idx_memories_tags     ON memories USING GIN(tags);
CREATE INDEX idx_memories_private  ON memories(is_private);
```

### 11.2 Conversations Table

```sql
CREATE TABLE conversations (
    id               UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID      NOT NULL,
    role             TEXT      NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content          TEXT      NOT NULL,
    module_triggered TEXT,               -- Which module handled this turn
    provider_used    TEXT,               -- Which AI provider was used
    latency_ms       INT,                -- Response time in milliseconds
    timestamp        TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conv_session ON conversations(session_id);
CREATE INDEX idx_conv_time    ON conversations(timestamp DESC);
```

### 11.3 Preferences Table

```sql
CREATE TABLE preferences (
    key        TEXT      PRIMARY KEY,
    value      JSONB     NOT NULL,
    category   TEXT      NOT NULL CHECK (category IN ('voice', 'privacy', 'automation', 'ai', 'ui')),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Default preferences
INSERT INTO preferences VALUES
  ('ai.default_provider',       '"ollama"',          'ai',       NOW()),
  ('ai.privacy_mode',           'false',             'privacy',  NOW()),
  ('voice.wake_word_sensitivity','0.5',              'voice',    NOW()),
  ('voice.tts_provider',        '"coqui"',           'voice',    NOW()),
  ('automation.require_confirm', 'true',             'automation',NOW());
```

### 11.4 Tasks Table

```sql
CREATE TABLE tasks (
    id          UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT      NOT NULL,
    plugin      TEXT      NOT NULL,
    status      TEXT      DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'done', 'failed', 'cancelled')),
    params      JSONB     DEFAULT '{}',
    result      JSONB,
    error       TEXT,
    session_id  UUID,
    created_at  TIMESTAMP DEFAULT NOW(),
    started_at  TIMESTAMP,
    finished_at TIMESTAMP
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_plugin ON tasks(plugin);
```

### 11.5 Plugin Permissions Table

```sql
CREATE TABLE plugin_permissions (
    plugin_name  TEXT    NOT NULL,
    permission   TEXT    NOT NULL,
    granted      BOOLEAN DEFAULT FALSE,
    granted_at   TIMESTAMP,
    PRIMARY KEY (plugin_name, permission)
);
```

---

## 12. API Design

### 12.1 REST API Endpoints

```
Base URL: http://localhost:3001/api/v1

Authentication: Bearer JWT token in Authorization header

POST   /auth/login               → {token, expires_at}
POST   /auth/refresh             → {token}

GET    /chat/history             → ConversationTurn[]
POST   /chat/message             → {message_id, queued: true}
DELETE /chat/history             → {deleted: true}

GET    /memory                   → Memory[]  (paginated)
POST   /memory                   → Memory    (create manual memory)
PATCH  /memory/:id               → Memory    (update importance/tags)
DELETE /memory/:id               → {deleted: true}
GET    /memory/search?q=         → Memory[]  (semantic search)

GET    /plugins                  → Plugin[]
POST   /plugins/:name/enable     → {enabled: true}
POST   /plugins/:name/disable    → {enabled: false}
GET    /plugins/:name/permissions→ Permission[]
PATCH  /plugins/:name/permissions→ Permission[]

GET    /settings                 → Settings
PATCH  /settings                 → Settings

GET    /providers                → AIProvider[]  (available)
PATCH  /providers/default        → {provider: string}

GET    /tasks                    → Task[]  (recent)
GET    /tasks/:id                → Task
DELETE /tasks/:id                → {cancelled: true}

GET    /health                   → SystemHealth
```

### 12.2 WebSocket Events (Socket.IO)

```javascript
// Client → Server
socket.emit('voice.manual_input', { text: 'open my browser' })
socket.emit('conversation.clear', {})
socket.emit('module.restart', { module: 'voice' })

// Server → Client  (real-time streaming)
socket.on('ai.token',           (data) => { /* {token: string} */ })
socket.on('ai.response.done',   (data) => { /* {full_text, latency_ms} */ })
socket.on('voice.status',       (data) => { /* {listening: bool, transcribing: bool} */ })
socket.on('task.update',        (data) => { /* {task_id, status, result} */ })
socket.on('memory.stored',      (data) => { /* {memory_id, summary} */ })
socket.on('module.health',      (data) => { /* {module, status, cpu, mem} */ })
socket.on('wake_word.detected', (data) => { /* {timestamp} */ })
```

### 12.3 Python Internal Event Bus Events

```python
# Event naming convention: module.noun.verb

# Voice events
'voice.wake_word.detected'    # payload: {timestamp, confidence}
'voice.transcription.ready'   # payload: {text, session_id, language}
'voice.tts.requested'         # payload: {text, priority}
'voice.tts.complete'          # payload: {duration_ms}

# AI events
'ai.response.token'           # payload: {token, session_id}
'ai.response.ready'           # payload: {text, session_id, provider}
'ai.intent.classified'        # payload: {intent, confidence, entities}

# Memory events
'memory.store.requested'      # payload: {content, type, importance}
'memory.query.requested'      # payload: {query, limit, session_id}
'memory.context.ready'        # payload: {memories[], session_id}

# Automation events
'automation.task.requested'   # payload: {plugin, command, params}
'automation.task.started'     # payload: {task_id, plugin}
'automation.task.complete'    # payload: {task_id, result}
'automation.task.failed'      # payload: {task_id, error}

# System events
'system.module.ready'         # payload: {module_name}
'system.module.error'         # payload: {module_name, error}
'system.shutdown.requested'   # payload: {reason}
```

---

## 13. Security Architecture

### 13.1 API Key Management

```python
# core/security/key_manager.py
import keyring
from cryptography.fernet import Fernet

class KeyManager:
    SERVICE_NAME = "sanaya_ai_os"

    def __init__(self):
        master_key = keyring.get_password(self.SERVICE_NAME, "master_key")
        if not master_key:
            master_key = Fernet.generate_key().decode()
            keyring.set_password(self.SERVICE_NAME, "master_key", master_key)
        self.fernet = Fernet(master_key.encode())

    def store_api_key(self, provider: str, key: str):
        encrypted = self.fernet.encrypt(key.encode())
        # Store encrypted key in database, never in env files
        db.execute("INSERT INTO api_keys VALUES (?, ?)", [provider, encrypted])

    def get_api_key(self, provider: str) -> str:
        row = db.execute("SELECT key FROM api_keys WHERE provider = ?", [provider])
        return self.fernet.decrypt(row.key).decode()
```

### 13.2 Privacy Routing Rules

```
Request arrives with context
        │
        ▼
Does context contain private-flagged memories?
        │ YES → Route to Ollama (local)
        │ NO  ↓
Does user preference = "always local"?
        │ YES → Route to Ollama
        │ NO  ↓
Does content match sensitive patterns?
  (SSN, password, health, financial)
        │ YES → Route to Ollama
        │ NO  ↓
Task-based routing:
  vision    → Gemini Vision (or local LLaVA)
  complex   → Claude / GPT-4o
  simple    → User default provider
  embedding → nomic-embed-text (always local)
```

### 13.3 Permission Control System

Every plugin declares required permissions. User grants permissions once, stored in database.

```python
# Permission hierarchy
permissions = {
    "files": {
        "files.read":          "Read files and folders",
        "files.write":         "Create and modify files",
        "files.write.delete":  "Permanently delete files",  # Requires explicit grant
    },
    "browser": {
        "browser.open":        "Open the browser",
        "browser.navigate":    "Navigate to URLs",
        "browser.form":        "Fill and submit forms",     # Elevated permission
    },
    "os": {
        "os.launch":           "Launch applications",
        "os.clipboard":        "Read/write clipboard",
        "os.system":           "System settings (volume, brightness)",
        "os.execute":          "Run system commands",        # Requires explicit grant
    },
    "network": {
        "network.read":        "Make read-only API requests",
        "network.write":       "Make write API requests (send email, post)",
    }
}
```

### 13.4 Memory Encryption

```python
# Field-level encryption for sensitive memory
class EncryptedMemory:
    def store(self, content: str, is_private: bool = False) -> str:
        encrypted = self.fernet.encrypt(content.encode()).decode()
        return encrypted  # Stored in DB — plaintext never persists

    def retrieve(self, encrypted: str) -> str:
        return self.fernet.decrypt(encrypted.encode()).decode()
        # Decrypted in memory for the duration of the request only
```

### 13.5 Local vs Cloud Decision Matrix

| Content | Cloud AI | Encryption | Rationale |
|---|---|---|---|
| Private-flagged memory | Never | At rest + in transit | User decision |
| Health/medical data | Never | Field-level | Sensitive by nature |
| Financial data | Never | Field-level | Sensitive by nature |
| Passwords/credentials | Never | Field-level | Never stored |
| General conversation | User preference | At rest | Default: local |
| Complex reasoning tasks | Allowed (if user permits) | At rest | Quality tradeoff |
| Vision/screen content | Allowed (if user permits) | At rest | Capability tradeoff |
| Embeddings | Never (always local) | At rest | Privacy + cost |

---

## 14. Future Expansion

### 14.1 Desktop Assistant (Phase 1–2)

Wrap the existing system in an Electron shell for:
- System tray icon with status indicator
- Hotkey activation (in addition to wake word)
- Native Windows notifications
- Auto-start on login
- No browser required for the dashboard

```bash
# Electron wraps the existing React dashboard
electron-builder --win --x64
```

### 14.2 Mobile Assistant (Phase 5)

React Native app connecting to the same API gateway:
- Voice interface using device microphone
- Push notifications for task completion
- Offline mode with local Whisper (on-device)
- Sync preferences and memory with desktop Sanaya
- Lock screen widget for quick commands

### 14.3 Smart Home Assistant (Phase 6)

Integration via Home Assistant and MQTT:

```python
# plugins/smart_home_plugin.py
class SmartHomePlugin(SanayaPlugin):
    manifest = PluginManifest(
        name="smart_home",
        triggers=["turn on", "turn off", "set temperature", "lock", "unlock"],
        permissions=["network.write"]
    )

    async def execute(self, command, params, context):
        # Publish to Home Assistant via MQTT or REST API
        await self.ha_client.set_state(
            entity_id=params["device"],
            state=params["state"]
        )
```

### 14.4 Business Assistant (Phase 6)

Plugin pack for professional use:
- Slack: read messages, draft replies, post updates
- Notion: create pages, update databases
- CRM (HubSpot, Salesforce): log calls, update contacts
- Jira/Linear: create tickets, update status
- Google Workspace: Docs, Sheets, Calendar
- Microsoft 365: Word, Excel, Outlook, Teams

All implemented as plugins — same architecture, no core changes.

### 14.5 AI Agent Platform (Phase 5–6)

Transform Sanaya into a platform where agents collaborate:

```
User: "Research competitors and prepare a strategy deck"
        │
        ▼
Orchestrator Agent
    ├── Research Agent (web search + summarisation)
    ├── Analysis Agent (competitive analysis)
    ├── Writer Agent (PowerPoint generation)
    └── Critic Agent (review and feedback)
        │
        ▼
Completed strategy deck delivered in ~10 minutes
```

Built with LangGraph for state machine-based agent coordination and CrewAI for role-based agent teams.

---

## 15. Development Strategy

### 15.1 Start Today — Literal Next Steps

```bash
# Day 1: Bootstrap the project
mkdir sanaya && cd sanaya
python -m venv venv && venv\Scripts\activate   # Windows
pip install fastapi uvicorn ollama openai-whisper pyaudio sqlalchemy redis chromadb cryptography

# Pull your first local model
ollama pull mistral:7b-q4

# Download Whisper base model
python -c "import whisper; whisper.load_model('base')"
```

### 15.2 Week-by-Week Plan for Phase 1

| Week | Goal |
|---|---|
| 1 | Project structure, config system, event bus working |
| 2 | Voice module: Whisper STT + Coqui TTS working end-to-end |
| 3 | Wake word detection: OpenWakeWord trained on your voice |
| 4 | AI module: Ollama connected, basic conversation working |
| 5 | Basic automation: app launcher + file commands |
| 6 | SQLite memory, polish, and first real daily use |

### 15.3 The Golden Rules

1. **Protect the abstraction layer.** No module may import any AI SDK except its assigned provider class. Enforce this with code review and linting rules.

2. **Ship every phase.** Each phase must be usable before starting the next. No "I'll clean it up in Phase 3."

3. **Memory is the product.** Every design decision should ask: "does this make Sanaya understand the user better?"

4. **Privacy by default.** When in doubt, process locally. Ask before sending to cloud. Let the user see and delete everything.

5. **Plugins, not core changes.** If a new capability can be a plugin, it must be a plugin. Core changes should be rare and deliberate.

6. **Test the voice pipeline.** Every code change that touches the voice stack should be tested with your actual voice, not just unit tests.

### 15.4 Hardware Upgrade Path

| Phase | Recommended RAM | GPU |
|---|---|---|
| 1–2 | 8 GB (current) ✓ | Not needed |
| 3 | 8 GB (current) ✓ | Not needed |
| 4 | 16 GB recommended | Integrated OK |
| 5–6 | 16–32 GB | Dedicated GPU for local LLaVA |

The architecture scales with your hardware automatically. As you add RAM, point Ollama to a larger model. As you add GPU, switch to accelerated inference. No architectural changes needed.

---

## Appendix A — Environment Variables

```bash
# .env.example — copy to .env and fill in values
# Never commit .env to version control

# Application
SANAYA_ENV=development            # development | production
SANAYA_LOG_LEVEL=INFO
SANAYA_DASHBOARD_PORT=3000
SANAYA_API_PORT=3001
SANAYA_CORE_PORT=8000

# Database
DATABASE_URL=sqlite:///./data/sqlite/sanaya.db
REDIS_URL=redis://localhost:6379
CHROMA_PATH=./data/chroma

# AI Providers (stored encrypted — these are only used for initial setup)
# After first run, keys are moved to the OS keychain
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
OLLAMA_BASE_URL=http://localhost:11434

# Default AI configuration
DEFAULT_AI_PROVIDER=ollama        # ollama | openai | gemini | claude
PRIVACY_MODE=false                # true = always use local AI
EMBEDDING_MODEL=nomic-embed-text  # Always local

# Voice configuration
WHISPER_MODEL=base                # tiny | base | small
TTS_PROVIDER=coqui                # coqui | elevenlabs
WAKE_WORD_MODEL=./data/models/wake_word/hey_sanaya.onnx
WAKE_WORD_SENSITIVITY=0.5

# Security
JWT_SECRET=change-this-in-production
JWT_EXPIRY=24h
MEMORY_ENCRYPTION=true
```

---

## Appendix B — Quick Reference Commands

```bash
# Start full system
python core/main.py                    # Start all Python modules
cd api && npm run dev                  # Start API gateway
cd dashboard && npm run dev            # Start React dashboard

# Download models
python scripts/download_models.py

# Train wake word
python scripts/train_wake_word.py

# Database migrations
python scripts/migrate.py upgrade head

# Run tests
pytest tests/ -v
cd dashboard && npm test

# Add a new plugin
# 1. Copy core/automation/plugins/app_launcher.py as template
# 2. Implement SanayaPlugin interface
# 3. Drop file into core/automation/plugins/ or /plugins/
# 4. Restart Sanaya — plugin auto-discovered

# Check system health
curl http://localhost:3001/api/v1/health
```

---

*Sanaya is designed to grow with you. Start small, ship early, and trust the architecture.*
*The modular event-driven design means nothing you build today will need to be thrown away tomorrow.*

---
**Document version**: 1.0  
**Architecture target**: Phase 1–6 (2025–2028)  
**Primary language**: Python 3.12 + TypeScript 5  
**Designed for**: Intel i5 / 8GB RAM / Windows — scales up without rewrites
