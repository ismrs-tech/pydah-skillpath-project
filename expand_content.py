import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "pydah_skillpath.db")

def expand_content():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("SELECT id, code FROM career_tracks")
    track_map = {row[1]: row[0] for row in cursor.fetchall()}

    # 1. EXPAND INTERVIEW FLASHCARDS
    new_flashcards = [
        # FSD
        ("FSD", "What is the difference between REST and GraphQL APIs, and what trade-offs do they present?",
         "REST exposes fixed endpoint URLs returning rigid data structures, which often leads to over-fetching or under-fetching across multiple roundtrips. GraphQL exposes a single endpoint with a strongly-typed query language allowing clients to declare exactly which fields they require in a single payload. Trade-offs: GraphQL adds schema complexity, client-side caching difficulty, and query cost inspection overhead compared to HTTP caching and standard status codes in REST.",
         "Core", "API Architecture"),

        ("FSD", "Explain Database Normalization (1NF, 2NF, 3NF) versus Denormalization in scalable applications.",
         "Normalization structures relational schemas to eliminate redundancy and update anomalies: 1NF requires atomic values and unique records; 2NF removes partial key dependencies; 3NF eliminates transitive dependencies. Denormalization intentionally adds controlled redundancy (e.g. pre-calculated aggregates, cached tables) to eliminate expensive multi-table JOINs in high-throughput read-heavy applications.",
         "Medium", "Database Design"),

        ("FSD", "How does Browser CORS (Cross-Origin Resource Sharing) work, and what is a Preflight Request?",
         "CORS is a browser security mechanism enforcing Same-Origin Policy. When a client web app makes a request to a different domain, port, or protocol using non-simple HTTP methods (PUT, DELETE) or custom headers, the browser automatically dispatches an OPTIONS Preflight request. The server must respond with Access-Control-Allow-Origin, Access-Control-Allow-Methods, and Access-Control-Allow-Headers headers before the browser executes the actual request.",
         "Advanced", "Web Security & Protocols"),

        # AIML
        ("AIML", "Explain the Transformer Self-Attention mechanism and why Multi-Head Attention is advantageous.",
         "Self-attention allows tokens to dynamically attend to every other token in a sequence based on contextual relevance by computing Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V. Multi-Head Attention projects Queries, Keys, and Values into multiple lower-dimensional subspaces, allowing the model to jointly attend to information from different representation aspects simultaneously (e.g., grammatical syntax, pronouns, factual relations).",
         "Advanced", "Deep Learning & Transformers"),

        ("AIML", "How do you evaluate Machine Learning models when dealing with heavily imbalanced datasets?",
         "Accuracy is misleading in imbalanced sets (e.g. 99% accuracy by guessing negative in 1% fraud). Instead, utilize Precision (minimizing false positives), Recall (minimizing false negatives), F1-Score (harmonic mean), and PR-AUC (Precision-Recall Area Under Curve). Additionally, evaluate confusion matrices and consider resampling (SMOTE), class weighting in the loss function, or focal loss.",
         "Core", "Model Evaluation"),

        ("AIML", "What is the difference between Fine-Tuning (e.g. LoRA/PEFT) and Prompt Engineering in Large Language Models?",
         "Prompt Engineering (few-shot, chain-of-thought, system prompts) alters input instructions without modifying model weights, operating strictly at inference time. Fine-Tuning adapts the actual model parameters on domain-specific training data. Parameter-Efficient Fine-Tuning (LoRA) freezes the base model weights and trains small low-rank adapter matrices (reducing GPU memory by 80%+), enabling permanent domain specialization.",
         "Medium", "Generative AI & LLMs"),

        # DEVOPS
        ("DEVOPS", "Explain Blue-Green Deployment versus Canary Deployment strategies in production environments.",
         "Blue-Green deployment runs two identical production environments: Blue (active live version) and Green (new release). Traffic is switched instantly via the load balancer/router once Green passes health checks, offering instant zero-downtime rollback. Canary deployment rolls out the new release to a small percentage of real users (e.g. 5%), monitors error rates and latency, and gradually ramps to 100%.",
         "Core", "Release Strategies"),

        ("DEVOPS", "How does Docker Multi-Stage Builds optimize image size and security?",
         "Multi-Stage builds author multiple FROM instructions in a single Dockerfile. Heavy build dependencies (compilers, SDKs, dev headers) are isolated in early builder stages. Only the compiled binary or production artifacts are copied to the minimal final runtime image (e.g. Alpine/distroless), slashing final image size from 1GB+ down to tens of megabytes and eliminating vulnerability surfaces.",
         "Medium", "Container Optimization"),

        ("DEVOPS", "What is Infrastructure as Code (IaC), and how does Terraform manage state and drift detection?",
         "IaC manages cloud resources declaratively using human-readable configuration files (HCL) version-controlled in Git. Terraform tracks the true state of infrastructure in a 'terraform.tfstate' file. When 'terraform plan' runs, it compares the declared code, the state file, and the live cloud APIs to detect configuration drift and computes an exact execution plan to reconcile discrepancies.",
         "Advanced", "Cloud Infrastructure"),

        # CYBER
        ("CYBER", "What are the top web vulnerabilities according to OWASP Top 10, and how do you prevent SQL Injection?",
         "OWASP Top 10 includes Broken Access Control, Cryptographic Failures, Injection (SQLi, Command), Insecure Design, and Security Misconfiguration. SQL Injection occurs when untrusted user input alters SQL query logic. Prevention: parameterized queries (prepared statements), Object-Relational Mappers (ORMs), input validation, and enforcing database principle of least privilege.",
         "Core", "Application Security"),

        ("CYBER", "Explain the difference between Symmetric and Asymmetric Encryption (e.g., AES vs RSA/ECC).",
         "Symmetric encryption (AES-256, ChaCha20) utilizes the same secret key for both encryption and decryption; it is computationally fast and ideal for bulk data transfer. Asymmetric encryption (RSA, ECC/ECDSA) utilizes mathematically linked public-private keypairs; public key encrypts, private key decrypts. It solves the key-exchange problem and enables digital signatures, powering SSL/TLS handshakes.",
         "Core", "Cryptography"),

        ("CYBER", "What happens during a Man-in-the-Middle (MitM) attack, and how does TLS/SSL certificate pinning prevent it?",
         "In a MitM attack, an adversary positions themselves between client and server (via ARP spoofing, rogue Wi-Fi, or DNS poisoning) to intercept and tamper with traffic. In HTTPS, TLS certificates signed by trusted Certificate Authorities (CAs) validate the server's identity. SSL Pinning embeds the expected certificate or public key hash directly in the client application, thwarting interception even if an OS CA is compromised.",
         "Advanced", "Network Security"),

        # APP
        ("APP", "Explain the difference between the Widget Tree, Element Tree, and RenderObject Tree in Flutter.",
         "1. Widget Tree: Lightweight, immutable declarative blueprints created on every build. 2. Element Tree: Manages lifecycle, acts as the persistent bridge holding context and state, comparing old and new widgets. 3. RenderObject Tree: Handles actual layout calculation, sizing, constraints, hit-testing, and GPU painting commands on screen. This 3-tree separation ensures Flutter's high-speed 60/120 FPS UI performance.",
         "Advanced", "Flutter Architecture"),

        ("APP", "What is the lifecycle of a StatefulWidget in Flutter, and when should you call setState()?",
         "Lifecycle order: createState() -> initState() (setup controllers/listeners once) -> didChangeDependencies() -> build() -> didUpdateWidget() -> deactivate() -> dispose() (cleanup resources, cancel timers/streams). setState() notifies the framework that the internal state changed, scheduling a dirty build for the element so the UI re-renders with updated data.",
         "Core", "Mobile Lifecycle"),

        ("APP", "How do mobile applications handle offline-first caching and data synchronization with a remote backend?",
         "Offline-first architecture stores all read/write operations locally first (using SQLite / Drift / Hive) so the app functions seamlessly without network. When mutations occur offline, operations are queued in a persistent Sync Queue. Once connectivity is detected, an idempotent background sync pushes changes, resolves timestamp or vector-clock merge conflicts, and pulls delta updates from the server.",
         "Medium", "Mobile Offline Architecture"),

        # EMBEDDED
        ("EMBEDDED", "What is the purpose of the 'volatile' keyword in embedded C/C++, and where is it indispensable?",
         "The 'volatile' qualifier instructs the compiler that a variable's value can change unexpectedly at any moment outside the current code flow, preventing the compiler from optimizing away repeated memory reads into CPU registers. Indispensable uses: 1) Memory-mapped hardware I/O peripheral registers. 2) Global flags shared between an Interrupt Service Routine (ISR) and the main loop. 3) Multi-threaded RTOS shared variables without mutexes.",
         "Core", "Embedded C & Hardware"),

        ("EMBEDDED", "Explain the difference between Polling, Interrupt-Driven I/O, and Direct Memory Access (DMA).",
         "1. Polling: The CPU continually loops checking peripheral status flags, wasting CPU cycles and energy. 2. Interrupt-Driven: The peripheral asserts an electrical interrupt pin when data arrives, causing the CPU to context-switch to the ISR—efficient for sporadic data. 3. DMA: A dedicated hardware controller transfers data blocks directly between memory and peripherals with zero CPU intervention, freeing the CPU completely for computations.",
         "Medium", "Hardware Data Transfer"),

        ("EMBEDDED", "What is a Hardware Watchdog Timer (WDT), and how do you prevent nuisance resets in multi-threaded RTOS?",
         "A Watchdog Timer is an autonomous countdown hardware timer that automatically reboots the system if software hangs or crashes and fails to 'kick' (refresh) it before timeout. In a multi-tasking RTOS, kicking from a single task is dangerous if other critical tasks deadlock. The best practice is an RTOS Watchdog Supervisor: every thread must report a heartbeat bit to the supervisor task before the supervisor executes the hardware kick.",
         "Advanced", "Fault Tolerance & Safety"),

        # VLSI
        ("VLSI", "What is Metastability in digital systems, and how do Multi-Stage Synchronizers mitigate it?",
         "Metastability occurs when input data changes inside the Setup/Hold time aperture of a clocked flip-flop, causing the output voltage to oscillate between logic 0 and 1 for an indeterminate time. A Multi-Stage Synchronizer places two or more flip-flops in series on the destination clock. If the first stage enters metastability, the extra clock cycle provides exponential settling time for the signal to resolve before propagating.",
         "Core", "Digital Circuit Design"),

        ("VLSI", "Explain Clock Domain Crossing (CDC) and how an Asynchronous FIFO safely transfers data across different clocks.",
         "When signals pass between modules running on unsynchronized or different frequency clocks, race conditions and metastability arise. For multi-bit buses, simple flip-flop synchronizers fail due to bus skew. An Asynchronous FIFO uses dual-port RAM with independent write and read clock ports. Read and write pointers are encoded into Gray code (where only 1 bit transitions at a time) before being synchronized across clock domains.",
         "Advanced", "Clock Domain Crossing"),

        ("VLSI", "What are the core differences between Mealy and Moore Finite State Machines (FSMs)?",
         "In a Moore machine, outputs depend solely on the current state. Consequently, Moore outputs change only on the clock edge, are cleaner, and have no direct combinational path from inputs to outputs. In a Mealy machine, outputs depend on both the current state and the current inputs, which allows Mealy FSMs to often require fewer states and react one clock cycle faster, but input glitches can propagate directly to outputs.",
         "Core", "FSM Architecture"),

        # EV_SMARTGRID
        ("EV_SMARTGRID", "Explain Field Oriented Control (FOC) versus Scalar (V/f) Control for Electric Vehicle BLDC/PMSM motors.",
         "Scalar (V/f) control adjusts stator voltage and frequency proportionally, but cannot decouple magnetic flux from torque, resulting in sluggish response and poor low-speed torque. Field Oriented Control (FOC) uses Clarke and Park transformations to convert 3-phase AC stator currents into two orthogonal DC components: direct axis (d-axis, controlling flux) and quadrature axis (q-axis, controlling torque). This yields maximum torque per ampere, high efficiency, and precise dynamic acceleration.",
         "Advanced", "Electric Drives & Powertrains"),

        ("EV_SMARTGRID", "How does Regenerative Braking operate in an electric vehicle powertrain, and how is battery charging managed?",
         "During deceleration or braking, the electric traction motor transitions from motoring mode to generator mode, using vehicle kinetic energy to induce alternating current in the stator windings. The bi-directional inverter switches act as a boost rectifier, converting generated AC to DC voltage higher than the battery pack voltage. The BMS monitors cell temperature, maximum charging current limits, and State of Charge (SoC) to taper or disable regen when the battery is near 100% full.",
         "Medium", "EV Energy Management"),

        ("EV_SMARTGRID", "What is Islanding in a Smart Grid renewable power system, and why is Anti-Islanding protection mandatory?",
         "Islanding occurs when a distributed generator (e.g. grid-tied solar PV inverter) continues powering a localized section of the utility grid after the main utility power has tripped or disconnected. Unintentional islanding creates lethal electrical shock hazards for utility linemen performing repairs, and causes out-of-phase re-closing that damages consumer equipment. Anti-Islanding (via frequency shift, ROCOF, and voltage window protection) is legally mandated to trip inverters within 2 seconds.",
         "Core", "Smart Grid Protection")
    ]

    for fc in new_flashcards:
        cursor.execute("""
            INSERT INTO interview_flashcards (track_code, question, answer, difficulty, key_concept)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(track_code, question) DO UPDATE SET
                answer=excluded.answer,
                difficulty=excluded.difficulty,
                key_concept=excluded.key_concept
        """, fc)

    # 2. EXPAND QUIZZES ACROSS ALL TRACKS
    new_quizzes = [
        # FSD
        (track_map["FSD"], "REST API Idempotency",
         "Which of the following standard HTTP methods is NOT guaranteed to be idempotent according to HTTP specifications?",
         '["GET", "PUT", "POST", "DELETE"]', 2,
         "POST is non-idempotent because executing it multiple times produces multiple distinct resources (e.g. creating duplicate orders). GET, PUT, and DELETE are idempotent.", 25),

        (track_map["FSD"], "Relational ACID Transactions",
         "In database transactions, which ACID property ensures that partially executed transactions are rolled back completely upon system crash?",
         '["Atomicity", "Consistency", "Isolation", "Durability"]', 0,
         "Atomicity guarantees 'all-or-nothing' execution; if any step fails or crashes, all changes are rolled back to the pre-transaction state.", 25),

        (track_map["FSD"], "CSS Flexbox Cross-Axis Alignment",
         "In CSS Flexbox, which property aligns flex items along the cross-axis (perpendicular to flex-direction)?",
         '["justify-content", "align-items", "flex-wrap", "gap"]', 1,
         "align-items aligns items along the cross-axis, whereas justify-content aligns items along the main-axis.", 25),

        # AIML
        (track_map["AIML"], "Gradient Descent Learning Rate",
         "What typically occurs during neural network training if the learning rate is set excessively high?",
         '["The model converges immediately to global minimum", "The loss oscillates wildly or diverges to NaN/infinity", "The gradient vanishes to zero", "The model underfits due to lack of parameters"]', 1,
         "An excessively high learning rate causes parameter updates to overshoot the minima, resulting in oscillating or diverging training loss.", 25),

        (track_map["AIML"], "Overfitting Mitigation",
         "Which technique actively reduces model variance and overfitting by randomly deactivating a subset of neurons during forward pass?",
         '["Dropout", "Batch Normalization", "ReLU Activation", "Gradient Clipping"]', 0,
         "Dropout randomly zeroes out neuron activations with probability p during training, forcing redundant representations and mitigating co-adaptation.", 25),

        (track_map["AIML"], "Vector Similarity Metrics",
         "Why is Cosine Similarity frequently preferred over Euclidean Distance for semantic document embeddings?",
         '["Cosine similarity executes in O(1) time", "Cosine similarity measures vector direction/angle regardless of text length or magnitude", "Euclidean distance cannot handle negative numbers", "Cosine similarity does not require multiplication"]', 1,
         "Cosine similarity measures the orientation between vectors, making it insensitive to absolute document length or magnitude differences.", 25),

        # DEVOPS
        (track_map["DEVOPS"], "Kubernetes Health Probes",
         "Which Kubernetes probe is used to determine when a container has finished initializing and can safely begin receiving ingress network traffic?",
         '["Liveness Probe", "Readiness Probe", "Startup Probe", "Security Probe"]', 1,
         "Readiness probe indicates whether the container is ready to accept traffic. If it fails, Kubernetes stops routing Service traffic to that Pod.", 25),

        (track_map["DEVOPS"], "Linux File Permissions",
         "In Linux POSIX permissions, what does the numerical octal mode '755' represent on a script or directory?",
         '["Read, write, execute for Owner; read and execute for Group and Others", "Read and write for Everyone", "Full access for Group only", "Read-only for Owner"]', 0,
         "7 (rwx = 4+2+1) for owner; 5 (r-x = 4+1) for group; 5 (r-x = 4+1) for others.", 25),

        (track_map["DEVOPS"], "Terraform Declarative IaC",
         "What is the primary function of the 'terraform apply' command?",
         '["Formats HCL syntax", "Scans code for syntax errors", "Executes changes required to reach the desired state declared in the configuration", "Destroys all cloud resources immediately"]', 2,
         "terraform apply builds or modifies real cloud infrastructure to reconcile the desired configuration with live state.", 25),

        # CYBER
        (track_map["CYBER"], "TLS 1.3 Handshake Security",
         "How does TLS 1.3 improve security and latency over TLS 1.2 during session establishment?",
         '["It eliminates encryption entirely", "It reduces the handshake from 2 roundtrips to 1-RTT and eliminates legacy insecure ciphers", "It uses plain MD5 checksums", "It only works on port 80"]', 1,
         "TLS 1.3 mandates Forward Secrecy, removes insecure ciphers (RC4, DES, CBC), and finishes handshake in a single round-trip (1-RTT).", 25),

        (track_map["CYBER"], "Cross-Site Scripting (XSS)",
         "Which type of XSS attack occurs when malicious payload is permanently stored inside a web database and served to unsuspecting users?",
         '["Reflected XSS", "Stored (Persistent) XSS", "DOM-based XSS", "Blind SSRF"]', 1,
         "Stored XSS permanently stores malicious JavaScript in the target database (e.g. forum comments) that executes in victims' browsers.", 25),

        (track_map["CYBER"], "Network Scanning Protocols",
         "In Nmap, what is an SYN Stealth Scan (-sS) and why is it preferred by security auditors?",
         '["It completes the full TCP 3-way handshake", "It sends SYN and terminates with RST upon receiving SYN-ACK, never completing the full connection", "It disables target firewalls", "It uses ICMP ping only"]', 1,
         "A SYN scan never completes the TCP handshake, making it faster and less likely to be logged by basic application-level monitoring.", 25),

        # APP
        (track_map["APP"], "Flutter Widget Immutability",
         "Why are Flutter Widget classes marked with @immutable and their fields declared as 'final'?",
         '["Because Flutter cannot compile mutable classes", "Widgets are temporary blueprints rebuilt rapidly, while persistent state lives in Element and State objects", "It prevents garbage collection", "It is required for iOS release only"]', 1,
         "Widgets are disposable descriptions; Flutter creates and destroys thousands of them per second, keeping long-lived state in separate Element/State instances.", 25),

        (track_map["APP"], "Dart Asynchronous Streams",
         "In Dart, what is the primary difference between a Future and a Stream?",
         '["A Future returns multiple events over time, while a Stream returns one", "A Future yields a single asynchronous value or error, while a Stream delivers a sequence of asynchronous events over time", "Futures run on GPU, Streams run on CPU", "They are identical in functionality"]', 1,
         "A Future delivers one single eventual result; a Stream is a continuous pipe emitting zero or more asynchronous values over time.", 25),

        # EMBEDDED
        (track_map["EMBEDDED"], "C Volatile Qualifier",
         "Why must global flags modified inside an Interrupt Service Routine (ISR) be declared as 'volatile' in embedded C?",
         '["To allocate them in EEPROM memory", "To prevent compiler optimization from assuming the variable never changes in the main loop", "To encrypt the variable value", "To speed up floating point division"]', 1,
         "Without volatile, the compiler's optimizer assumes no other code changes the flag in the loop and caches it in a register, causing infinite loops.", 25),

        (track_map["EMBEDDED"], "Direct Memory Access (DMA)",
         "What is the greatest architectural advantage of using DMA for high-speed ADC sampling in microcontrollers?",
         '["It quadruples CPU clock speed", "It streams analog sample buffers into RAM with zero CPU intervention, freeing 100% of CPU cycles", "It eliminates the need for power supplies", "It converts code to assembly"]', 1,
         "DMA moves data directly between peripherals and SRAM via the system bus matrix, preventing CPU bottlenecking.", 25),

        # VLSI
        (track_map["VLSI"], "Setup Time Slack Calculation",
         "In Static Timing Analysis (STA), what does positive Setup Slack (+0.8ns) indicate about a digital timing path?",
         '["The path has failed and violates timing", "Data arrives safely 0.8ns before the required clock edge and meets timing criteria", "Clock jitter is greater than 1GHz", "The flip-flop has entered metastability"]', 1,
         "Positive slack means data arrives before the required setup threshold, confirming the circuit will operate reliably at the target frequency.", 25),

        (track_map["VLSI"], "FPGA Look-Up Tables",
         "In modern FPGAs, what basic hardware building block physically implements arbitrary combinational boolean logic functions?",
         '["Look-Up Table (LUT) with SRAM configuration cells", "Hard-wired NAND gate arrays", "Analog operational amplifiers", "Bipolar junction transistors"]', 0,
         "LUTs are small truth-table RAMs (typically 4 to 6 inputs) that emulate any truth table by storing pre-computed outputs.", 25),

        # EV_SMARTGRID
        (track_map["EV_SMARTGRID"], "Lithium-Ion Thermal Runaway",
         "What critical failure mechanism occurs when an EV Li-Ion cell is pierced or overcharged, triggering uncontrollable exothermic heat release?",
         '["Electrochemical passivation", "Thermal Runaway", "Hydrogen embrittlement", "Magnetic saturation"]', 1,
         "Thermal runaway is a self-sustaining positive feedback loop where internal shorting generates extreme heat and decomposition gases.", 25),

        (track_map["EV_SMARTGRID"], "Smart Grid Modbus Protocol",
         "In industrial SCADA and PLC communication, what is the maximum standard transmission speed of Modbus RTU over RS-485 serial links?",
         '["10 Gbps", "115,200 baud (typically 9600 to 115200 bps)", "100 MHz", "1.5 Mbps"]', 1,
         "Modbus RTU serial links run over balanced twisted-pair RS-485 differential lines up to 115,200 baud over long industrial distances.", 25)
    ]

    for q in new_quizzes:
        cursor.execute("""
            INSERT INTO quizzes (track_id, title, question, options_json, correct_index, explanation, points)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(track_id, title) DO UPDATE SET
                question=excluded.question,
                options_json=excluded.options_json,
                correct_index=excluded.correct_index,
                explanation=excluded.explanation,
                points=excluded.points
        """, q)

    # 3. EXPAND PLACEMENT OPPORTUNITIES ACROSS ALL DISCIPLINES
    new_placements = [
        ("Google India", "Cloud Solutions Engineer", "DEVOPS", "₹ 24.0 - 28.0 LPA", "Super Dream", "Bengaluru / Hyderabad", 
         "Linux, Kubernetes, GCP/Cloud Infra, Python/Go, Networking (TCP/IP), Distributed Systems", "10 Dec 2026", "B.Tech CSE/IT with 7.5+ CGPA and cloud certifications", "https://careers.google.com"),

        ("Microsoft India", "Software Development Engineer - Cloud & Systems", "FSD", "₹ 20.0 - 25.0 LPA", "Super Dream", "Hyderabad / Bengaluru",
         "C#/.NET or Python, React, Microservices, Azure, Relational DB, Distributed Systems", "14 Dec 2026", "B.Tech 2026/2027 Cohort with strong DSA and verified capstone", "https://careers.microsoft.com"),

        ("NVIDIA India", "AI Systems & Deep Learning Engineer", "AIML", "₹ 18.0 - 24.0 LPA", "Super Dream", "Bengaluru / Pune",
         "PyTorch, CUDA, TensorRT, Python, CNNs/Transformers, Model Quantization & Acceleration", "18 Dec 2026", "AI & Data Science / CSE with deep learning research or verified projects", "https://nvidia.com/careers"),

        ("AMD India", "Silicon Design & FPGA Validation Engineer", "VLSI", "₹ 17.5 - 22.0 LPA", "Super Dream", "Hyderabad",
         "Verilog HDL, SystemVerilog, FPGA Synthesis, Xilinx Vivado, Static Timing Analysis (STA)", "22 Dec 2026", "ECE / EEE graduates with 70%+ aggregate and digital design portfolio", "https://amd.com/careers"),

        ("Synopsys India", "ASIC Physical Design & Verification Engineer", "VLSI", "₹ 16.5 - 20.0 LPA", "Super Dream", "Bengaluru",
         "ASIC Flow, UVM, SystemVerilog, Timing Closure, DRC/LVS, Linux Shell Scripting", "28 Dec 2026", "ECE with coursework in VLSI circuits and digital synthesis", "https://synopsys.com/careers"),

        ("Palo Alto Networks", "Cyber Security Operations Analyst", "CYBER", "₹ 16.0 - 19.5 LPA", "Super Dream", "Bengaluru",
         "Threat Analysis, SIEM, Wireshark, OWASP Top 10, Network Defense, Python Scripting", "05 Jan 2027", "CSE / IT / ECE with certified cybersecurity labs or CTF rankings", "https://paloaltonetworks.com/careers"),

        ("CrowdStrike", "Penetration Tester & Vulnerability Analyst", "CYBER", "₹ 14.0 - 18.0 LPA", "Super Dream", "Pune / Remote",
         "Burp Suite, Metasploit, Reverse Engineering, Exploit Analysis, Linux Security", "08 Jan 2027", "All B.Tech streams with hands-on ethical hacking experience", "https://crowdstrike.com/careers"),

        ("PhonePe", "Mobile Application Systems Engineer", "APP", "₹ 15.0 - 19.0 LPA", "Super Dream", "Bengaluru",
         "Flutter, Dart, React Native, REST API sync, Offline Caching, Device Hardware APIs", "12 Jan 2027", "B.Tech with published Play Store or App Store client applications", "https://phonepe.com/careers"),

        ("Swiggy", "Mobile & Frontend Engineering Specialist", "APP", "₹ 12.0 - 15.5 LPA", "Super Dream", "Hyderabad / Bengaluru",
         "Dart/Flutter, Kotlin, React, State Management (Riverpod/Bloc), Performance Profiling", "15 Jan 2027", "Graduating cohort with demonstrated mobile app projects", "https://swiggy.com/careers"),

        ("Bosch Global Software", "Automotive Embedded & IoT Firmware Engineer", "EMBEDDED", "₹ 8.5 - 11.0 LPA", "Dream", "Bengaluru / Coimbatore",
         "Embedded C/C++, ARM Cortex-M, FreeRTOS, CAN Bus, AUTOSAR basics, SPI/I2C Protocols", "20 Jan 2027", "ECE / EEE / Mechanical with embedded systems capstone", "https://bosch.com/careers"),

        ("L&T Technology Services", "Embedded Firmware & RTOS Specialist", "EMBEDDED", "₹ 7.5 - 9.5 LPA", "Dream", "Mysuru / Chennai",
         "C/C++, Microcontrollers (STM32/ESP32), RTOS Task Scheduling, Hardware Debugging", "25 Jan 2027", "ECE / EEE graduates (60%+ in B.Tech)", "https://ltts.com/careers"),

        ("Tata Motors Electric Mobility", "EV Battery Pack & BMS Systems Engineer", "EV_SMARTGRID", "₹ 10.0 - 13.5 LPA", "Dream", "Pune",
         "Power Electronics, Battery Management Systems (BMS), MATLAB/Simulink, CAN bus, Thermal Control", "30 Jan 2027", "EEE / Mechanical / ECE with electric vehicle capstone", "https://tatamotors.com/careers"),

        ("Schneider Electric", "Smart Grid Automation & SCADA Specialist", "EV_SMARTGRID", "₹ 8.5 - 11.5 LPA", "Dream", "Hyderabad / Vadodara",
         "PLC Programming, SCADA Systems, Modbus/OPC-UA, Renewable Microgrids, Power Distribution", "05 Feb 2027", "EEE / ECE graduates with industrial automation lab experience", "https://se.com/careers"),

        ("Fractal Analytics", "AI & Machine Learning Specialist", "AIML", "₹ 9.0 - 12.0 LPA", "Dream", "Bengaluru / Mumbai",
         "Python, Pandas, Scikit-Learn, NLP, Vector DBs, RAG Architecture, SQL", "10 Feb 2027", "AI & DS / CSE with analytics and data science project portfolio", "https://fractal.ai/careers"),

        ("Accenture Advanced Technology", "Full Stack Application Developer", "FSD", "₹ 6.5 - 8.0 LPA", "Standard", "Hyderabad / Visakhapatnam",
         "HTML5, CSS3, JavaScript/TypeScript, Python/Java, SQL, Git, Agile Development", "15 Feb 2027", "Open to all Engineering branches with fundamental coding proficiency", "https://accenture.com/careers"),

        ("Wipro Turbo", "Cloud Infrastructure & DevOps Associate", "DEVOPS", "₹ 6.5 - 7.5 LPA", "Standard", "Hyderabad / Bengaluru",
         "Linux Administration, Shell Scripting, Docker Basics, CI/CD, Networking Fundamentals", "20 Feb 2027", "All B.Tech streams with 60%+ throughout academics", "https://wipro.com/careers")
    ]

    for p in new_placements:
        cursor.execute("""
            INSERT INTO placements (company, role, track_code, package_or_stipend, package_category, location, required_skills, deadline, eligibility, apply_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(company, role) DO UPDATE SET
                track_code=excluded.track_code,
                package_or_stipend=excluded.package_or_stipend,
                package_category=excluded.package_category,
                location=excluded.location,
                required_skills=excluded.required_skills,
                deadline=excluded.deadline,
                eligibility=excluded.eligibility
        """, p)

    conn.commit()
    conn.close()
    print("Content expansion successfully applied!")

if __name__ == "__main__":
    expand_content()
