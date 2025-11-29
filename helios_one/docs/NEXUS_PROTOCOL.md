# THE NEXUS PROTOCOL (SPECIFICATION v1.0)

**Purpose:** Enable decentralized, resilient communication between autonomous Helios Shards.

## 1. Core Principles
- **No Central Broker:** Shards communicate peer-to-peer via a distributed hash table (DHT) or gossip protocol.
- **Eventual Consistency:** Global state converges over time; local operations are never blocked by network latency.
- **Identity-Based Addressing:** Shards are addressed by cryptographic public keys, not IP addresses.

## 2. Message Structure
All messages must adhere to the `HeliosMessage` schema:
```json
{
  "id": "uuid-v4",
  "sender": "shard-public-key",
  "recipient": "shard-public-key" | "broadcast",
  "timestamp": 1732900000.0,
  "type": "state_update" | "resource_request" | "pattern_discovery",
  "payload": { ... },
  "signature": "ed25519-signature"
}
```

## 3. Synchronization Mechanism
- **Gossip:** Shards randomly select peers to exchange state summaries.
- **Vector Clocks:** Used to order events and detect causality violations.
- **Conflict Resolution:** "Last Writer Wins" (LWW) for simple state; CRDTs (Conflict-Free Replicated Data Types) for complex structures like the Knowledge Graph.

## 4. Implementation Plan
1.  `src/helios/nexus.py`: Core networking logic.
2.  `src/helios/sync.py`: State reconciliation engine.
3.  `tests/test_nexus.py`: Multi-process simulation of shard interaction.
