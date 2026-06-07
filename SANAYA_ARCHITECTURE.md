# Sanaya AI Assistant Architecture

## Vision

Sanaya is a voice-first personal AI operating system inspired by JARVIS, designed to evolve for 5-10 years without requiring major rewrites.

The goal is not to build a simple chatbot. The goal is to build a modular, secure, extensible AI assistant platform that can support:

- Voice-first interaction
- Wake word: "Hey Sanaya"
- Human-like conversations
- Personal memory
- Computer automation
- Web automation
- User preference learning
- Local and cloud AI models
- Desktop, mobile, smart home, and business expansion

Core architectural rule:

> No module should directly depend on OpenAI, Gemini, Claude, Ollama, or any single AI provider.

All AI providers must be accessed through Sanaya's own AI abstraction layer.

---

## High-Level Architecture

```text
User
  |
  v
Voice UI / Desktop UI / Web Dashboard / Mobile App
  |
  v
Sanaya Core Orchestrator
  |
  +--> Intent Router
  +--> Context Manager
  +--> Permission Engine
  +--> Workflow Engine
  +--> Event Bus
  |
  v
Modules
  |
  +--> Voice Module
  +--> AI Module
  +--> Memory Module
  +--> Automation Module
  +--> Vision Module
  +--> Web Module
  +--> Security Module
  +--> Dashboard Module
```

Expanded view:

```text
+------------------------------------------------------+
|                  Sanaya Clients                      |
|  Desktop UI | Voice UI | Web Dashboard | Mobile App  |
+--------------------------+---------------------------+
                           |
                           v
+------------------------------------------------------+
|                 Sanaya Core Backend                  |
|  Orchestrator | Intent Router | Context Manager      |
|  Permission Engine | Workflow Engine | Event Bus     |
+--------------------------+---------------------------+
                           |
       +-------------------+-------------------+
       |                   |                   |
       v                   v                   v
+-------------+     +-------------+     +-------------+
| AI Module   |     | Memory      |     | Automation  |
| LLM Router  |     | Vector DB   |     | Plugins     |
| Tools       |     | Profiles    |     | OS/Web      |
+-------------+     +-------------+     +-------------+
       |                   |                   |
       v                   v                   v
OpenAI/Ollama/       PostgreSQL/SQLite/    Playwright/
Gemini/Claude        pgvector/Files        PowerShell/AutoHotkey
```

---

## Core Modules

### 1. Voice Module

Responsibilities:

- Wake word detection
- Microphone streaming
- Voice activity detection
- Speech-to-text
- Text-to-speech
- Voice interruption
- Speaker profile support in later phases

Voice flow:

```text
Wake Word
  -> Audio Capture
  -> Speech-to-Text
  -> Intent Router
  -> AI Module
  -> Text-to-Speech
  -> Speaker Output
```

### 2. AI Module

Responsibilities:

- Provider abstraction
- Model routing
- Prompt management
- Tool/function calling
- Reasoning policies
- Fallbacks between providers
- Cost and latency tracking
- Agent planning

The rest of Sanaya should call:

```ts
ai.generate()
ai.stream()
ai.embed()
ai.transcribe()
ai.summarize()
ai.routeTask()
```

It should never directly call a provider SDK.

### 3. Memory Module

Responsibilities:

- Short-term memory
- Long-term memory
- User preferences
- Task history
- Knowledge storage
- Embedding search
- Memory editing and deletion

Memory should be explicit, searchable, and user-controllable.

### 4. Automation Module

Responsibilities:

- Open applications
- Manage files
- Control browser
- Read documents
- Create reports
- Execute workflows
- Run plugins
- Request permission before risky actions

Automation flow:

```text
User Request
  -> Intent Router
  -> Tool Planner
  -> Permission Check
  -> Execute Plugin
  -> Verify Result
  -> Store Task History
```

### 5. Vision Module

Responsibilities:

