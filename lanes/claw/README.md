# claw — OpenClaw Fleet Cell (SuperInstance Fork)

**claw** is the SuperInstance fork of [OpenClaw](https://github.com/openclaw/openclaw), an open-source multi-channel AI gateway that routes messages between platforms (Telegram, LINE, WhatsApp, Discord, Web) and AI model providers with pluggable skills, memory, and safety layers. This fork extends OpenClaw with fleet-native integrations: ternary action routing, conservation-aware scheduling, and the γ + η = C enforcement that keeps the agent population in healthy equilibrium.

## Why It Matters

AI assistants are fragmented across platforms — a user might interact via Telegram, LINE, WhatsApp, and a web chat simultaneously. OpenClaw solves this by providing a unified gateway with channel adapters, plugin SDK, and a session model that maintains conversational state across channels. The SuperInstance fork goes further: it treats each message-processing cycle as a ternary action (avoid unknown inputs, defer uncertain ones, choose confident responses), enabling the fleet's conservation framework to operate on real conversational data. The built-in cron scheduler, heartbeat system, and subagent spawning make it suitable for autonomous long-running operation — not just request-response chat.

## How It Works

### Channel Architecture

OpenClaw uses a **channel adapter pattern**: each platform (Telegram, LINE, WhatsApp, Discord, Web) has an adapter that normalizes incoming messages into a common internal format and denormalizes outgoing responses back to platform-specific formats (e.g., Telegram markdown vs. WhatsApp plain text vs. LINE Flex messages).

```
Platform → Adapter → NormalizedMessage → Router → Provider (LLM) → Response → Adapter → Platform
```

The router supports **model routing** — different models can handle different message types based on cost, latency, and capability requirements.

### Session & Memory Model

Each conversation has a **session** with persistent state. The memory system uses a two-tier architecture:
- **Daily notes** (`memory/YYYY-MM-DD.md`): Raw event logs, per-session.
- **Long-term memory** (`MEMORY.md`): Curated knowledge, distilled from daily notes.

Sessions can spawn **subagents** — isolated contexts for specific tasks that report back to the main session. This enables parallel task execution without polluting the main conversation context.

### Skill System

Skills are self-contained modules with a `SKILL.md` manifest. The system scans available skills, loads the relevant one for each task, and provides tool access (shell, web, file I/O). Skills compose — a task can invoke multiple skills in sequence.

### Plugin SDK

The plugin SDK provides extension points for custom channels, providers, and tools. Plugins are loaded dynamically and have access to the full message pipeline.

### Ternary Routing (SuperInstance Extension)

In the SuperInstance fork, the routing layer classifies each incoming message as:
- **Avoid (−1)**: Spam, unsafe content, or messages outside the agent's competence. Routed to a safety rejection.
- **Unknown (0)**: Ambiguous messages requiring clarification. Routed to a clarification flow.
- **Choose (+1)**: Clear, actionable messages. Routed to the primary LLM provider.

The ratios of these classifications feed directly into the γ + η = C conservation framework. When γ_drift is detected (too many avoids), the router can lower its confidence threshold to convert Unknown → Choose, increasing η (entropy/diversity).

### Complexity

| Operation | Complexity |
|-----------|-----------|
| Message routing | $O(1)$ hash lookup per channel |
| Session context retrieval | $O(k)$ where $k$ = context window size |
| Skill matching | $O(n)$ over $n$ available skills |
| Ternary classification | $O(1)$ per message (threshold comparison) |

## Quick Start

```bash
# Clone the fork
git clone https://github.com/SuperInstance/claw.git
cd claw
npm install

# Configure
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys and channel tokens

# Build and run
npm run build
npm start

# Or use the CLI
npx openclaw gateway start
```

```typescript
// Plugin SDK example
import { PluginSDK } from 'openclaw/plugin-sdk';

export default PluginSDK.createChannel({
  name: 'my-channel',
  async onMessage(msg) {
    const response = await this.routeToProvider(msg);
    await this.send(msg.channelId, response);
  },
});
```

## API

### Core Modules

```typescript
// Gateway lifecycle
entry.ts          → Process entry point
gateway/          → HTTP gateway server
runtime.ts        → Runtime context and configuration

// Channels
channels/         → Platform adapters (Telegram, WhatsApp, LINE, Discord, Web)
line/             → LINE Messaging API integration
whatsapp/         → WhatsApp Business API integration

// Agent Infrastructure
agents/           → Agent definitions and spawning
sessions/         → Session management and context
memory/           → Two-tier memory system
commands/         → Slash command handlers
hooks/            → Lifecycle hooks (pre-message, post-response)
cron/             → Scheduled tasks

// Extension Points
plugin-sdk/       → Plugin development kit
providers/        → LLM provider adapters (OpenAI, Anthropic, etc.)
skills/           → Skill manifests and loaders
config/           → Configuration management
```

### Key Config (config.yaml)

```yaml
channels:
  telegram:
    token: ${TELEGRAM_BOT_TOKEN}
  line:
    channelAccessToken: ${LINE_CHANNEL_TOKEN}
    channelSecret: ${LINE_CHANNEL_SECRET}

providers:
  primary:
    model: claude-sonnet-4
    maxTokens: 8192

memory:
  type: file
  path: ./memory

conservation:  # SuperInstance extension
  enabled: true
  gammaThreshold: 0.95
  etaFloor: 0.3
```

## Architecture Notes

claw is the **cellular logic engine** of the SuperInstance fleet — it runs inside each fleet node and provides the conversational interface through which humans interact with the agent ecosystem. The ternary routing extension makes every message a data point in the conservation framework: high avoid ratios (γ → −1) signal that the system is overwhelmed with noise, while high entropy (η → max) indicates healthy diverse interactions. The heartbeat system provides the periodic polling mechanism that monitors conservation compliance and triggers corrective actions when C drifts.

See: [SuperInstance Architecture](https://github.com/SuperInstance/SuperInstance/blob/main/ARCHITECTURE.md)

## References

1. OpenClaw Project. "Multi-Channel AI Gateway." [docs.openclaw.ai](https://docs.openclaw.ai) — Official documentation for the upstream project.
2. Gamma, E. et al. (1994). *Design Patterns.* — The channel adapter and plugin patterns used in the architecture.

## License

MIT
