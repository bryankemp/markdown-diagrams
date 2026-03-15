# Fixable Diagrams

A file whose Mermaid blocks contain common formatting issues that
`fix_diagram` can correct automatically.

## 2.1 Login Flow

```mermaid
flowchart TD   
    A[Start (Init)] --> B{Check Token (valid)?}   
    B -->|Yes (cached)| C[Grant Access]   
    B -->|No| D[Redirect to Login]   
```

## 2.2 Simple Graph

```mermaid
graph LR
    X[Begin] --> Y[Finish]
```
