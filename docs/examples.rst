Diagram Examples
================

This page demonstrates every Mermaid diagram type that ``markdown-diagrams``
can extract and render.  The diagrams below are rendered live using the
Mermaid JavaScript library.

.. tip::

   The source for all of these examples is also available in
   `examples/all_diagram_types.md <https://github.com/bryankemp/markdown-diagrams/blob/main/examples/all_diagram_types.md>`_
   which you can render locally with:

   .. code-block:: bash

      markdown-diagrams extract examples/all_diagram_types.md -o output/

Flowchart
---------

Top-down decision flow:

.. mermaid::

   flowchart TD
       A[Start] --> B{Decision}
       B -->|Yes| C[Action A]
       B -->|No| D[Action B]
       C --> E[End]
       D --> E

Left-to-right data pipeline:

.. mermaid::

   flowchart LR
       Input[User Input] --> Validate[Validate Data]
       Validate --> Process[Process Request]
       Process --> Store[(Database)]
       Process --> Cache[(Redis Cache)]
       Store --> Response[Send Response]
       Cache --> Response

Graph
-----

System architecture:

.. mermaid::

   graph TD
       A[Web Browser] --> B[Load Balancer]
       B --> C[App Server 1]
       B --> D[App Server 2]
       C --> E[(Primary DB)]
       D --> E
       E --> F[(Replica DB)]

Sequence Diagram
----------------

API authentication flow:

.. mermaid::

   sequenceDiagram
       participant Client
       participant Gateway as API Gateway
       participant Auth as Auth Service
       participant API as Backend API
       participant DB as Database

       Client->>Gateway: POST /login (credentials)
       Gateway->>Auth: Validate credentials
       Auth->>DB: Query user record
       DB-->>Auth: User data
       Auth-->>Gateway: JWT token
       Gateway-->>Client: 200 OK (token)

       Client->>Gateway: GET /data (Bearer token)
       Gateway->>Auth: Verify token
       Auth-->>Gateway: Token valid
       Gateway->>API: Forward request
       API->>DB: Fetch data
       DB-->>API: Results
       API-->>Gateway: JSON response
       Gateway-->>Client: 200 OK (data)

Class Diagram
-------------

Observer design pattern:

.. mermaid::

   classDiagram
       class Subject {
           -List~Observer~ observers
           +attach(Observer o)
           +detach(Observer o)
           +notify()
       }
       class Observer {
           <<interface>>
           +update(String event)
       }
       class ConcreteSubject {
           -String state
           +getState() String
           +setState(String s)
       }
       class ConcreteObserverA {
           +update(String event)
       }
       class ConcreteObserverB {
           +update(String event)
       }

       Subject <|-- ConcreteSubject
       Observer <|.. ConcreteObserverA
       Observer <|.. ConcreteObserverB
       Subject o-- Observer

State Diagram
-------------

Order lifecycle:

.. mermaid::

   stateDiagram-v2
       [*] --> Draft
       Draft --> Submitted : Customer submits
       Submitted --> Processing : Payment confirmed
       Processing --> Shipped : Items dispatched
       Shipped --> Delivered : Carrier confirms
       Delivered --> [*]

       Submitted --> Cancelled : Customer cancels
       Processing --> Cancelled : Out of stock
       Cancelled --> [*]

       Delivered --> Returned : Return requested
       Returned --> Refunded : Refund processed
       Refunded --> [*]

Entity Relationship Diagram
---------------------------

E-commerce data model:

