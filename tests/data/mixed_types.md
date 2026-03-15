# Mixed Diagram Types

## Class Hierarchy

```mermaid
classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal : +int age
    Animal : +String gender
    Animal : +isMammal()
    Duck : +String beakColor
    Duck : +swim()
    Fish : +int sizeInFeet
    Fish : +canEat()
```

## State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : submit
    Processing --> Done : complete
    Processing --> Error : fail
    Error --> Idle : retry
    Done --> [*]
```

## Data Model

```er
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER {
        string name
        string email
    }
    ORDER {
        int id
        date created
    }
```

Some trailing text after the diagrams.
