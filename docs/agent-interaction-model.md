# Agent Interaction Model

How agents communicate, negotiate, and orchestrate within the Singularion Nexus mesh.

---

## Communication Protocol

### Mesh Protocol (NexusMP)

All agent-to-agent communication flows through **NexusMP** — a peer-to-peer protocol designed for:

- **Low-latency negotiation** (sub-millisecond within clusters)
- **Encrypted channels** (quantum-resistant encryption via Zeta's fabric)
- **Intent-addressed routing** (messages addressed to capabilities, not specific agents)
- **Multi-cast support** (broadcast to domain clusters or the entire mesh)

### Message Types

| Type | Purpose | Example |
|------|---------|---------|
| `INTENT` | New intent or sub-intent | "Optimize portfolio for risk-adjusted returns" |
| `BID` | Agent's offer to handle a sub-task | Lynx bids on opportunity detection |
| `COMMIT` | Agent accepts a sub-task | Merlin commits to forecast generation |
| `RESULT` | Sub-task output | Grimma returns risk assessment |
| `SIGNAL` | Real-time event or alert | Quasar signals energy price spike |
| `NEGOTIATE` | Multi-turn negotiation | Eclips negotiating deal terms |
| `FEEDBACK` | Post-execution quality signal | Satori validates product quality |
| `EVOLVE` | System evolution proposal | Kaelix proposes topology change |

---

## Negotiation Patterns

### 1. Auction-Based (Competitive)

Used when multiple agents could handle a task and the best should be selected.

```
Intent Owner ──► Broadcast INTENT to cluster
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     Agent A     Agent B     Agent C
     (BID: $x)   (BID: $y)   (BID: $z)
        │           │           │
        └───────────┼───────────┘
                    ▼
            Best BID selected
                    │
                    ▼
             COMMIT → Execute
```

**Example**: Investment opportunity → Lynx, Spectra, and Merlin each bid with different strategies. Best risk-adjusted approach wins.

### 2. Consensus-Based (Collaborative)

Used when a task requires multi-agent agreement.

```
Proposer ──► NEGOTIATE to coalition
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
 Agent A     Agent B     Agent C
 (VOTE)      (VOTE)      (VOTE)
    │           │           │
    └───────────┼───────────┘
                ▼
         Consensus reached?
          ├─ YES → COMMIT all
          └─ NO  → Re-negotiate
```

**Example**: High-value asset transfer → Umbrex, Rhino, and Grimma must all agree the risk is acceptable.

### 3. Pipeline (Sequential)

Used when tasks have natural dependencies.

```
Agent A ──RESULT──► Agent B ──RESULT──► Agent C ──RESULT──► Output
(Sense)            (Analyze)            (Execute)
```

**Example**: Pulse (sense trend) → Aurora Nexus (design product) → Hype (launch) → Pulsar (viralize)

### 4. Swarm (Parallel Fan-out)

Used for maximum speed on decomposable tasks.

```
              ┌──► Agent A ──┐
              │              │
Intent ───────┼──► Agent B ──┼───► Synthesize
              │              │
              └──► Agent C ──┘
```

**Example**: Full market analysis → Merlin (macro) + Spectra (patterns) + Grimma (risks) + Lynx (opportunities) all execute simultaneously, results merged.

---

## Coalition Formation

When an intent arrives, Kaelix decomposes it and forms a **coalition** — a temporary team of agents optimized for the task.

### Formation Algorithm

```
1. DECOMPOSE intent into capability requirements
2. MATCH capabilities to agent skills (weighted by reputation + load)
3. FORM coalition with optimal agent set
4. ASSIGN roles: Lead, Support, Validator
5. ESTABLISH communication channels within coalition
6. EXECUTE with real-time coordination
7. DISSOLVE coalition after fulfillment + feedback
```

### Coalition Roles

| Role | Responsibility |
|------|----------------|
| **Lead** | Primary executor, owns the output quality |
| **Support** | Provides auxiliary data, computation, or validation |
| **Validator** | Independent verification of results (typically from a different domain) |
| **Guardian** | Monitors for risks/threats during execution (Grimma, Rhino, or Umbrex) |
| **Timer** | Manages temporal constraints (Aion or Kairos) |

---

## Cross-Domain Bridges

Key interaction patterns between domains:

### Financial ↔ Temporal
```
Merlin (forecast) ──► Kairos (timing) ──► Nexus (execute at optimal moment)
Aion (time-lock) ──► Helix (smart contract with temporal clause)
```

### Product ↔ Consumer Intelligence
```
Pulse (trend signal) ──► Aurora Nexus (product vision)
Tango (co-creation input) ──► Cerebra (R&D)
Satori (quality gate) ──► Raison (design iteration)
Echoflux (emotional data) ──► Quirk (delight features)
```

### Brand ↔ Consumer Experience
```
Hype (demand wave) ──► Nexa (seamless fulfillment)
Vega (brand promise) ──► Diva (personalized delivery)
Pulsar (viral moment) ──► Oasis (immersive experience)
```

### Financial ↔ Asset Protection
```
Eclips (deal in progress) ──► Rhino (security perimeter)
Kapital (portfolio change) ──► Umbrex (legacy impact check)
Grimma (threat detected) ──► Rhino (activate defense)
```

---

## Conflict Resolution

When agents disagree (conflicting bids, contradictory assessments):

1. **Reputation-weighted voting** — higher reputation = more weight
2. **Stake escalation** — agents can increase their stake to signal confidence
3. **Domain arbiter** — the domain's senior agent arbitrates (e.g., Grimma for risk disputes)
4. **Kaelix override** — meta-architect resolves cross-domain conflicts
5. **Human escalation** — ultimate fallback for high-stakes unresolvable conflicts

---

## Feedback & Evolution

```
Execution Complete
       │
       ▼
  Feedback Collection
  (Satori validates, Pulse measures, Echoflux senses)
       │
       ▼
  Reputation Update
  (On-chain, affects future coalition formation)
       │
       ▼
  Kaelix Evolution Check
  (Should the mesh topology change?)
       │
       ├─ YES → EVOLVE message → Mesh reconfiguration
       └─ NO  → Continue
```
