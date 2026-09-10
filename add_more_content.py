import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "pydah_skillpath.db")

NEW_PLACEMENTS = [
    (
        "Cisco Systems",
        "Network Security & Cloud Infrastructure Engineer",
        "Super Dream",
        19.5,
        "Bengaluru (Hybrid)",
        "2026 Batch B.Tech CSE, IT, ECE with CGPA 7.5+",
        "Python, TCP/IP, Linux Networking, Docker, AWS/Azure, Network Security Protocols, Kubernetes",
        "https://www.cisco.com/c/en_in/about/careers.html",
        "2026-10-18",
        "Online Diagnostic Assessment + Technical Architecture Rounds + Managerial Evaluation",
        1
    ),
    (
        "Oracle Cloud Infrastructure (OCI)",
        "Cloud Systems & Distributed Infrastructure Engineer",
        "Super Dream",
        22.0,
        "Hyderabad (On-site)",
        "2026 B.Tech CSE, IT, ECE with strong OS & Systems knowledge",
        "Java, Go, Linux Internals, Distributed Systems, Docker, Kubernetes, Terraform, High Availability",
        "https://www.oracle.com/corporate/careers/",
        "2026-10-25",
        "HackerRank Coding Test + Distributed Systems Design + Core Interview Loop",
        1
    ),
    (
        "Adobe",
        "Frontend & Web Experience Systems Engineer",
        "Super Dream",
        24.0,
        "Bengaluru / Noida (Hybrid)",
        "2026 B.Tech CSE / IT with Web Systems portfolio",
        "JavaScript, TypeScript, React, WebGL, WebAssembly, Browser Performance, Canvas API, RESTful APIs",
        "https://careers.adobe.com",
        "2026-11-02",
        "Online Coding Challenge + UI Architecture & DOM Optimization Round + Behavioral",
        1
    ),
    (
        "Broadcom",
        "ASIC Physical Design & Verification Engineer",
        "Super Dream",
        21.0,
        "Bengaluru (On-site)",
        "2026 B.Tech / M.Tech ECE with Digital Electronics proficiency",
        "Verilog, SystemVerilog, UVM, Static Timing Analysis (STA), Synopsys Design Compiler, CMOS VLSI",
        "https://www.broadcom.com/careers",
        "2026-10-30",
        "VLSI Logic Screening + STA Timing Analysis Round + Digital Design Technical Interview",
        1
    ),
    (
        "MediaTek India",
        "SoC Architecture & Embedded Linux Kernel Engineer",
        "Super Dream",
        16.0,
        "Noida / Bengaluru (Hybrid)",
        "2026 B.Tech ECE, EEE, CSE with Embedded systems mastery",
        "Embedded C, ARM Cortex Architecture, Linux Kernel Device Drivers, I2C, SPI, DMA, RTOS",
        "https://www.mediatek.com/careers",
        "2026-11-10",
        "Embedded C & OS Assessment + Device Driver Coding Challenge + Technical Board Interview",
        1
    ),
    (
        "Juniper Networks",
        "Cyber Threat Defense & Cloud Security Engineer",
        "Super Dream",
        18.0,
        "Bengaluru (Hybrid)",
        "2026 B.Tech CSE, IT, ECE with Cyber Defense focus",
        "Firewalls, Zero Trust, Python, Penetration Testing, SIEM, Snort, Linux Hardening, Wireshark",
        "https://www.juniper.net/us/en/company/careers.html",
        "2026-10-28",
        "Security Assessment + CTF Style Practical Challenge + Technical Panel",
        1
    ),
    (
        "Tata Elxsi",
        "Autonomous Driving & Automotive EV Software Engineer",
        "Dream",
        9.5,
        "Bengaluru / Pune (On-site)",
        "2026 B.Tech ECE, EEE, Mech, CSE with Automotive/Embedded interest",
        "C++, AUTOSAR, CAN Bus, ROS2, Sensor Fusion, Embedded Linux, Simulink",
        "https://www.tataelxsi.com/careers",
        "2026-11-05",
        "Aptitude & Technical MCQ + C++ Coding Test + Automotive Domain Interview",
        1
    ),
    (
        "Zoho Corporation",
        "Full Stack Web Product Developer",
        "Dream",
        8.5,
        "Chennai / Tirunelveli (On-site)",
        "2026 Any B.Tech branch with strong coding fundamentals",
        "Java, JavaScript, C, Data Structures, OOP, SQL, Web Security, System Design",
        "https://www.zoho.com/careers/",
        "2026-10-15",
        "Multi-round Zoho Incubation Coding: Basic C/Java -> Advanced App Design -> Tech Interview",
        1
    ),
    (
        "Siemens India",
        "Industrial Automation & Smart Grid Controls Engineer",
        "Dream",
        9.0,
        "Bengaluru / Goa (On-site)",
        "2026 B.Tech EEE, ECE, Instrumentation with 65%+ aggregate",
        "PLC Programming, SCADA, IEC 61850, Modbus, Power Systems, Python, Industrial IoT",
        "https://www.siemens.com/in/en/company/jobs.html",
        "2026-11-12",
        "Industrial Automation Screening + Core Power Electronics / Control Systems Interview",
        1
    ),
    (
        "Ather Energy",
        "EV Motor Control & Embedded Firmware Engineer",
        "Dream",
        10.5,
        "Bengaluru (On-site)",
        "2026 B.Tech EEE, ECE with Electric Powertrain interest",
        "Embedded C, Field Oriented Control (FOC), BLDC/PMSM Motors, TI C2000 DSP, CAN Protocol, BMS",
        "https://www.atherenergy.com/careers",
        "2026-11-20",
        "Motor Control Hardware/Firmware Design Test + Inverter Circuitry Round + Tech Interview",
        1
    ),
    (
        "Delta Electronics",
        "Power Electronics & Solar Inverter Systems Engineer",
        "Dream",
        8.0,
        "Bengaluru / Rudrapur (On-site)",
        "2026 B.Tech EEE, ECE with Power Electronics coursework",
        "Power Converter Topologies, MATLAB/Simulink, PCB Layout, Grid-Tie Inverters, Thermal Management",
        "https://www.deltaelectronicsindia.com/careers",
        "2026-11-15",
        "Technical Aptitude Test + Circuit Simulation & Power Electronics Interview",
        1
    ),
    (
        "Tech Mahindra",
        "Enterprise AI & Cloud DevOps Associate",
        "Standard",
        5.5,
        "Hyderabad / Pune (Hybrid)",
        "2026 B.Tech all branches with 60%+ throughout academics",
        "Python, SQL, AWS Fundamentals, Docker, CI/CD Pipelines, Machine Learning Basics",
        "https://careers.techmahindra.com/",
        "2026-10-22",
        "Tech Mahindra National Qualifier (Aptitude + Psychometric + Technical Coding)",
        1
    ),
    (
        "HCLTech",
        "Junior Full Stack & Cloud Developer",
        "Standard",
        5.0,
        "Visakhapatnam / Chennai (On-site)",
        "2026 B.Tech all branches with min 60% in 10th, 12th & Degree",
        "Core Java, HTML5/CSS3, JavaScript, Spring Boot, MySQL, Git",
        "https://www.hcltech.com/careers",
        "2026-10-20",
        "Online Cognitive & Coding Assessment + Technical & HR Video Interview",
        1
    ),
    (
        "Capgemini",
        "Data Analytics & Python Software Engineer",
        "Standard",
        5.2,
        "Hyderabad / Bengaluru (Hybrid)",
        "2026 B.Tech all branches with 60%+ aggregate",
        "Python, Pandas, NumPy, SQL, Data Visualization (PowerBI/Tableau), REST APIs",
        "https://www.capgemini.com/in-en/careers/",
        "2026-10-19",
        "Capgemini Excellence Assessment (Game-based Aptitude + Pseudo Code + Coding)",
        1
    )
]

