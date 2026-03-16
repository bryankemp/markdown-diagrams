# Invention Disclosure

## Disclosure 1 – Hardware Injection

### Diagrams

**Flowchart – License Injection Process**

```mermaid
flowchart TD
    A[Device Connected] --> B[OS Loads Driver]
    B --> C[Read License Token]
    C --> D{Valid?}
    D -- Yes --> E[Inject License]
    D -- No --> F[Abort]
```

**Sequence Diagram – Driver Interaction**

```mermaid
sequenceDiagram
    participant HW as Hardware
    participant DRV as Driver
    participant ES as Entitlement Service
    HW->>DRV: Device connected
    DRV->>ES: InjectLicense
    ES-->>DRV: Ack
```

## Disclosure 2 – Multi-Source Architecture

### Diagrams

**Flowchart – License Evaluation**

```mermaid
flowchart TD
    A[Request] --> B{HW License?}
    B -->|Yes| C[Grant]
    B -->|No| D{SW License?}
    D -->|Yes| C
    D -->|No| E[Deny]
```