- Screenshot capture
- Screen understanding
- OCR
- UI element detection
- Image analysis
- Document vision
- Future camera/device vision

This should be added after the assistant already has useful memory, chat, voice, and automation.

### 6. Web Module

Responsibilities:

- Web search
- Browser automation
- Website interaction
- Scraping with rules
- Form filling
- Web task execution

Recommended browser automation tool:

- Playwright

### 7. Security Module

Responsibilities:

- API key management
- Permission control
- Audit logs
- Sensitive data redaction
- Memory encryption
- Local/cloud routing policy
- User confirmation for dangerous actions

### 8. Dashboard Module

Responsibilities:

- Chat interface
- Voice controls
- Memory editor
- Workflow builder
- Plugin manager
- Logs and audit trail
- Model/provider configuration
- Permission settings

---

## AI Abstraction Layer

Sanaya must support:

- Local models through Ollama
- OpenAI API
- Google Gemini
- Anthropic Claude
- Future providers

Provider-neutral interface:

```ts
export interface AIProvider {
  id: string;

  generate(input: GenerateInput): Promise<GenerateOutput>;

  stream?(input: GenerateInput): AsyncIterable<GenerateChunk>;

  embed?(input: EmbedInput): Promise<EmbedOutput>;

  transcribe?(input: TranscribeInput): Promise<TranscribeOutput>;

  supports: {
    streaming: boolean;
    tools: boolean;
    vision: boolean;
    embeddings: boolean;
    local: boolean;
  };
}
```

Provider implementations:

```text
packages/ai-core/src/providers/
  openai.provider.ts
  ollama.provider.ts
  gemini.provider.ts
  anthropic.provider.ts
  mock.provider.ts
```

Routing example:

```ts
class AIModelRouter {
  async generate(task: AITask) {
    if (task.privacy === "local-only") {
      return this.providers.ollama.generate(task);
    }

    if (task.type === "fast-chat") {
      return this.providers.openai.generate(task);
    }

    if (task.type === "large-reasoning") {
      return this.providers.anthropic.generate(task);
    }

    return this.providers.default.generate(task);
  }
}
```

Recommended routing policy:

```text
Private documents:
  local-only by default

General conversation:
  cloud allowed

Heavy reasoning:
  OpenAI / Claude / Gemini

Offline mode:
  Ollama

Low-latency commands:
  smallest capable model
```

---

## Memory System

Sanaya should use five memory types.

```text
Short-Term Memory
  Recent conversation, active task state, temporary context

Long-Term Memory
  Important user facts, recurring patterns, personal history

Preferences
  Tone, writing style, favorite tools, daily habits, UI choices

Task History
  What Sanaya did, when, why, and whether it succeeded

Knowledge Storage
  Documents, notes, PDFs, websites, project data, embeddings
```

### MVP Storage

```text
SQLite:
  Local app database

Local vector store:
  Simple embeddings storage

File storage:
  Documents, screenshots, generated reports, audio
```

### Production Storage

```text
PostgreSQL:
  Primary database

pgvector:
  Embeddings and semantic memory search

Redis:
  Short-term sessions, queues, locks

S3-compatible storage:
  Files, audio, screenshots, document archives
```

Recommendation:

- Start with SQLite + Prisma.
- Move to PostgreSQL + Prisma + pgvector later.
- Use PostgreSQL as the system of record.
- Use MongoDB only if you specifically need flexible document-style logging.

---

## Voice System

### Wake Word

Free/local options:

- openWakeWord
- Mycroft Precise
- Howl

Premium/reliable option:

- Picovoice Porcupine

Recommendation:

```text
MVP:
  Push-to-talk first

Phase 2:
  Porcupine or openWakeWord

Production:
  Porcupine if licensing works
```

### Speech-to-Text

Free/local options:

- Whisper
- whisper.cpp
- Vosk

Premium/cloud options:

- OpenAI speech models
- Deepgram
- AssemblyAI
- Azure Speech

Recommendation for current hardware:

```text
MVP:
  Browser microphone + cloud STT

Local:
  whisper.cpp tiny/base model

Production:
  Hybrid STT with local fallback
```

### Text-to-Speech

Free/local options:

- Piper TTS
- Coqui TTS
- Windows built-in voices

Premium/cloud options:

- OpenAI TTS
- ElevenLabs
- Azure Neural TTS
- Google Cloud TTS

Recommendation:

```text
MVP:
  Browser speech synthesis or cloud TTS

Local:
  Piper

Premium:
  ElevenLabs or Azure Neural TTS
```

---

## Automation System

Sanaya should support:

- Opening applications
- Managing files
- Controlling browser
- Reading documents
- Creating reports
- Executing workflows
- Installing new skills/plugins

Recommended technologies:

```text
Open applications:
  PowerShell, Windows shell APIs, AutoHotkey

Manage files:
  Node fs, PowerShell, permission wrappers

Control browser:
  Playwright

Read documents:
  PDF parser, DOCX parser, OCR, embeddings

Create reports:
  Markdown, DOCX, PDF

Execute workflows:
  BullMQ, Temporal, or custom workflow engine
```

### Plugin Contract

```ts
export interface SanayaPlugin {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
  tools: SanayaTool[];
}

export interface SanayaTool {
  name: string;
  description: string;
  schema: unknown;
  risk: "low" | "medium" | "high";
  execute(input: unknown, context: ToolContext): Promise<ToolResult>;
}
```

Example plugins:

```text
plugins/
  filesystem/
  browser/
  email/
  calendar/
  documents/
  reports/
  code-assistant/
  windows-control/
  smart-home/
```

---

## Technology Stack

### Frontend

Recommended:

- Next.js
- React
- Tailwind CSS
- shadcn/ui
- Zustand or Redux Toolkit
- WebSocket client for live chat/voice events

### Desktop

Recommended:

- Tauri for a lightweight desktop assistant
- Electron only if mature Node desktop APIs become necessary

For the current laptop, Tauri is preferable because it is lighter.

### Backend

Recommended:

- Node.js
- TypeScript
- Fastify or NestJS
- WebSocket server
- REST API
- Event bus

Best choice:

```text
Fastify:
  Lightweight, fast, good for MVP

NestJS:
  Better if you want enterprise structure
```

### Database

MVP:

```text
SQLite + Prisma
```

Production:

```text
PostgreSQL + Prisma + pgvector
Redis for queues/cache
```

### AI Frameworks

Recommended:

- Vercel AI SDK for streaming UI
- LlamaIndex for document knowledge/RAG
- LangChain only where useful
- Custom orchestrator for Sanaya Core

Recommended strategy:

```text
Start custom.
Use AI SDK for streaming.
Add LangChain/LlamaIndex only where they reduce work.
```

### Authentication

MVP:

- Local user profile
- PIN/password
- Windows user binding

Production:

- Auth.js / NextAuth
- OAuth for connected services
- Role-based permissions
- Device trust model

### Deployment

Local:

- Windows app
- Local backend
- SQLite

Cloud:

- Vercel for dashboard
- Railway, Fly.io, or Render for backend
- Supabase or Neon for PostgreSQL
- Upstash Redis

Hybrid:

```text
Desktop Sanaya Agent:
  Local automation

Cloud Sanaya Brain:
  Optional intelligence and sync
```

---

## Scalability Roadmap