.. mermaid::

   erDiagram
       CUSTOMER ||--o{ ORDER : places
       CUSTOMER {
           int id PK
           string name
           string email
           date created_at
       }
       ORDER ||--|{ LINE_ITEM : contains
       ORDER {
           int id PK
           date order_date
           string status
           float total
       }
       LINE_ITEM }|--|| PRODUCT : references
       LINE_ITEM {
           int id PK
           int quantity
           float unit_price
       }
       PRODUCT {
           int id PK
           string name
           string sku
           float price
           int stock
       }

Gantt Chart
-----------

Product launch timeline:

.. mermaid::

   gantt
       title Product Launch Plan
       dateFormat YYYY-MM-DD
       axisFormat %b %d

       section Planning
           Market Research       :done, research, 2026-01-06, 14d
           Requirements          :done, reqs, after research, 7d
           Technical Design      :done, design, after reqs, 10d

       section Development
           Backend API           :active, backend, 2026-02-03, 21d
           Frontend UI           :active, frontend, 2026-02-10, 21d
           Integration Testing   :integration, after backend, 10d

       section Launch
           Beta Release          :milestone, beta, 2026-03-17, 0d
           User Feedback         :feedback, after beta, 14d
           Bug Fixes             :fixes, after feedback, 7d
           Public Release        :milestone, launch, 2026-04-14, 0d

Pie Chart
---------

Programming language distribution:

.. mermaid::

   pie title Languages in Codebase
       "Python" : 45
       "TypeScript" : 25
       "Go" : 15
       "Shell" : 10
       "Other" : 5

Mindmap
-------

Software architecture concepts:

.. mermaid::

   mindmap
       root((Software Architecture))
           Patterns
               MVC
               Microservices
               Event-Driven
               Layered
           Quality Attributes
               Scalability
               Reliability
               Security
               Performance
           Infrastructure
               Containers
               Kubernetes
               CI/CD
               Monitoring
           Data
               SQL Databases
               NoSQL
               Message Queues
               Caching

Git Graph
---------

Feature branch workflow:

.. mermaid::

   gitGraph
       commit id: "init"
       commit id: "base setup"
       branch feature/auth
       checkout feature/auth
       commit id: "add login"
       commit id: "add JWT"
       checkout main
       branch feature/api
       checkout feature/api
       commit id: "add endpoints"
       commit id: "add validation"
       checkout main
       merge feature/auth id: "merge auth"
       merge feature/api id: "merge api"
       commit id: "v1.0.0" tag: "v1.0.0"

User Journey
------------

Online shopping experience:

.. mermaid::

   journey
       title Customer Purchase Journey
       section Browse
           Visit homepage      : 5 : Customer
           Search for product  : 4 : Customer
           View product page   : 4 : Customer
       section Purchase
           Add to cart         : 5 : Customer
           Enter shipping info : 3 : Customer
           Enter payment       : 2 : Customer
           Confirm order       : 4 : Customer
       section Post-Purchase
           Receive confirmation: 5 : Customer, System
           Track shipment      : 4 : Customer, System
           Receive delivery    : 5 : Customer

Quadrant Chart
--------------

Technology evaluation matrix:

.. mermaid::

   quadrantChart
       title Technology Adoption Readiness
       x-axis Low Maturity --> High Maturity
       y-axis Low Impact --> High Impact
       quadrant-1 Adopt Now
       quadrant-2 Evaluate
       quadrant-3 Avoid
       quadrant-4 Monitor
       Kubernetes: [0.85, 0.90]
       WebAssembly: [0.45, 0.70]
       GraphQL: [0.70, 0.65]
       Blockchain: [0.40, 0.35]
       Serverless: [0.75, 0.80]
       Quantum Computing: [0.15, 0.55]

Requirement Diagram
-------------------

System requirements:

.. mermaid::

   requirementDiagram

   requirement high_availability {
   id: 1
   text: System shall maintain 99.9 percent uptime
   risk: high
   verifymethod: test
   }

   requirement data_encryption {
   id: 2
   text: All data at rest shall be encrypted
   risk: medium
   verifymethod: inspection
   }

   requirement response_time {
   id: 3
   text: API responses shall complete within 200ms
   risk: medium
   verifymethod: test
   }

   element load_balancer {
   type: component
   docref: arch_lb
   }

   element encryption_module {
   type: component
   docref: arch_crypto
   }

   load_balancer - satisfies -> high_availability
   encryption_module - satisfies -> data_encryption
   load_balancer - satisfies -> response_time

C4 Context Diagram
------------------

System context overview:

.. mermaid::

   C4Context
       title System Context Diagram - Online Store

       Person(customer, "Customer", "Browses and purchases products")
       Person(admin, "Admin", "Manages products and orders")

       System(store, "Online Store", "Allows customers to browse and buy products")

       System_Ext(payment, "Payment Gateway", "Processes credit card payments")
       System_Ext(email, "Email Service", "Sends order confirmations")
       System_Ext(shipping, "Shipping Provider", "Handles package delivery")

       Rel(customer, store, "Uses", "HTTPS")
       Rel(admin, store, "Manages", "HTTPS")
       Rel(store, payment, "Processes payments", "HTTPS/API")
       Rel(store, email, "Sends emails", "SMTP")
       Rel(store, shipping, "Creates shipments", "HTTPS/API")