NEW_FLASHCARDS = [
    # Track 1: FSD
    (
        "FSD",
        "Explain Database Normalization (1NF, 2NF, 3NF, BCNF) and when to denormalize.",
        "Normalization organizes relational tables to eliminate redundancy and prevent insert/update/delete anomalies. 1NF requires atomic values and unique records. 2NF removes partial dependency on composite keys. 3NF removes transitive dependencies (non-key attributes depending on non-key attributes). BCNF is an advanced 3NF where every determinant is a candidate key. In modern high-throughput web apps, intentional denormalization is used in read-heavy reporting or document stores (like caching product ratings directly on order items) to avoid expensive multi-table joins at scale.",
        "Database Architecture & SQL",
        "Standard",
        1
    ),
    (
        "FSD",
        "What is Eventual Consistency vs Strong Consistency in distributed microservices (CAP Theorem)?",
        "According to the CAP theorem, a distributed system can only guarantee two out of Consistency, Availability, and Partition Tolerance during a network partition. Strong Consistency guarantees that every read immediately receives the most recent write (typical in banking relational databases with 2-Phase Commit). Eventual Consistency guarantees that, given no new updates, all replicas will eventually converge to the same value (typical in NoSQL, DynamoDB, and asynchronous event-driven microservices using Kafka or RabbitMQ to maximize availability and low latency).",
        "Distributed Systems & Microservices",
        "Standard",
        1
    ),
    (
        "FSD",
        "How does the React 18 Concurrent Renderer and Fiber Architecture work?",
        "React Fiber is a complete rewrite of React's core reconciliation engine. It represents each component as a unit of work (Fiber node) in a virtual call stack linked list. Unlike the legacy synchronous stack reconciler that could block the browser thread during large DOM trees, Fiber allows React to pause, prioritize, reuse, or abort rendering work. Features like useTransition and Suspense leverage this to keep typing and button clicks responsive (high priority) while background component trees render asynchronously (low priority).",
        "Frontend Engineering & Frameworks",
        "Standard",
        1
    ),

    # Track 2: AIML
    (
        "AIML",
        "How do Self-Attention and Multi-Head Attention mechanisms work in Transformers?",
        "Self-attention allows a neural network to weigh the contextual importance of every token in a sequence relative to every other token. For each token, the model calculates Query (Q), Key (K), and Value (V) vectors. The attention weights are computed using Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k)) * V. Multi-Head Attention splits Q, K, and V across multiple parallel projection subspaces, enabling the model to jointly attend to information from different representation aspects (e.g., syntactic structure in one head, coreference resolution in another).",
        "Deep Learning & NLP",
        "Standard",
        2
    ),
    (
        "AIML",
        "Explain the differences between RAG (Retrieval-Augmented Generation) and Fine-Tuning (LoRA).",
        "RAG connects an LLM to external real-time data or internal enterprise knowledge bases using vector embeddings and similarity search (e.g., Chroma, FAISS). It injects retrieved source context directly into the prompt at runtime, preventing hallucinations and keeping facts updated without retraining. Fine-Tuning (e.g., LoRA - Low-Rank Adaptation) freezes base model weights and trains small low-rank adapter matrices to alter the model's tone, syntax, style, or specific task behavior (like medical diagnosis or code formatting). RAG provides knowledge, while fine-tuning teaches skills and stylistic structure.",
        "Generative AI & LLMs",
        "Standard",
        2
    ),
    (
        "AIML",
        "What is Data Leakage in Machine Learning pipelines and how do you prevent it?",
        "Data leakage occurs when information from outside the training dataset (specifically from the test or target dataset) contaminates the training process, causing overly optimistic validation accuracy that fails completely in production. Common sources include calculating MinMax/Standard scalers or imputation statistics on the entire dataset before train-test split, or using future time-series features to predict current events. It is prevented by using scikit-learn Pipelines to fit transformers exclusively on training folds during cross-validation.",
        "MLOps & Data Science",
        "Standard",
        2
    ),

    # Track 3: DEVOPS
    (
        "DEVOPS",
        "What is GitOps and how does ArgoCD enforce continuous delivery on Kubernetes?",
        "GitOps is an operational framework where Git repositories serve as the single source of truth for infrastructure and application configurations. ArgoCD is a declarative Kubernetes controller that continuously compares the desired state stored in Git (manifests, Helm charts, or Kustomize) with the actual live state running inside the Kubernetes cluster. If discrepancies occur (drift), ArgoCD can automatically sync or alert developers, providing audit logs, easy rollbacks, and zero-touch deployments.",
        "Cloud Native & GitOps",
        "Standard",
        3
    ),
    (
        "DEVOPS",
        "Explain Prometheus metrics collection (Pull vs Push) and the role of Node Exporter.",
        "Prometheus is a time-series monitoring system that uses a pull-based architecture: it periodically scrapes HTTP metric endpoints exposed by services (in Prometheus exposition format) at configured intervals. Node Exporter is a lightweight daemon installed on Linux hosts that collects kernel-level OS metrics (CPU usage, RAM, disk I/O, network packets) and exposes them on port 9100 for Prometheus scraping. For ephemeral short-lived jobs (batch scripts) that terminate before scrape intervals, a Prometheus Pushgateway is used.",
        "Observability & SRE",
        "Standard",
        3
    ),

    # Track 4: CYBER
    (
        "CYBER",
        "Explain Cross-Site Scripting (XSS): Stored, Reflected, and DOM-based vulnerabilities.",
        "XSS occurs when malicious JavaScript executes in a victim's browser within the context of a trusted website. Stored XSS permanently saves malicious code in the database (e.g., comment boards), targeting all visitors viewing that record. Reflected XSS reflects the payload immediately from the HTTP request (e.g., search queries or error messages via phishing links). DOM-based XSS occurs entirely client-side when client scripts unsafely write user inputs into the DOM (e.g., document.write or innerHTML) without server involvement. Prevention requires strict input sanitization, contextual output encoding, CSP (Content Security Policy), and HttpOnly cookie flags.",
        "Web Application Security",
        "Standard",
        4
    ),
    (
        "CYBER",
        "What is Zero Trust Architecture and what are its core operational pillars?",
        "Zero Trust is a modern cybersecurity paradigm based on the principle 'Never Trust, Always Verify'. Unlike perimeter security ('castle and moat'), Zero Trust assumes attackers already exist inside the network. Its core pillars include: 1) Explicit verification of identity and device posture on every request, 2) Least Privilege Access (granting only just-in-time permissions), 3) Micro-segmentation of networks to contain lateral movement, and 4) Continuous real-time telemetry and behavioral threat monitoring.",
        "Enterprise Cyber Architecture",
        "Standard",
        4
    ),

    # Track 5: APP
    (
        "APP",
        "How do React Native TurboModules and the Fabric renderer improve mobile performance?",
        "In legacy React Native, the JavaScript thread communicated with native iOS/Android modules asynchronously over an asynchronous JSON serialization bridge, which caused frame drops and sluggish lists. In the new architecture: 1) TurboModules use JSI (JavaScript Interface) in C++ to allow JavaScript code to directly call native C++/Java/Objective-C methods synchronously without JSON serialization, and 2) Fabric manages the UI tree directly in C++, creating native platform views with shared memory for instant 60/120 FPS scrolling.",
        "Mobile Framework Architecture",
        "Standard",
        5
    ),
    (
        "APP",
        "Explain Mobile App Lifecycle states in Android and how background services are managed.",
        "In Android, Activities transition across states: onCreate() -> onStart() -> onResume() (interactive) -> onPause() -> onStop() (backgrounded) -> onDestroy(). Modern Android heavily restricts background execution to save battery. Apps cannot run indefinite background services; instead, developers use WorkManager for deferrable, guaranteed background tasks (e.g., data sync, photo uploads with constraints like Wi-Fi and charging), Foreground Services with a persistent notification (e.g., media playback, turn-by-turn navigation), and FCM for push notifications.",
        "Android OS & Architecture",
        "Standard",
        5
    ),

    # Track 11: EMBEDDED
    (
        "EMBEDDED",
        "Why must variables shared between an ISR and the main loop be declared as 'volatile' in C?",
        "The 'volatile' qualifier instructs the C/C++ compiler that the variable's value can be changed at any moment by hardware or an external interrupt without the compiler's knowledge. Without 'volatile', aggressive compiler optimizations (like -O2 or -O3) might cache the variable in a CPU register instead of reading from RAM, causing the main loop to read stale values or infinite-loop on a flag that was updated inside the ISR. Furthermore, accesses to multi-byte volatile variables must be protected atomically to prevent race conditions.",
        "Embedded C & Microcontrollers",
        "Standard",
        11
    ),
    (
        "EMBEDDED",
        "Explain Direct Memory Access (DMA) and why it is critical for high-throughput peripherals.",
        "DMA is a specialized hardware controller that transfers data directly between memory and peripherals (e.g., ADC, SPI, UART, Ethernet) without involving the CPU for every single byte. In a standard interrupt-driven transfer, the CPU must context-switch on every byte received, consuming significant clock cycles. With DMA, the CPU configures the source address, destination address, and transfer size once; the DMA hardware handles the transfer autonomously in the background and raises a single interrupt only when the entire block or circular buffer is filled.",
        "Microcontroller Hardware Architecture",
        "Standard",
        11
    ),
    (
        "EMBEDDED",
        "What is Priority Inversion in RTOS and how does Priority Inheritance prevent it?",
        "Priority Inversion occurs when a high-priority task (H) is blocked waiting for a shared mutex held by a low-priority task (L), while an intermediate-priority task (M) preempts L because M has higher priority than L. Consequently, M delays H, inverting their real priorities (which famously nearly caused the Mars Pathfinder rover to reboot endlessly). Priority Inheritance solves this by temporarily boosting the priority of L to match H's priority while L holds the mutex, ensuring L finishes quickly and releases the mutex before M can preempt.",
        "Real-Time Operating Systems (RTOS)",
        "Standard",
        11
    ),

    # Track 12: VLSI
    (
        "VLSI",
        "What is the difference between Synchronous and Asynchronous resets in sequential circuit design?",
        "A synchronous reset only affects the flip-flop's state on the active clock edge (posedge/negedge clock), ensuring clean, predictable synchronous transitions free from glitching, but requiring the clock to be running. An asynchronous reset resets the flip-flop immediately regardless of the clock signal, which is critical for power-on startup when the clock tree might not yet be stabilized. However, releasing an asynchronous reset must be synchronized to the clock domain using reset synchronizers to prevent reset recovery and removal timing violations.",
        "Digital IC Design & Verilog",
        "Standard",
        12
    ),
    (
        "VLSI",
        "Explain Mealy vs Moore State Machines and their trade-offs in digital logic.",
        "In a Moore machine, the outputs depend solely on the current state; outputs change synchronously with clock transitions and are inherently glitch-free. In a Mealy machine, the outputs depend on both the current state AND the current external inputs; this often requires fewer states to implement the same logic and responds one clock cycle faster to input changes. However, Mealy outputs can produce combinatorial glitches if inputs transition asynchronously, requiring careful output register buffering.",
        "FSM & Sequential Logic",
        "Standard",
        12
    ),
    (
        "VLSI",
        "What are False Paths and Multi-Cycle Paths in Static Timing Analysis (STA)?",
        "In STA, the timing engine checks every path between flip-flops against setup and hold constraints. A False Path is a logical path that physically exists in the netlist but can never be sensitized or exercised during actual chip operation (e.g., test mode logic or static configuration registers). A Multi-Cycle Path is a design path intentionally architected to take more than one clock cycle for data to propagate (e.g., an ALU complex division operation). Design engineers write SDC timing exceptions so tools don't waste silicon area trying to meet impossible 1-cycle timing constraints.",
        "Static Timing Analysis (STA)",
        "Standard",
        12
    ),

    # Track 13: EV_SMARTGRID
    (
        "EV_SMARTGRID",
        "Explain the core functional architecture of an EV Battery Management System (BMS).",
        "A BMS is the brain and safety guardian of an EV lithium-ion battery pack. Its core modules include: 1) Analog Front End (AFE) ICs for high-accuracy per-cell voltage, current, and temperature monitoring; 2) Algorithms for State of Charge (SoC) estimation and State of Health (SoH); 3) Cell Balancing circuitry (passive bleed resistors or active inductor/capacitor charge shuttles) to equalize cell voltages; 4) Protection switches (Contactor relays, Pyro-fuses) against overvoltage, undervoltage, overcurrent, and thermal runaway; and 5) CAN bus communication with the Vehicle Control Unit (VCU) and charger.",
        "EV Battery Systems",
        "Standard",
        13
    ),
    (
        "EV_SMARTGRID",
        "How does Regenerative Braking work in Electric Vehicles with 3-Phase Inverters?",
        "During acceleration, the high-voltage battery discharges DC power into a 3-phase inverter, which synthesizes AC sinusoidal currents using Space Vector PWM to drive a Permanent Magnet Synchronous Motor (PMSM) or BLDC. During braking or coasting, the vehicle's momentum spins the motor rotor, turning the motor into an AC generator. The inverter switches operate as a boost rectifier: diodes and controlled MOSFET/IGBT switching step up the induced AC back-EMF into DC voltage higher than the battery pack, feeding kinetic energy back into the cells and slowing the vehicle down.",
        "Electric Powertrain & Power Electronics",
        "Standard",
        13
    ),
    (
        "EV_SMARTGRID",
        "What is the IEC 61850 standard and why is it essential for Digital Smart Substation automation?",
        "IEC 61850 is the international communication standard for electrical substation automation. It replaces bulky copper hardwiring between transformers, circuit breakers, and protection relays with high-speed Ethernet communication over fiber optic LANs. It defines standard protocols including GOOSE (Generic Object Oriented Substation Events) for millisecond-level peer-to-peer trip signals, Sampled Values (SV) for digitized voltage/current waveforms from optical transducers, and MMS for client-server SCADA supervision.",
        "Smart Grid Communications & SCADA",
        "Standard",
        13
    )
]