| Phase | Name | Features | Technologies | Difficulty | Timeline |
|---|---|---|---|---|---|
| 1 | Minimum Viable Product | Chat UI, cloud LLM, basic memory, dashboard, manual commands | Next.js, Node.js, SQLite, OpenAI/Gemini | Medium | 4-8 weeks |
| 2 | Local AI Assistant | Ollama support, local STT/TTS, wake word, offline mode | Ollama, Whisper, Piper, Tauri | Medium-High | 2-3 months |
| 3 | Advanced Automation | File ops, browser control, workflows, plugins | Playwright, PowerShell, AutoHotkey, BullMQ | High | 3-5 months |
| 4 | Vision and Screen Understanding | Screenshot analysis, OCR, UI detection, document vision | Tesseract, vision LLMs, OpenCV | High | 3-6 months |
| 5 | Multi-Agent System | Planner, executor, researcher, critic, memory agent | Custom agents, queues, evals | Very High | 6-12 months |
| 6 | Personal AI Operating System | Mobile, smart home, business workflows, marketplace | Mobile app, Home Assistant, cloud sync | Very High | 1-3 years |

Recommended build order:

```text
1. Core backend with AI abstraction
2. Chat dashboard
3. Memory system
4. Tool/plugin system
5. Local desktop agent
6. Voice pipeline
7. Automation
8. Vision
9. Multi-agent workflows
10. Mobile and smart devices
```

---

## Production Folder Structure

```text
sanaya/
  apps/
    web-dashboard/
      src/
        app/
        components/
        features/
        hooks/
        lib/
        styles/
    desktop/
      src/
        main/
        renderer/
        preload/
    mobile/
      src/
    local-agent/
      src/
        windows/
        audio/
        automation/
        screen/
  services/
    api/
      src/
        main.ts
        app.module.ts
        config/
        modules/
          ai/
          memory/
          voice/
          automation/
          vision/
          web/
          security/
          workflows/
          plugins/
        common/
        events/
        jobs/
    worker/
      src/
        queues/
        processors/
    voice-service/
      src/
        wake-word/
        stt/
        tts/
    automation-service/
      src/
        browser/
        filesystem/
        apps/
        documents/
  packages/
    ai-core/
      src/
        providers/
        router/
        prompts/
        tools/
    memory-core/
      src/
        schemas/
        retrieval/
        embeddings/
    plugin-sdk/
      src/
        types/
        permissions/
        runtime/
    security-core/
      src/
        vault/
        encryption/
        policies/
    shared/
      src/
        types/
        constants/
        utils/
  plugins/
    filesystem/
    browser/
    reports/
    email/
    calendar/
    windows-control/
  prisma/
    schema.prisma
    migrations/
  storage/
    documents/
    audio/
    screenshots/
    reports/
  scripts/
    setup/
    dev/
    db/
  docs/
    architecture/
    security/
    api/
    plugins/
  tests/
    unit/
    integration/
    e2e/
  docker/
    docker-compose.yml
  package.json
  pnpm-workspace.yaml
  turbo.json
  README.md
```

---

## Database Schema

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE conversations (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  title TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE messages (
  id UUID PRIMARY KEY,
  conversation_id UUID REFERENCES conversations(id),
  role TEXT CHECK (role IN ('user', 'assistant', 'system', 'tool')),
  content TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE memories (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  type TEXT CHECK (type IN ('fact', 'preference', 'task', 'knowledge')),
  content TEXT NOT NULL,
  importance INTEGER DEFAULT 1,
  source TEXT,
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE memory_embeddings (
  id UUID PRIMARY KEY,
  memory_id UUID REFERENCES memories(id),
  embedding VECTOR(1536),
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  title TEXT NOT NULL,
  status TEXT CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  input JSONB,
  result JSONB,
  created_at TIMESTAMP DEFAULT now(),
  completed_at TIMESTAMP
);

CREATE TABLE plugins (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  enabled BOOLEAN DEFAULT false,
  permissions JSONB,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  action TEXT NOT NULL,
  resource TEXT,
  risk_level TEXT,
  approved BOOLEAN,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT now()
);
```

---

## API Design

```text
POST   /api/chat
POST   /api/chat/stream

GET    /api/memory
POST   /api/memory
PUT    /api/memory/:id
DELETE /api/memory/:id

GET    /api/tasks
POST   /api/tasks
GET    /api/tasks/:id
POST   /api/tasks/:id/cancel

GET    /api/plugins
POST   /api/plugins/:id/enable
POST   /api/plugins/:id/disable

GET    /api/permissions/pending
POST   /api/permissions/:id/approve
POST   /api/permissions/:id/deny

POST   /api/voice/transcribe
POST   /api/voice/speak

POST   /api/automation/run
POST   /api/web/browse
POST   /api/documents/ingest
```

WebSocket endpoint:

```text
ws://localhost:SANAYA_PORT/events
```

Example event:

```json
{
  "type": "ai.token",
  "conversationId": "uuid",
  "data": {
    "text": "Sure, I can help with that."
  }
}
```

---

## Security Design

### API Key Management

Use:

```text
Local development:
  .env.local

Desktop production:
  Encrypted local vault

Cloud:
  Provider secret manager
```

Never store raw API keys in the database.

### User Privacy

Every memory should include:

```text
source
created_at
importance
visibility
delete option
cloud_allowed flag
```

Sanaya should be able to answer:

```text
What do you remember about me?
```

And obey:

```text
Forget this.
```

### Memory Encryption

Use:

- AES-256-GCM for encrypted fields
- Windows Credential Manager for local secret keys
- Cloud KMS later

### Permission Control

Risk levels:

```text
Low:
  Read time, summarize local note, answer question

Medium:
  Open app, create file, send draft

High:
  Delete files, send email, make purchase, modify system settings
```

High-risk actions require explicit user approval.

### Local vs Cloud Processing

Policy example:

```text
Private documents:
  Local-only by default

General reasoning:
  Cloud allowed

Voice audio:
  User configurable

Passwords/API keys:
  Never sent to LLM

Automation commands:
  Logged and permission checked
```

---

## Hardware Reality Check

Current hardware:

```text
Intel Core i5 1.60 GHz
8 GB RAM
Intel UHD Graphics 620
Windows laptop
```

Suitable for:

- Dashboard
- Local agent
- Wake word
- Basic local speech-to-text
- Small local LLMs
- Browser automation
- Cloud-powered AI

Not ideal for:

- Large local LLMs
- Real-time heavy vision models
- Heavy multi-agent local inference
- High-quality local voice generation at scale

Recommended local models:

```text
1.5B to 3B quantized models
Small embedding models
Whisper tiny/base
Piper TTS
```

Use cloud models for heavy reasoning until the hardware is upgraded.

---

## Future Expansion

### Desktop Assistant

Recommended stack:

```text
Tauri + local-agent + Windows APIs
```

Capabilities:

- Voice overlay
- File automation
- App control
- Screen understanding
- Personal workflows

### Mobile Assistant

Recommended stack:

```text
React Native / Expo
```

Capabilities:

- Voice commands
- Notifications
- Location-aware help
- Mobile memory sync
- Smart home control

### Smart Home Assistant

Recommended stack:

```text
Home Assistant
MQTT
Matter devices
```

Capabilities:

- Lights
- Sensors
- Routines
- Security camera summaries
- Household automation

### Business Assistant

Recommended integrations:

```text
Google Workspace
Microsoft Graph
Slack
Notion
CRM systems
```

Capabilities:

- Meeting summaries
- Report generation
- Email drafting
- Research
- Task automation

### AI Agent Platform

Future Sanaya platform APIs:

```text
Plugin SDK
Agent SDK
Workflow marketplace
Memory API
Tool registry
Device connectors
```

---

## CTO Recommendation

Build Sanaya in this order:

```text
1. Core backend with AI abstraction
2. Chat dashboard
3. Memory system
4. Tool/plugin system
5. Local desktop agent
6. Voice pipeline
7. Automation
8. Vision
9. Multi-agent workflows
10. Mobile and smart devices
```

The winning architecture is not one powerful model.

The winning architecture is:

```text
Modular core
Provider-independent AI layer
Explicit memory
Permissioned automation
Local-first privacy
Plugin-based expansion
```

That is how Sanaya can survive 5-10 years without becoming a rewrite trap.