NEW_QUIZZES = [
    # Track 1: FSD (Track ID 1)
    (
        1,
        "React Virtual DOM Reconciliation",
        "How does React's diffing algorithm achieve O(n) complexity when comparing two Virtual DOM trees?",
        json.dumps([
            "By performing full tree recursion and edit distance calculations",
            "By assuming elements of different types generate different trees and using stable 'key' props for lists",
            "By directly reading the browser's hardware GPU layers",
            "By comparing MD5 hashes of raw HTML strings"
        ]),
        1,
        "React uses two heuristic assumptions: 1) Two elements of different types will produce different trees, so React tears down the old tree and mounts the new one; 2) Child lists are tracked using unique 'key' props to match existing nodes, achieving linear O(n) instead of general O(n^3) tree diffing.",
        10
    ),
    (
        1,
        "Web Application Authentication & Security",
        "Where is the most secure place to store a sensitive JWT access/refresh token in a browser to prevent XSS theft?",
        json.dumps([
            "In window.localStorage because it persists across tabs",
            "In window.sessionStorage because it clears when the tab is closed",
            "In an HttpOnly, Secure, SameSite=Strict HTTP cookie",
            "Inside the document.title attribute"
        ]),
        2,
        "Storing JWTs in localStorage or sessionStorage leaves them vulnerable to theft via Cross-Site Scripting (XSS). An HttpOnly cookie cannot be read or accessed by client-side JavaScript, while Secure and SameSite flags protect against man-in-the-middle and CSRF attacks.",
        10
    ),

    # Track 2: AIML (Track ID 2)
    (
        2,
        "Classification Evaluation Metrics",
        "In a fraud detection or cancer diagnosis system where the dataset is 99% negative (benign), which metric is LEAST reliable?",
        json.dumps([
            "Raw Classification Accuracy",
            "Precision",
            "Recall (Sensitivity)",
            "Area Under the Precision-Recall Curve (PR-AUC)"
        ]),
        0,
        "Raw accuracy is misleading for imbalanced datasets because a naive model that always predicts 'negative' achieves 99% accuracy while catching 0% of fraud or cancer cases. Recall, Precision, and PR-AUC are far more informative.",
        10
    ),
    (
        2,
        "Deep Learning Regularization",
        "What is the mathematical effect of Dropout during the training phase of a Deep Neural Network?",
        json.dumps([
            "It permanently removes weights with values less than zero",
            "It randomly deactivates a fraction 'p' of neurons per forward pass, preventing co-adaptation of features",
            "It multiplies the learning rate by a decay factor on each epoch",
            "It converts all activation functions to linear identities"
        ]),
        1,
        "Dropout acts as an ensemble technique within a single network: by randomly setting activations of a chosen subset of neurons to zero during training, it prevents neurons from relying excessively on neighboring units (co-adaptation), significantly reducing overfitting.",
        10
    ),
    (
        2,
        "Vector Search & Embeddings",
        "Which metric measures the directional similarity between two high-dimensional text embeddings regardless of vector magnitude?",
        json.dumps([
            "Cosine Similarity",
            "Manhattan Distance (L1 norm)",
            "Euclidean Distance (L2 norm)",
            "Hamming Distance"
        ]),
        0,
        "Cosine Similarity computes the cosine of the angle between two vectors: (A . B) / (||A|| * ||B||). Because it normalizes by vector length, it measures orientation and semantic meaning independently of text length.",
        10
    ),

    # Track 3: DEVOPS (Track ID 3)
    (
        3,
        "Kubernetes Workload Controllers",
        "Which Kubernetes workload controller is best suited for running stateful databases (e.g., PostgreSQL cluster) with persistent storage identities?",
        json.dumps([
            "Deployment",
            "StatefulSet",
            "DaemonSet",
            "Job"
        ]),
        1,
        "StatefulSets provide unique, persistent network identifiers (pod-0, pod-1) and stable, ordered storage volume bindings for each pod, which are essential for databases that require consistent master-replica topologies.",
        10
    ),
    (
        3,
        "Docker Multi-Stage Builds",
        "What is the primary benefit of using Docker Multi-Stage Builds in a CI/CD pipeline?",
        json.dumps([
            "It runs containers faster by disabling the Linux namespace isolation",
            "It drastically minimizes final production image sizes by separating build tools from runtime binaries",
            "It automatically encrypts the Docker daemon socket with TLS",
            "It converts container images into virtual machine OVA files"
        ]),
        1,
        "Multi-stage builds allow developers to use large SDKs and compilers (Node, Go, Maven) in early build stages, and then copy only the compiled binary or dist artifacts into a minimal runtime image (like Alpine or Distroless), reducing image size from 1GB+ down to <50MB.",
        10
    ),
    (
        3,
        "Infrastructure as Code & Drift",
        "What command does Terraform provide to inspect real-world cloud resource differences against the local state file without applying changes?",
        json.dumps([
            "terraform init",
            "terraform plan",
            "terraform destroy",
            "terraform fmt"
        ]),
        1,
        "'terraform plan' refreshes state against the cloud provider API and generates an execution plan showing exactly what will be created, modified, or destroyed to reconcile state drift before 'terraform apply' is run.",
        10
    ),

    # Track 4: CYBER (Track ID 4)
    (
        4,
        "Web Security Defenses",
        "What is the most effective defense against SQL Injection vulnerabilities in backend web applications?",
        json.dumps([
            "Client-side JavaScript input length validation",
            "Using Parameterized Queries (Prepared Statements) or an ORM",
            "Changing the database port from 3306 to a random port",
            "Encrypting the database connection string with Base64"
        ]),
        1,
        "Parameterized queries (Prepared Statements) ensure that user-supplied input is treated purely as data, never as executable SQL code, completely neutralizing SQL injection regardless of special characters input.",
        10
    ),
    (
        4,
        "Public Key Cryptography & TLS",
        "During a TLS 1.3 handshake, which key exchange mechanism provides Perfect Forward Secrecy (PFS)?",
        json.dumps([
            "Static RSA Key Transport",
            "Ephemeral Diffie-Hellman (ECDHE)",
            "DES / 3DES Symmetric Cipher",
            "MD5 Hash Checksum Exchange"
        ]),
        1,
        "Ephemeral Diffie-Hellman (ECDHE) generates a temporary, unique session key pair for every individual TLS connection. Even if a server's private key is compromised in the future, past recorded encrypted communications cannot be decrypted.",
        10
    ),
    (
        4,
        "Enterprise Security Frameworks",
        "In the MITRE ATT&CK Matrix, what tactic describes an attacker moving from an initial compromised machine to other high-value servers inside an internal network?",
        json.dumps([
            "Initial Access",
            "Privilege Escalation",
            "Lateral Movement",
            "Exfiltration"
        ]),
        2,
        "Lateral Movement consists of techniques adversaries use to enter and control systems on a network after gaining initial foothold (e.g., using Pass-the-Hash, SMB/SSH pivoting, or stolen domain admin tokens).",
        10
    ),

    # Track 5: APP (Track ID 5)
    (
        5,
        "Flutter State Management",
        "In Flutter, why is calling setState() inside the build() method of a widget considered an anti-pattern?",
        json.dumps([
            "It causes an infinite build loop and crashes the Flutter engine",
            "It turns off the Skia/Impeller graphics rendering engine",
            "It converts the widget permanently into a StatelessWidget",
            "It bypasses hot reload completely"
        ]),
        0,
        "Calling setState() marks the widget as dirty and triggers another build(). If called during build(), it creates an infinite recursive loop that throws a 'setState() or markNeedsBuild() called during build' exception.",
        10
    ),
    (
        5,
        "Mobile App Deep Linking",
        "What Android mechanism allows an app to register HTTP URLs so the OS opens the native app directly instead of the web browser?",
        json.dumps([
            "ContentProvider URI permissions",
            "Android App Links with verified assetlinks.json and Intent Filters",
            "BroadcastReceivers with priority 999",
            "AIDL Remote Services"
        ]),
        1,
        "Android App Links use intent filters with the autoVerify='true' attribute inside AndroidManifest.xml and verify domain ownership via a digital assetlinks.json file hosted on the company domain's .well-known path.",
        10
    ),
    (
        5,
        "Mobile Battery & Power Optimization",
        "Which sensor configuration strategy is best for preserving battery life in a background location tracking mobile app?",
        json.dumps([
            "Polling GPS every 100 milliseconds at Highest Accuracy continuously",
            "Using Geofencing and Fused Location Provider with balanced power intervals and motion activity recognition",
            "Keeping the screen wake-lock permanently active in the background",
            "Reading Wi-Fi scan results in an infinite while loop"
        ]),
        1,
        "Continuous raw GPS polling rapidly drains phone batteries within hours. Fused Location Provider combines Wi-Fi, cell towers, and accelerometer activity detection to poll GPS only when the user is actively in motion.",
        10
    ),

    # Track 11: EMBEDDED (Track ID 11)
    (
        11,
        "Serial Peripheral Protocols",
        "Which communication protocol operates in full-duplex using 4 wires (MOSI, MISO, SCK, CS) with transfer speeds typically exceeding 10 Mbps?",
        json.dumps([
            "I2C (Inter-Integrated Circuit)",
            "SPI (Serial Peripheral Interface)",
            "UART (Universal Asynchronous Receiver-Transmitter)",
            "1-Wire Protocol"
        ]),
        1,
        "SPI is a synchronous, full-duplex master-slave bus using separate Master-Out-Slave-In (MOSI) and Master-In-Slave-Out (MISO) lines, allowing clock rates of 20-50+ MHz, far higher than standard I2C (100kHz-3.4MHz).",
        10
    ),
    (
        11,
        "Embedded System Reliability",
        "What is the purpose of a Watchdog Timer (WDT) in a mission-critical embedded microcontroller?",
        json.dumps([
            "To measure the execution time of floating-point math functions",
            "To reset the microcontroller automatically if the firmware hangs or enters an infinite deadlock",
            "To overclock the CPU crystal oscillator when heat rises",
            "To record the system's GPS timestamp into flash memory"
        ]),
        1,
        "A Watchdog Timer is a hardware countdown counter. The firmware must regularly 'kick' or 'refresh' the timer during normal execution. If the firmware freezes or enters an unexpected infinite loop, the timer underflows and triggers a hardware reset.",
        10
    ),
    (
        11,
        "Interrupt Service Routines (ISRs)",
        "Why is it hazardous to execute printf() or dynamic malloc() calls inside an Interrupt Service Routine (ISR)?",
        json.dumps([
            "printf and malloc are non-reentrant, blocking, and take unpredictable clock cycles, stalling critical CPU execution",
            "printf consumes 100% of GPU memory bandwidth",
            "malloc permanently disables the microcontroller's flash memory",
            "The compiler automatically deletes any printf calls inside an interrupt"
        ]),
        0,
        "ISRs must execute and return as quickly as possible. Functions like printf and malloc use shared mutexes and heap pointers that are non-reentrant; calling them from an ISR can corrupt memory or cause deadlocks if the main thread was interrupted during a memory allocation.",
        10
    ),

    # Track 12: VLSI (Track ID 12)
    (
        12,
        "Sequential Timing Constraints",
        "What timing violation occurs if input data to a flip-flop changes too close AFTER the active clock edge arrives?",
        json.dumps([
            "Setup Time Violation",
            "Hold Time Violation",
            "Clock Skew Drift Violation",
            "Ground Bounce Violation"
        ]),
        1,
        "Hold time is the minimum duration the data input must remain stable AFTER the active clock edge. If data changes before hold time expires, a hold violation occurs. Unlike setup violations (which can be fixed by lowering clock frequency), hold violations cannot be fixed by frequency changes.",
        10
    ),
    (
        12,
        "Clock Domain Crossing (CDC)",
        "What circuit technique is standardly used to safely synchronize a 1-bit asynchronous control signal across two asynchronous clock domains?",
        json.dumps([
            "A single pull-up resistor to VDD",
            "A 2-Flip-Flop (2-FF) Synchronizer",
            "A Schmitt Trigger buffer",
            "A 4-to-1 Multiplexer"
        ]),
        1,
        "When transferring an asynchronous signal, metastability can occur if input transitions violate setup/hold times. A 2-FF synchronizer allows the metastable state in the first flip-flop to settle to a stable 0 or 1 before the second flip-flop samples it on the destination clock.",
        10
    ),
    (
        12,
        "Verilog Hardware Description Language",
        "In Verilog RTL design, which assignment type should always be used inside clocked sequential 'always @(posedge clk)' blocks?",
        json.dumps([
            "Continuous assignment (assign =)",
            "Blocking assignment (=)",
            "Non-blocking assignment (<=)",
            "Force/Release assignment"
        ]),
        2,
        "Non-blocking assignments (<=) evaluate all right-hand expressions simultaneously at the clock edge before updating left-hand registers. This guarantees concurrent hardware register behavior and prevents simulation race conditions between flip-flops.",
        10
    ),

    # Track 13: EV_SMARTGRID (Track ID 13)
    (
        13,
        "EV Battery State of Charge (SoC)",
        "Why is simple Coulomb Counting insufficient for long-term Battery State of Charge (SoC) estimation in EVs?",
        json.dumps([
            "Coulomb counting requires high AC voltage inputs",
            "Sensor current measurement drift and integration errors accumulate over time without periodic recalibration",
            "Lithium iron phosphate batteries do not have electrical current",
            "It destroys the battery's active cathode material"
        ]),
        1,
        "Coulomb counting integrates current over time. Small sensor inaccuracies, thermal effects, and self-discharge cause drift to accumulate over weeks. Production BMS systems combine Coulomb counting with Extended Kalman Filtering (EKF) and open-circuit voltage lookups to correct drift.",
        10
    ),
    (
        13,
        "Power Electronics & Inverters",
        "What modulation technique is most widely adopted in modern EV motor controllers to synthesize smooth sinusoidal voltages from a DC battery?",
        json.dumps([
            "Space Vector Pulse Width Modulation (SVPWM)",
            "Simple Amplitude Modulation (AM)",
            "Phase Shift Keying (PSK)",
            "Binary Frequency Shift Modulation"
        ]),
        0,
        "SVPWM utilizes the eight switching states of a 3-phase inverter to approximate a circular rotating flux vector. It increases DC bus voltage utilization by up to 15.5% compared to sinusoidal PWM and minimizes harmonic distortion and torque ripple.",
        10
    ),
    (
        13,
        "Smart Grid Communications",
        "Which protocol under the IEC 61850 standard provides ultra-fast (< 4 millisecond) peer-to-peer multicast messaging between intelligent protection relays during a grid fault?",
        json.dumps([
            "Modbus RTU",
            "GOOSE (Generic Object Oriented Substation Events)",
            "SNMP v2",
            "HTTP REST over IPv4"
        ]),
        1,
        "GOOSE bypasses standard TCP/IP network protocol stacks and maps directly to the Ethernet data link layer (Layer 2) with 802.1Q priority tagging, allowing protection relays to transmit breaker trip commands in under 4ms to isolate faults.",
        10
    )
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Insert Placements
    inserted_placements = 0
    for p in NEW_PLACEMENTS:
        try:
            cursor.execute("""
                INSERT INTO placements (company, role, package_category, package_lpa, location, eligibility, required_skills, apply_url, deadline, selection_process, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company, role) DO UPDATE SET
                    package_category = excluded.package_category,
                    package_lpa = excluded.package_lpa,
                    location = excluded.location,
                    eligibility = excluded.eligibility,
                    required_skills = excluded.required_skills,
                    apply_url = excluded.apply_url,
                    deadline = excluded.deadline,
                    selection_process = excluded.selection_process,
                    is_active = excluded.is_active;
            """, p)
            inserted_placements += 1
        except Exception as e:
            print(f"Error inserting placement {p[0]}: {e}")

    # 2. Insert Flashcards
    inserted_flashcards = 0
    for f in NEW_FLASHCARDS:
        try:
            cursor.execute("""
                INSERT INTO interview_flashcards (track_code, question, answer, category, difficulty, track_id)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(track_code, question) DO UPDATE SET
                    answer = excluded.answer,
                    category = excluded.category,
                    difficulty = excluded.difficulty,
                    track_id = excluded.track_id;
            """, f)
            inserted_flashcards += 1
        except Exception as e:
            print(f"Error inserting flashcard {f[1]}: {e}")

    # 3. Insert Quizzes
    inserted_quizzes = 0
    for q in NEW_QUIZZES:
        try:
            cursor.execute("""
                INSERT INTO quizzes (track_id, title, question, options_json, correct_index, explanation, points)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(track_id, title) DO UPDATE SET
                    question = excluded.question,
                    options_json = excluded.options_json,
                    correct_index = excluded.correct_index,
                    explanation = excluded.explanation,
                    points = excluded.points;
            """, q)
            inserted_quizzes += 1
        except Exception as e:
            print(f"Error inserting quiz {q[1]}: {e}")

    conn.commit()

    total_placements = cursor.execute("SELECT COUNT(*) FROM placements").fetchone()[0]
    total_flashcards = cursor.execute("SELECT COUNT(*) FROM interview_flashcards").fetchone()[0]
    total_quizzes = cursor.execute("SELECT COUNT(*) FROM quizzes").fetchone()[0]
    conn.close()

    print(f"Successfully added/updated:")
    print(f"- Placements processed: {inserted_placements} | Total in DB: {total_placements}")
    print(f"- Flashcards processed: {inserted_flashcards} | Total in DB: {total_flashcards}")
    print(f"- Quizzes processed: {inserted_quizzes} | Total in DB: {total_quizzes}")

if __name__ == "__main__":
    main()
