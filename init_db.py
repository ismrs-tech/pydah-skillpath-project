import sqlite3
import os
import sys
import json
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "pydah_skillpath.db")

def init_database(reset=False, db_target=None):
    target_path = db_target or DB_PATH
    if reset and os.path.exists(target_path):
        try:
            os.remove(target_path)
            print("Removed previous database for clean rebuild.")
        except Exception as e:
            print(f"Notice during reset: {e}")

    conn = sqlite3.connect(target_path)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT CHECK(role IN ('student', 'admin')) NOT NULL DEFAULT 'student',
        department TEXT DEFAULT 'Computer Science & Engineering',
        year_or_designation TEXT DEFAULT '3rd Year B.Tech',
        target_role TEXT DEFAULT 'Full Stack Software Engineer',
        preferred_track_id INTEGER,
        avatar_seed TEXT DEFAULT 'pydah_student',
        karma_xp INTEGER DEFAULT 450,
        tagline TEXT DEFAULT 'Computer Science Student, Python Developer & Robotics Enthusiast',
        bio TEXT,
        github_url TEXT,
        linkedin_url TEXT,
        location TEXT DEFAULT 'Kakinada, Andhra Pradesh, India',
        phone TEXT,
        custom_skills TEXT,
        experience_json TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (preferred_track_id) REFERENCES career_tracks(id) ON DELETE SET NULL
    );
    """)

    # 2. Career Tracks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS career_tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        tagline TEXT NOT NULL,
        category TEXT NOT NULL,
        icon TEXT NOT NULL,
        badge_color TEXT NOT NULL,
        estimated_hours INTEGER DEFAULT 60,
        demand_level TEXT DEFAULT 'Very High',
        departments TEXT DEFAULT 'Computer Science & Engineering'
    );
    """)

    # 3. Modules / Roadmap Steps with Granular Checkpoints
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id INTEGER NOT NULL,
        step_number INTEGER NOT NULL,
        title TEXT NOT NULL,
        tier TEXT CHECK(tier IN ('Fundamentals', 'Core Building', 'Advanced & Cloud', 'Capstone & Industry Readiness')) NOT NULL,
        description TEXT NOT NULL,
        key_skills TEXT NOT NULL,
        resources TEXT NOT NULL,
        project_prompt TEXT,
        checkpoints_json TEXT DEFAULT '[]', -- Array of sub-topics
        UNIQUE(track_id, step_number),
        FOREIGN KEY (track_id) REFERENCES career_tracks(id) ON DELETE CASCADE
    );
    """)

    # 4. User Module Progress
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        module_id INTEGER NOT NULL,
        status TEXT CHECK(status IN ('not_started', 'in_progress', 'completed')) DEFAULT 'not_started',
        completed_checkpoints_json TEXT DEFAULT '[]',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, module_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
    );
    """)

    # 5. Quizzes / Assessments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        question TEXT NOT NULL,
        options_json TEXT NOT NULL,
        correct_index INTEGER NOT NULL,
        explanation TEXT,
        points INTEGER DEFAULT 25,
        UNIQUE(track_id, title),
        FOREIGN KEY (track_id) REFERENCES career_tracks(id) ON DELETE CASCADE
    );
    """)

    # 6. User Quiz Attempts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        track_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        passed INTEGER CHECK(passed IN (0, 1)) NOT NULL,
        attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (track_id) REFERENCES career_tracks(id) ON DELETE CASCADE
    );
    """)

    # 7. Student Projects Portfolio
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        track_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        tech_stack TEXT NOT NULL,
        github_url TEXT,
        live_demo_url TEXT,
        status TEXT CHECK(status IN ('Draft', 'Under Review', 'Verified & Approved')) DEFAULT 'Verified & Approved',
        endorsement_remarks TEXT DEFAULT 'Verified by Pydah Innovation Cell. Excellent code cleanliness and architecture.',
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, title),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (track_id) REFERENCES career_tracks(id) ON DELETE CASCADE
    );
    """)

    # 8. Placement Opportunities & Internships
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS placements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        role TEXT NOT NULL,
        track_code TEXT NOT NULL,
        package_or_stipend TEXT NOT NULL,
        package_category TEXT DEFAULT 'Dream', -- 'Standard', 'Dream' (>7LPA), 'Super Dream' (>10LPA)
        location TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        deadline TEXT NOT NULL,
        eligibility TEXT NOT NULL,
        apply_link TEXT DEFAULT '#',
        UNIQUE(company, role)
    );
    """)

    # 9. Technical Interview Flashcards Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_code TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        difficulty TEXT CHECK(difficulty IN ('Core', 'Medium', 'Advanced')) DEFAULT 'Core',
        key_concept TEXT NOT NULL,
        UNIQUE(track_code, question)
    );
    """)

    # Safe clean-up of any existing duplicates before creating unique indexes
    cursor.execute("DELETE FROM projects WHERE id NOT IN (SELECT MIN(id) FROM projects GROUP BY user_id, title);")
    cursor.execute("DELETE FROM modules WHERE id NOT IN (SELECT MIN(id) FROM modules GROUP BY track_id, step_number);")
    cursor.execute("DELETE FROM quizzes WHERE id NOT IN (SELECT MIN(id) FROM quizzes GROUP BY track_id, title);")
    cursor.execute("DELETE FROM interview_flashcards WHERE id NOT IN (SELECT MIN(id) FROM interview_flashcards GROUP BY track_code, question);")
    cursor.execute("DELETE FROM placements WHERE id NOT IN (SELECT MIN(id) FROM placements GROUP BY company, role);")

    # Ensure Unique Indexes exist for ON CONFLICT resolution
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_tracks_code ON career_tracks(code);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_modules_track_step ON modules(track_id, step_number);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_quizzes_track_title ON quizzes(track_id, title);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_flashcards_track_q ON interview_flashcards(track_code, question);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_placements_comp_role ON placements(company, role);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_user_title ON projects(user_id, title);")

    conn.commit()

    # Seed Tracks
    tracks_data = [
        ("FSD", "Full Stack Web & Cloud Architect", "Master frontend frameworks, scalable microservices, databases, and automated cloud deployments.", "Software Engineering", "code-2", "#ea580c", 90, "Very High", "Computer Science & Engineering, Information Technology"),
        ("AIML", "Artificial Intelligence & Generative AI", "From Python foundations and Deep Learning to Vector Databases, Transformers, and LLM RAG pipelines.", "AI & Data Science", "sparkles", "#f59e0b", 110, "Explosive", "Artificial Intelligence & Data Science, Computer Science & Engineering"),
        ("DEVOPS", "Cloud Native, DevOps & Site Reliability", "Build resilient CI/CD pipelines, Docker containers, Kubernetes clusters, and Terraform infrastructure.", "Cloud Infrastructure", "cloud", "#0ea5e9", 85, "High", "Computer Science & Engineering, Information Technology"),
        ("CYBER", "Cybersecurity & Ethical Penetration Testing", "Defensive network engineering, OWASP security, threat intelligence, and vulnerability remediation.", "Information Security", "shield-check", "#ef4444", 80, "Critical", "Computer Science & Engineering, Information Technology, Electronics & Communication"),
        ("APP", "Mobile App Development (Flutter & React Native)", "Cross-platform mobile applications, reactive state management, device hardware APIs, and store releases.", "Mobile Engineering", "smartphone", "#10b981", 75, "High", "Computer Science & Engineering, Information Technology"),
        ("EMBEDDED", "Embedded Systems, IoT & Robotics", "Master ARM Cortex, ESP32 microcontrollers, RTOS, sensor telemetry, PCB protocols, and ROS robotics.", "Hardware & IoT Systems", "cpu", "#06b6d4", 85, "Very High", "Electronics & Communication, Electrical & Electronics"),
        ("VLSI", "VLSI Design & Digital Verification", "Verilog HDL, FPGA prototyping, ASIC design flows, static timing analysis, and digital system design.", "Semiconductor & Chip Design", "microchip", "#8b5cf6", 95, "Very High", "Electronics & Communication"),
        ("EV_SMARTGRID", "Electric Vehicles (EV) & Smart Automation", "EV powertrains, Battery Management Systems (BMS), PLC automation, SCADA, and smart renewable grids.", "Power Tech & Automation", "zap", "#22c55e", 80, "High", "Electrical & Electronics")
    ]

    for code, title, tagline, cat, icon, color, hrs, demand, depts in tracks_data:
        cursor.execute("""
            INSERT INTO career_tracks (code, title, tagline, category, icon, badge_color, estimated_hours, demand_level, departments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
                title=excluded.title,
                tagline=excluded.tagline,
                category=excluded.category,
                icon=excluded.icon,
                badge_color=excluded.badge_color,
                estimated_hours=excluded.estimated_hours,
                demand_level=excluded.demand_level,
                departments=excluded.departments
        """, (code, title, tagline, cat, icon, color, hrs, demand, depts))

    conn.commit()

    cursor.execute("SELECT id, code FROM career_tracks")
    track_map = {row[1]: row[0] for row in cursor.fetchall()}

    # Seed Default Users & Campus Leaderboard Peers
    demo_pass_hash = generate_password_hash("pydah123")
    users_data = [
        ("Venkata Sai Teja", "student@pydah.edu.in", demo_pass_hash, "student", "Computer Science & Engineering", "3rd Year B.Tech", "Full Stack Cloud Architect", track_map["FSD"], "sai_teja", 880),
        ("Pydah SkillPath Administrator", "admin@pydah.edu.in", demo_pass_hash, "admin", "Pydah Group Dean Office", "Director of Placement Training", "Platform Administrator", track_map["FSD"], "dean_pydah", 1500),
        ("K. Ananya Reddy", "ananya.r@pydah.edu.in", demo_pass_hash, "student", "Artificial Intelligence & Data Science", "Final Year B.Tech", "AI Research Engineer", track_map["AIML"], "ananya", 920),
        ("M. Rahul Varma", "rahul.v@pydah.edu.in", demo_pass_hash, "student", "Computer Science & Engineering", "Final Year B.Tech", "Cloud DevOps Specialist", track_map["DEVOPS"], "rahul", 780),
        ("S. Sneha Latha", "sneha.l@pydah.edu.in", demo_pass_hash, "student", "Information Technology", "3rd Year B.Tech", "Full Stack Developer", track_map["FSD"], "sneha", 740),
        ("Ch. Tarun Kumar", "tarun.k@pydah.edu.in", demo_pass_hash, "student", "Electronics & Communication", "3rd Year B.Tech", "Embedded IoT Architect", track_map["EMBEDDED"], "tarun", 690)
    ]

    for name, email, pw, role, dept, yr, target, pref_id, seed, karma in users_data:
        cursor.execute("""
            INSERT OR IGNORE INTO users (name, email, password_hash, role, department, year_or_designation, target_role, preferred_track_id, avatar_seed, karma_xp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, pw, role, dept, yr, target, pref_id, seed, karma))

    # Modules Data for All Tracks
    fsd_modules = [
        (track_map["FSD"], 1, "HTML5 Semantic Architecture & Modern CSS3 Layouts", "Fundamentals", 
         "Master semantic HTML elements, CSS Flexbox, CSS Grid, mobile-first responsive design, and DevTools debugging.", 
         "HTML5, CSS Flexbox, CSS Grid, Responsive Design, CSS Variables", 
         "https://developer.mozilla.org/en-US/docs/Web/HTML", 
         "Build a responsive multi-page institutional tech club portal.",
         json.dumps(["HTML5 Semantic Structure (<header>, <main>, <article>)", "CSS Flexbox Navigation & Alignment", "CSS Grid 12-Column Responsive Layouts", "Mobile Breakpoints & Media Queries", "Chrome DevTools Layout Inspection"])),

        (track_map["FSD"], 2, "JavaScript Deep Dive & Asynchronous Programming", "Fundamentals", 
         "ES6+ syntax, scope, closures, event loop, Promises, Fetch API, and asynchronous state handling.", 
         "ES6+, Promises, Async/Await, Web Storage, REST APIs", 
         "https://javascript.info", 
         "Develop an interactive real-time weather & telemetry dashboard with live API feeds.",
         json.dumps(["ES6 Destructuring, Spread Operator & Arrow Functions", "Closures, Lexical Scope & Hoisting", "Promises and Async / Await Patterns", "Fetch API Integration & JSON Parsing", "DOM Event Delegation & Microtask Queue"])),

        (track_map["FSD"], 3, "Backend Development with Python & RESTful APIs", "Core Building", 
         "API design patterns, Flask framework, JSON serialization, routing, error handling, and middleware.", 
         "Python, Flask, REST APIs, JSON, Postman, MVC Architecture", 
         "https://flask.palletsprojects.com", 
         "Create a modular campus resource management REST API with complete endpoints.",
         json.dumps(["Flask Application Factory & Blueprint Routing", "HTTP Methods (GET, POST, PUT, DELETE) and Status Codes", "JSON Request Parsing & Error Handling Middleware", "CORS Configuration & Postman Endpoint Testing"])),

        (track_map["FSD"], 4, "Relational Databases & Data Modeling (SQLite/PostgreSQL)", "Core Building", 
         "Schema normalization (1NF-3NF), indexing, transactions, ACID properties, and relational query optimization.", 
         "SQL, Relational Modeling, Query Optimization, Foreign Keys, Indexing", 
         "https://www.sqlite.org/docs.html", 
         "Design a student gradebook & attendance relational schema with analytic queries.",
         json.dumps(["Relational Schema Design & Foreign Key Cascades", "Multi-table JOINs, GROUP BY & Window Aggregations", "ACID Transactions & Connection Pooling", "B-Tree Indexing Optimization"])),

        (track_map["FSD"], 5, "Authentication, Security & OWASP Best Practices", "Advanced & Cloud", 
         "Password hashing algorithms (bcrypt/argon2), session tokens, JWT, CORS, CSRF, and rate limiting.", 
         "Auth Flow, Werkzeug Security, OWASP Top 10, Data Encryption", 
         "https://owasp.org/www-project-top-ten/", 
         "Implement a secure multi-role access control gateway.",
         json.dumps(["PBKDF2 / Bcrypt Password Hashing with Salt", "Session Management vs Stateless JWT", "SQL Injection Mitigation via Prepared Queries", "Cross-Site Scripting (XSS) Sanitization"])),

        (track_map["FSD"], 6, "Docker Containerization & Production Deployment", "Advanced & Cloud", 
         "Containerizing full-stack apps with Dockerfile, multi-stage builds, reverse proxies, and cloud hosting.", 
         "Docker, Docker Compose, Nginx, CI/CD, Cloud Hosting", 
         "https://docs.docker.com", 
         "Containerize the backend and frontend into production-grade multi-container setups.",
         json.dumps(["Multi-stage Dockerfile Authoring", "Container Port Mapping & Volume Mounts", "Gunicorn Production WSGI Tuning", "Cloud Deployment on Render / Railway"])),

        (track_map["FSD"], 7, "Pydah Enterprise Capstone Project", "Capstone & Industry Readiness", 
         "End-to-end production application complete with automated testing, CI pipeline, monitoring, and live demo.", 
         "Full Stack Architecture, Testing, Production Monitoring, Git Workflows", 
         "https://github.com", 
         "Deliver a comprehensive full-stack enterprise platform addressing institutional workflow challenges.",
         json.dumps(["Automated Unit Testing & Mocking", "GitHub Actions CI Pipeline for Build Verification", "Production Logging & Sentry Exception Monitoring", "Final Architecture Defense and Code Walkthrough"]))
    ]

    aiml_modules = [
        (track_map["AIML"], 1, "Python for Data Science, NumPy & Pandas", "Fundamentals", 
         "Vectorized math with NumPy, tabular data manipulation with Pandas, data cleaning, and EDA.", 
         "Python, NumPy, Pandas, Matplotlib, Exploratory Data Analysis", 
         "https://numpy.org/doc/", 
         "Analyze institutional campus placement statistics across 5 years with visual reports.",
         json.dumps(["NumPy N-Dimensional Arrays & Broadcasting", "Pandas DataFrames Filtering & Merging", "Handling Missing Imputations & Outliers", "Visualizations using Seaborn / Matplotlib"])),

        (track_map["AIML"], 2, "Machine Learning Algorithms & Scikit-Learn", "Core Building", 
         "Supervised and unsupervised learning: Regression, Classification, Random Forests, K-Means, and model tuning.", 
         "Scikit-Learn, Regression, Classification, Hyperparameter Tuning", 
         "https://scikit-learn.org", 
         "Build an academic performance and dropout risk predictive classifier.",
         json.dumps(["Train-Test Split & Stratified K-Fold Cross-Validation", "Feature Scaling (StandardScaler, MinMaxScaler)", "Random Forest & Gradient Boosting Classifiers", "Confusion Matrix, ROC-AUC, and F1-Score Diagnostics"])),

        (track_map["AIML"], 3, "Deep Learning Foundations & PyTorch", "Core Building", 
         "Neural networks, backpropagation, activation functions, CNNs for computer vision, and PyTorch tensors.", 
         "PyTorch, Neural Networks, CNNs, CUDA, Transfer Learning", 
         "https://pytorch.org/tutorials/", 
         "Develop an automated student attendance facial feature recognition pipeline.",
         json.dumps(["PyTorch Tensors, Autograd & Custom Datasets", "Convolutional Neural Network (CNN) Layers", "Transfer Learning with ResNet-50", "Model Checkpointing and Inference Export"])),

        (track_map["AIML"], 4, "Natural Language Processing & Transformers", "Advanced & Cloud", 
         "Tokenization, Word2Vec, Attention mechanisms, HuggingFace transformers, BERT, and text classification.", 
         "HuggingFace, Transformers, BERT, Tokenizers, Embeddings", 
         "https://huggingface.co/docs", 
         "Create an automated institutional query classifier and sentiment analysis engine.",
         json.dumps(["BPE & WordPiece Tokenization Strategies", "Self-Attention Mechanism & Transformer Encoder", "Fine-Tuning BERT with HuggingFace Trainer", "Inference Optimization with ONNX Runtime"])),

        (track_map["AIML"], 5, "Generative AI, LLMs & Retrieval-Augmented Generation (RAG)", "Capstone & Industry Readiness", 
         "Prompt engineering, OpenAI API / Llama 3, Vector Databases (Chroma/FAISS), LangChain, and RAG pipelines.", 
         "LangChain, Vector DBs, ChromaDB, RAG Pipelines, Llama 3, Prompt Engineering", 
         "https://python.langchain.com", 
         "Engineer a verified Pydah Campus AI Assistant providing accurate syllabus guidance with citations.",
         json.dumps(["Document Ingestion, Chunking & Embedding Generation", "Vector Indexing in ChromaDB / FAISS", "Semantic Similarity Search & Top-K Retrieval", "Hallucination Mitigation & Citations Grounding"]))
    ]

    devops_modules = [
        (track_map["DEVOPS"], 1, "Linux System Administration & Shell Scripting", "Fundamentals", 
         "File permissions, process management, bash scripting, SSH keys, cron automations, and log rotation.", 
         "Linux, Bash Scripting, Cron, Systemd, SSH, Grep/Awk", 
         "https://tldp.org/LDP/Bash-Beginners-Guide/html/", 
         "Author an automated server health monitor that alerts via webhook upon memory/disk threshold breach.",
         json.dumps(["User Management & POSIX Permissions (chmod, chown)", "Bash Scripting (Loops, Conditionals, Functions)", "Process Monitoring (top, htop, ps, kill)", "Systemd Service Configuration & Cron Automation"])),

        (track_map["DEVOPS"], 2, "Continuous Integration & Automated Testing (CI)", "Core Building", 
         "GitHub Actions, linting, unit test automation, artifact publishing, and branch protection policies.", 
         "GitHub Actions, CI/CD, Pytest, Flake8, Workflow Automation", 
         "https://docs.github.com/en/actions", 
         "Build a production GitHub Actions CI pipeline executing tests and linting on every pull request.",
         json.dumps(["GitHub Actions Workflow YAML Structure", "Multi-version Matrix Test Runners", "Linting, Formatting & Code Quality Checks", "Caching Dependencies for Fast Execution"])),

        (track_map["DEVOPS"], 3, "Container Orchestration with Docker & Kubernetes", "Advanced & Cloud", 
         "Pods, Deployments, Services, ConfigMaps, Ingress controllers, and Helm chart packaging.", 
         "Kubernetes (K8s), Helm, Docker, Ingress, Persistent Volumes", 
         "https://kubernetes.io/docs/", 
         "Deploy a high-availability microservice cluster on local Minikube / K3s.",
         json.dumps(["Writing Production Dockerfiles", "Kubernetes Pods, Deployments & ReplicaSets", "Cluster Services & Ingress Routing", "ConfigMaps & Secrets Management"])),

        (track_map["DEVOPS"], 4, "Infrastructure as Code with Terraform & AWS", "Capstone & Industry Readiness", 
         "Declarative cloud provisioning (VPC, EC2, S3, RDS), state management, and cloud monitoring with Prometheus/Grafana.", 
         "Terraform, AWS, CloudWatch, Prometheus, Grafana", 
         "https://developer.hashicorp.com/terraform", 
         "Provision an enterprise VPC architecture with automated zero-downtime rolling updates.",
         json.dumps(["Terraform HCL Syntax & State Management", "AWS VPC, Subnets & Security Groups Provisioning", "Prometheus Metrics Scraping & Alerts", "Grafana Service Health Dashboards"]))
    ]

    cyber_modules = [
        (track_map["CYBER"], 1, "Network Protocols, Wireshark & Threat Vectors", "Fundamentals", 
         "TCP/IP handshakes, DNS, HTTP/S, packet inspection with Wireshark, port scanning with Nmap.", 
         "Wireshark, Nmap, TCP/IP, OSI Model, Subnetting", "https://tryhackme.com", 
         "Conduct a network topology and open port security audit.",
         json.dumps(["TCP 3-Way Handshake Analysis", "DNS & ARP Poisoning Defense", "Nmap Port & Service Discovery", "Wireshark Packet Capture Filtering"])),

        (track_map["CYBER"], 2, "Web Application Penetration Testing & OWASP", "Core Building", 
         "SQL injection, XSS, CSRF, insecure direct object references, and Burp Suite interception.", 
         "Burp Suite, OWASP Top 10, SQLMap, Vulnerability Assessment", "https://portswigger.net/web-security", 
         "Execute penetration test and compile a CVSS vulnerability remediation report.",
         json.dumps(["Burp Suite Proxy Traffic Interception", "SQL Injection Exploitation & Defense", "Cross-Site Scripting (XSS) Payloads", "CVSS Vulnerability Scoring & Reporting"]))
    ]

    app_modules = [
        (track_map["APP"], 1, "Dart Language & Flutter Widget Architecture", "Fundamentals", 
         "Object-oriented Dart, Stateless & Stateful widgets, layout trees, themes, and Material 3 design.", 
         "Flutter, Dart, Widget Trees, Material 3, Responsive UI", "https://flutter.dev", 
         "Design a campus timetable and event broadcast mobile app.",
         json.dumps(["Dart Syntax, Classes & Async Streams", "Stateless vs Stateful Lifecycle", "Column, Row, Stack & Flexible Layouts", "Material Design 3 Theme Styling"])),

        (track_map["APP"], 2, "State Management & REST API Synchronization", "Core Building", 
         "State management with Riverpod/Bloc, asynchronous HTTP feeds, JSON parsing, and offline cache.", 
         "Riverpod, Bloc, REST APIs, SharedPreferences, SQLite Mobile", "https://pub.dev", 
         "Create an offline-first student project submission mobile client.",
         json.dumps(["State Management using Riverpod Providers", "HTTP REST API Integration with Dio", "Local SQLite Storage via SQFlite", "Publishing Build Artifacts for Android/iOS"]))
    ]

    embedded_modules = [
        (track_map["EMBEDDED"], 1, "C/C++ Embedded Firmware & Microcontroller Architecture", "Fundamentals",
         "Master low-level registers, GPIO, Interrupt Service Routines (ISR), Hardware Timers, PWM, and ADC/DAC on STM32 / ESP32.",
         "C/C++, STM32, ESP32, GPIO, Hardware Interrupts, Timers, PWM",
         "https://www.embedded.com",
         "Build an interrupt-driven multi-sensor data acquisition firmware system.",
         json.dumps(["Register-Level GPIO Configuration & Bit Masking", "Hardware Timer Interrupts & Periodic Tick Generation", "Pulse Width Modulation (PWM) Duty Cycle Control", "Analog-to-Digital Converter (ADC) Continuous DMA Sampling", "Debugging with OpenOCD & GDB"])),

        (track_map["EMBEDDED"], 2, "Hardware Communication Protocols (UART, SPI, I2C & CAN Bus)", "Fundamentals",
         "Implement serial communication pipelines, frame parsing, checksums, and CAN bus telemetry for automotive/industrial systems.",
         "UART, SPI, I2C, CAN Bus, Logic Analyzers, Oscilloscopes",
         "https://www.bosch-semiconductors.com/can-literature",
         "Interconnect multiple microcontrollers over CAN & I2C with bus error detection.",
         json.dumps(["I2C Master-Slave Addressing & Clock Stretching", "High-Speed SPI Full-Duplex Sensor Interfacing", "UART Packet Framing, Ring Buffers & Checksums", "CAN 2.0B Frame Filtering & Arbitration ID Handling", "Serial Bus Decoding with Saleae Logic Analyzer"])),

        (track_map["EMBEDDED"], 3, "Real-Time Operating Systems (FreeRTOS & RT-Thread)", "Core Building",
         "Preemptive task scheduling, inter-task communication with queues, binary/counting semaphores, mutexes, and priority inversion prevention.",
         "FreeRTOS, Task Scheduling, Mutexes, Semaphores, Queues, ISR Safe APIs",
         "https://www.freertos.org",
         "Develop a concurrent multi-tasking industrial telemetry controller running FreeRTOS.",
         json.dumps(["Preemptive Priority-Based Task Scheduling", "Inter-Task Communication via Message Queues", "Mutexes & Priority Ceiling / Priority Inheritance", "Software Timers & Event Groups", "ISR-Safe FreeRTOS API Integration (xQueueSendFromISR)"])),

        (track_map["EMBEDDED"], 4, "IoT Edge Telemetry, MQTT & Cloud Connectivity", "Advanced & Cloud",
         "Wi-Fi and BLE stack management, MQTT publish/subscribe protocols, TLS certificates, and edge device provisioning on AWS IoT Core.",
         "ESP32 Wi-Fi, MQTT, TLS, AWS IoT Core, Node-RED, JSON Telemetry",
         "https://mqtt.org",
         "Connect embedded nodes to an enterprise IoT cloud dashboard with live alerts.",
         json.dumps(["Wi-Fi Station & AP Modes with Reconnection State Machine", "MQTT Client Connection with TLS Certificate Validation", "JSON Telemetry Payload Serialization", "OTA (Over-The-Air) Firmware Updates", "Cloud Dashboard Integration with AWS IoT / Node-RED"])),

        (track_map["EMBEDDED"], 5, "Robotics Kinematics, Sensor Fusion & ROS2 Basics", "Advanced & Cloud",
         "Inertial Measurement Units (IMU), Kalman Filter sensor fusion, differential drive kinematics, and ROS2 publisher-subscriber nodes.",
         "ROS2, IMU, Kalman Filter, Differential Drive, Robot Kinematics",
         "https://docs.ros.org",
         "Build a 2-wheel differential drive robot model with sensor fusion heading estimation.",
         json.dumps(["6-DOF IMU (Accelerometer/Gyroscope) Sensor Fusion", "Complementary & Extended Kalman Filter (EKF) Heading Estimation", "Differential Drive Forward & Inverse Kinematics", "ROS2 Nodes, Topics, and Messages Authoring"])),

        (track_map["EMBEDDED"], 6, "ECE Autonomous Smart Edge Gateway Capstone", "Capstone & Industry Readiness",
         "Production-ready edge computing hardware node with cloud telemetry, fail-safe watchdogs, local LCD diagnostics, and OTA update pipeline.",
         "FreeRTOS, STM32/ESP32, MQTT, Edge Telemetry, Watchdog Timers, CI Firmware",
         "https://pydah.edu.in/ece-innovation",
         "Deploy a complete autonomous hardware gateway for industrial environmental monitoring.",
         json.dumps(["Hardware Watchdog & Fault Tolerance Implementation", "Power Optimization & Deep Sleep Wakeup Triggers", "Local OLED / LCD Status & Diagnostics Interface", "Complete Capstone Verification & Industry Code Review"]))
    ]

    vlsi_modules = [
        (track_map["VLSI"], 1, "Digital Logic Design & Verilog HDL Fundamentals", "Fundamentals",
         "Combinational and sequential digital systems, finite state machines (Mealy & Moore), Verilog operators, and testbench writing.",
         "Verilog HDL, FSM Design, Combinational Logic, Testbenches, ModelSim",
         "https://www.asic-world.com/verilog",
         "Design and simulate an 8-bit Arithmetic Logic Unit (ALU) with status flags.",
         json.dumps(["Structural vs Behavioral Verilog Modeling", "Blocking (=) vs Non-blocking (<=) Assignments", "Mealy and Moore Finite State Machine Design", "Writing Directed and Randomized Verilog Testbenches"])),

        (track_map["VLSI"], 2, "FPGA Prototyping & Vivado Implementation", "Core Building",
         "FPGA architecture (CLBs, LUTs, DSP slices), synthesis constraints (XDC), timing closure, and on-chip hardware debugging using ILA.",
         "FPGA, Xilinx Vivado, LUTs, XDC Constraints, Integrated Logic Analyzer (ILA)",
         "https://www.xilinx.com/support/documentation",
         "Implement an audio frequency synthesizer on a Xilinx Artix-7 FPGA board.",
         json.dumps(["FPGA Architecture: LUTs, Flip-Flops, DSP48 & Block RAM", "Vivado Synthesis, Implementation & Bitstream Generation", "Timing Constraints (.xdc) & Clock Domain Crossing", "Hardware In-System Debugging using Integrated Logic Analyzer (ILA)"])),

        (track_map["VLSI"], 3, "SystemVerilog & UVM Verification Methodology", "Advanced & Cloud",
         "Object-Oriented verification, SystemVerilog assertions (SVA), coverage-driven verification, and Universal Verification Methodology (UVM) testbenches.",
         "SystemVerilog, UVM, Functional Coverage, Assertions, Constrained Randomization",
         "https://www.accellera.org/community/uvm",
         "Develop a UVM verification environment with driver, monitor, and scoreboard for an AXI-Stream interface.",
         json.dumps(["SystemVerilog OOP: Classes, Virtual Methods & Mailboxes", "Constrained-Random Stimulus Generation", "SystemVerilog Assertions (SVA) for Protocol Checking", "UVM Testbench Architecture: Driver, Monitor, Sequencer, Scoreboard"])),

        (track_map["VLSI"], 4, "ASIC Physical Design Flow & CMOS Layout", "Capstone & Industry Readiness",
         "Logic synthesis, floorplanning, power planning, clock tree synthesis (CTS), routing, Static Timing Analysis (STA), and DRC/LVS physical signoff.",
         "Physical Design, STA, CTS, DRC, LVS, OpenROAD / Cadence Flow",
         "https://theopenroadproject.org",
         "Complete RTL-to-GDSII flow for an open-source RISC-V core using OpenROAD.",
         json.dumps(["Static Timing Analysis (Setup and Hold Slack Verification)", "Floorplanning, Macro Placement & Power Distribution Network (PDN)", "Clock Tree Synthesis (CTS) & Skew Minimization", "Design Rule Check (DRC) & Layout Versus Schematic (LVS) Signoff"]))
    ]

    ev_modules = [
        (track_map["EV_SMARTGRID"], 1, "Power Electronics & BLDC Motor Drives", "Fundamentals",
         "Power semiconductor devices (MOSFET, IGBT), DC-DC converters, Field Oriented Control (FOC) of Brushless DC (BLDC) motors, and PWM inverters.",
         "Power Electronics, BLDC Motors, Inverters, DC-DC Converters, MATLAB Simulink",
         "https://www.mathworks.com/solutions/power-electronics.html",
         "Simulate a 3-phase inverter driving a BLDC motor with speed controller feedback.",
         json.dumps(["MOSFET/IGBT Gate Drive Circuits & Switching Losses", "Buck, Boost & Buck-Boost Converter Topologies", "Space Vector PWM (SVPWM) Inverter Generation", "Field Oriented Control (FOC) Fundamentals for EV Drives"])),

        (track_map["EV_SMARTGRID"], 2, "Battery Management Systems (BMS) & EV Powertrains", "Core Building",
         "Lithium-ion cell characteristics, active/passive cell balancing, State of Charge (SoC) estimation, thermal runaway prevention, and CAN telemetry.",
         "BMS, Li-Ion Chemistry, SoC Estimation, Thermal Management, CAN Telemetry",
         "https://www.batteryuniversity.com",
         "Build a BMS hardware model monitoring cell voltages, temperature, and over-current trip.",
         json.dumps(["Lithium-Ion Charge/Discharge Curves & Safety Limits", "Passive vs Active Shunt Resistor Cell Balancing", "Coulomb Counting & Extended Kalman Filter for SoC Estimation", "BMS Safety Interlocks & Contactor Control Sequence"])),

        (track_map["EV_SMARTGRID"], 3, "Industrial PLC Automation & SCADA Telemetry", "Advanced & Cloud",
         "Programmable Logic Controllers (PLC), Ladder Logic, Modbus TCP, OPC-UA protocols, SCADA supervisory monitoring, and industrial HMI screens.",
         "PLC, Ladder Logic, SCADA, Modbus TCP, OPC-UA, Siemens TIA Portal",
         "https://plcopen.org",
         "Design an automated batch control SCADA dashboard communicating with a software PLC.",
         json.dumps(["Ladder Diagram (LD) Programming & Timers/Counters", "Modbus TCP/IP Register Mapping & Communications", "SCADA Tag Configuration, Alarming & Real-time Trends", "Safety Instrumented Systems (SIS) & Emergency Stop Interlocks"])),

        (track_map["EV_SMARTGRID"], 4, "Smart Grid Telemetry & Renewable Energy Integration", "Capstone & Industry Readiness",
         "Microgrids, solar PV grid-tied inverters, smart net metering, grid synchronization (PLL), and power quality monitoring.",
         "Smart Grid, Solar PV, Microgrid, Grid Inverters, Net Metering",
         "https://www.ieee-pes.org",
         "Simulate a hybrid solar-storage microgrid with automated grid islanding transition.",
         json.dumps(["Grid-Tie Inverter Synchronization using Phase Locked Loop (PLL)", "Maximum Power Point Tracking (MPPT) Algorithms", "Smart Metering Protocols & Bi-directional Power Flow Analysis", "Microgrid Islanding Detection & Seamless Reconnection"]))
    ]

    all_modules = fsd_modules + aiml_modules + devops_modules + cyber_modules + app_modules + embedded_modules + vlsi_modules + ev_modules

    for m in all_modules:
        cursor.execute("""
            INSERT INTO modules (track_id, step_number, title, tier, description, key_skills, resources, project_prompt, checkpoints_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(track_id, step_number) DO UPDATE SET
                title=excluded.title,
                tier=excluded.tier,
                description=excluded.description,
                key_skills=excluded.key_skills,
                resources=excluded.resources,
                project_prompt=excluded.project_prompt,
                checkpoints_json=excluded.checkpoints_json
        """, m)

    conn.commit()

    # Pre-seed progress for the demo student
    cursor.execute("SELECT id FROM users WHERE email = 'student@pydah.edu.in'")
    demo_student_row = cursor.fetchone()
    if demo_student_row:
        demo_student_id = demo_student_row[0]
        cursor.execute("SELECT id, checkpoints_json FROM modules WHERE track_id = ? ORDER BY step_number ASC", (track_map["FSD"],))
        fsd_module_records = cursor.fetchall()

        if len(fsd_module_records) >= 3:
            # Module 1 completed with all checkpoints
            m1_id, m1_cp = fsd_module_records[0]
            cursor.execute("""
                INSERT OR IGNORE INTO user_progress (user_id, module_id, status, completed_checkpoints_json)
                VALUES (?, ?, 'completed', ?)
            """, (demo_student_id, m1_id, m1_cp))

            # Module 2 completed
            m2_id, m2_cp = fsd_module_records[1]
            cursor.execute("""
                INSERT OR IGNORE INTO user_progress (user_id, module_id, status, completed_checkpoints_json)
                VALUES (?, ?, 'completed', ?)
            """, (demo_student_id, m2_id, m2_cp))

            # Module 3 in progress
            m3_id, m3_cp = fsd_module_records[2]
            m3_list = json.loads(m3_cp) if m3_cp else []
            checked_sample = json.dumps(m3_list[:2])
            cursor.execute("""
                INSERT OR IGNORE INTO user_progress (user_id, module_id, status, completed_checkpoints_json)
                VALUES (?, ?, 'in_progress', ?)
            """, (demo_student_id, m3_id, checked_sample))

    # Seed Quizzes (Comprehensive Question Bank across all 8 tracks)
    quizzes_data = [
        # FSD
        (track_map["FSD"], "Full Stack Fundamentals", 
         "Which HTTP status code signifies that a client request was successfully processed and created a new resource?", 
         '["200 OK", "201 Created", "204 No Content", "304 Not Modified"]', 1, 
         "HTTP 201 Created indicates the request has succeeded and led to the creation of a new resource on the server.", 25),

        (track_map["FSD"], "JavaScript Asynchronous Lifecycle", 
         "In the browser JavaScript runtime, which queue handles resolved Promises callbacks?", 
         '["MacroTask Queue", "MicroTask Queue", "Call Stack directly", "Worker Thread Buffer"]', 1, 
         "Promise callbacks (.then/.catch) and queueMicrotask run in the Microtask Queue, prioritizing over regular macrotasks like setTimeout.", 25),

        (track_map["FSD"], "Database Indexing & Performance", 
         "Why is a B-Tree index commonly utilized in relational databases over a Hash index for primary keys?", 
         '["It consumes zero disk memory", "It supports range queries (<, <=, BETWEEN) efficiently", "It executes writes faster than no index", "It automatically normalizes data to 3NF"]', 1, 
         "B-Tree indices maintain sorted order, making range queries, inequality checks, and ORDER BY queries extremely fast.", 25),

        (track_map["FSD"], "Web Application Security", 
         "Which technique provides the most resilient defense against SQL Injection attacks in web APIs?", 
         '["Sanitizing client-side input in HTML", "Using parameterized queries (prepared statements)", "Encoding text to base64 before storing", "Turning off database foreign keys"]', 1, 
         "Parameterized queries separate the query structure from user parameters, preventing input from altering the SQL statement.", 25),

        (track_map["FSD"], "REST API Idempotency",
         "Which of the following standard HTTP methods is NOT guaranteed to be idempotent according to HTTP specifications?",
         '["GET", "PUT", "POST", "DELETE"]', 2,
         "POST is non-idempotent because executing it multiple times produces multiple distinct resources (e.g. duplicate orders). GET, PUT, and DELETE are idempotent.", 25),

        (track_map["FSD"], "Relational ACID Transactions",
         "In database transactions, which ACID property ensures that partially executed transactions are rolled back completely upon system crash?",
         '["Atomicity", "Consistency", "Isolation", "Durability"]', 0,
         "Atomicity guarantees 'all-or-nothing' execution; if any step fails or crashes, all changes are rolled back to the pre-transaction state.", 25),

        (track_map["FSD"], "CSS Flexbox Cross-Axis Alignment",
         "In CSS Flexbox, which property aligns flex items along the cross-axis (perpendicular to flex-direction)?",
         '["justify-content", "align-items", "flex-wrap", "gap"]', 1,
         "align-items aligns items along the cross-axis, whereas justify-content aligns items along the main-axis.", 25),

        # AIML
        (track_map["AIML"], "Model Evaluation Metrics", 
         "In a campus medical anomaly diagnosis system where missing a positive case has severe consequences, which metric should you maximize?", 
         '["Precision", "Recall (Sensitivity)", "Specificity", "F-beta where beta=0.5"]', 1, 
         "Recall maximizes true positives and minimizes false negatives (critical in healthcare / safety).", 25),

        (track_map["AIML"], "GenAI & RAG Architecture", 
         "What is the primary role of a Vector Database in a Retrieval-Augmented Generation (RAG) system?", 
         '["Fine-tuning model weights with backprop", "Executing high-speed similarity search on text embeddings", "Compiling Python bytecode to C", "Converting audio waveforms to text"]', 1, 
         "Vector databases store dense embeddings and perform cosine/k-NN similarity searches to provide relevant context to the LLM.", 25),

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
        (track_map["DEVOPS"], "Docker Layer Caching", 
         "Why is it recommended in a Node or Python Dockerfile to copy requirements.txt/package.json before copying the entire source directory?", 
         '["To minimize image color depth", "To leverage Docker build layer caching and avoid redundant dependency installations", "Docker requires it for compiling", "It encrypts the dependencies"]', 1, 
         "Docker caches layers; if requirements have not changed, it skips re-downloading packages, dramatically speeding up builds.", 25),

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
        (track_map["EMBEDDED"], "Microcontroller Hardware Interrupts",
         "What happens when a high-priority hardware interrupt fires while the CPU is executing the main loop in an ARM Cortex-M?",
         '["The CPU crashes immediately", "The CPU pushes register context to the stack and jumps to the Interrupt Vector Handler", "The interrupt is permanently ignored until reboot", "The compiler converts the loop to C++"]', 1,
         "ARM Cortex-M hardware automatically saves the context (R0-R3, R12, LR, PC, xPSR) to the active stack and executes the ISR.", 25),
        
        (track_map["EMBEDDED"], "CAN Bus Arbitration",
         "How does CAN bus resolve collisions when two nodes transmit simultaneously?",
         '["First node to transmit always wins", "Non-destructive bitwise arbitration where the lower identifier (dominant 0) wins", "Both messages are corrupted and discarded", "The bus master chooses randomly"]', 1,
         "In CAN arbitration, dominant bits (0) overwrite recessive bits (1). The node with the lower message ID continues transmitting without interruption.", 25),

        (track_map["EMBEDDED"], "C Volatile Qualifier",
         "Why must global flags modified inside an Interrupt Service Routine (ISR) be declared as 'volatile' in embedded C?",
         '["To allocate them in EEPROM memory", "To prevent compiler optimization from assuming the variable never changes in the main loop", "To encrypt the variable value", "To speed up floating point division"]', 1,
         "Without volatile, the compiler's optimizer assumes no other code changes the flag in the loop and caches it in a register, causing infinite loops.", 25),

        (track_map["EMBEDDED"], "Direct Memory Access (DMA)",
         "What is the greatest architectural advantage of using DMA for high-speed ADC sampling in microcontrollers?",
         '["It quadruples CPU clock speed", "It streams analog sample buffers into RAM with zero CPU intervention, freeing 100% of CPU cycles", "It eliminates the need for power supplies", "It converts code to assembly"]', 1,
         "DMA moves data directly between peripherals and SRAM via the system bus matrix, preventing CPU bottlenecking.", 25),

        # VLSI
        (track_map["VLSI"], "Verilog Assignments",
         "Which assignment operator should be used for clocked sequential registers (flip-flops) in an always @(posedge clk) block in Verilog?",
         '["Blocking assignment (=)", "Non-blocking assignment (<=)", "Continuous assignment (assign)", "Pointer dereference (*)"]', 1,
         "Non-blocking assignments (<=) schedule evaluations concurrently, accurately modeling physical flip-flop clock edge registers and preventing simulation race conditions.", 25),

        (track_map["VLSI"], "Setup Time Slack Calculation",
         "In Static Timing Analysis (STA), what does positive Setup Slack (+0.8ns) indicate about a digital timing path?",
         '["The path has failed and violates timing", "Data arrives safely 0.8ns before the required clock edge and meets timing criteria", "Clock jitter is greater than 1GHz", "The flip-flop has entered metastability"]', 1,
         "Positive slack means data arrives before the required setup threshold, confirming the circuit will operate reliably at the target frequency.", 25),

        (track_map["VLSI"], "FPGA Look-Up Tables",
         "In modern FPGAs, what basic hardware building block physically implements arbitrary combinational boolean logic functions?",
         '["Look-Up Table (LUT) with SRAM configuration cells", "Hard-wired NAND gate arrays", "Analog operational amplifiers", "Bipolar junction transistors"]', 0,
         "LUTs are small truth-table RAMs (typically 4 to 6 inputs) that emulate any truth table by storing pre-computed outputs.", 25),

        # EV_SMARTGRID
        (track_map["EV_SMARTGRID"], "BLDC Inverter Switching",
         "What is the role of Space Vector PWM (SVPWM) in an electric vehicle 3-phase motor inverter?",
         '["Increases battery pack voltage", "Maximizes DC bus voltage utilization and reduces motor current harmonic distortion", "Converts AC to DC", "Monitors tire pressure"]', 1,
         "SVPWM provides up to 15.5% higher DC bus voltage utilization than conventional sinusoidal PWM with lower total harmonic distortion (THD).", 25),

        (track_map["EV_SMARTGRID"], "Lithium-Ion Thermal Runaway",
         "What critical failure mechanism occurs when an EV Li-Ion cell is pierced or overcharged, triggering uncontrollable exothermic heat release?",
         '["Electrochemical passivation", "Thermal Runaway", "Hydrogen embrittlement", "Magnetic saturation"]', 1,
         "Thermal runaway is a self-sustaining positive feedback loop where internal shorting generates extreme heat and decomposition gases.", 25),

        (track_map["EV_SMARTGRID"], "Smart Grid Modbus Protocol",
         "In industrial SCADA and PLC communication, what is the maximum standard transmission speed of Modbus RTU over RS-485 serial links?",
         '["10 Gbps", "115,200 baud (typically 9600 to 115200 bps)", "100 MHz", "1.5 Mbps"]', 1,
         "Modbus RTU serial links run over balanced twisted-pair RS-485 differential lines up to 115,200 baud over long industrial distances.", 25)
    ]

    for q in quizzes_data:
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

    conn.commit()

    # Seed Technical Interview Flashcards (35 Complete Questions across all 8 tracks)
    flashcards_data = [
        # FSD
        ("FSD", "What is the difference between SQL and NoSQL databases, and when would you choose which?", 
         "SQL databases (PostgreSQL, SQLite) are relational, table-based, enforce rigid schemas, and guarantee ACID transactions—ideal for financial, ERP, and relational data. NoSQL databases (MongoDB, DynamoDB) are document/key-value based, offer flexible schemas and horizontal scaling, suited for rapid prototyping, real-time analytics, or unstructured documents.", 
         "Core", "Database Architecture"),

        ("FSD", "Explain the JavaScript Event Loop and the difference between Microtasks and Macrotasks.", 
         "The JavaScript engine is single-threaded. Synchronous code executes first on the Call Stack. When asynchronous operations finish, their callbacks enter queues: Microtasks (Promises, queueMicrotask) have higher priority and run immediately after the current call stack clears, before any Macrotask (setTimeout, setInterval, I/O events) executes.", 
         "Medium", "Asynchronous JavaScript"),

        ("FSD", "How do you defend against Cross-Site Request Forgery (CSRF) and Cross-Site Scripting (XSS)?", 
         "To prevent CSRF: use SameSite=Strict/Lax cookie attributes, anti-CSRF synchronizer tokens in POST requests, and custom header validation. To prevent XSS: escape/sanitize all user-generated input rendered in HTML, utilize modern UI frameworks with auto-escaping, and implement a strict Content Security Policy (CSP).", 
         "Advanced", "Web Security"),

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
        ("AIML", "What is the difference between Overfitting and Underfitting, and how do you mitigate Overfitting?", 
         "Overfitting occurs when a model learns training data noise and fails to generalize (low train loss, high val loss). Underfitting occurs when the model is too simple to capture patterns. Mitigate overfitting using L1/L2 regularization, dropout layers, cross-validation, data augmentation, early stopping, and pruning.", 
         "Core", "Machine Learning"),

        ("AIML", "Walk through how Retrieval-Augmented Generation (RAG) works from prompt to response.", 
         "1. Input: User submits a query. 2. Embed: Query is converted into a high-dimensional vector. 3. Retrieve: Vector DB performs cosine/k-NN similarity search on document chunks. 4. Augment: Relevant chunks are injected into the LLM system prompt as context. 5. Generate: The LLM produces a grounded, hallucination-free answer with exact citations.", 
         "Advanced", "Generative AI"),

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
        ("DEVOPS", "What is the difference between a Container (Docker) and a Virtual Machine (VM)?", 
         "A Virtual Machine virtualizes hardware and runs a full guest operating system on top of a Hypervisor, taking gigabytes and minutes to boot. A Docker Container shares the host OS kernel and isolates processes using Linux namespaces and cgroups, making it megabytes in size, starting in milliseconds, and consuming far less RAM.", 
         "Core", "Containerization"),

        ("DEVOPS", "What are the key differences between Kubernetes Deployment, Service, and Ingress?", 
         "Deployment manages Pod lifecycles, replicas, and rolling zero-downtime updates. Service provides a stable internal IP and load balances traffic across ephemeral Pods. Ingress acts as the smart HTTP/HTTPS reverse proxy routing external client domains and paths to the appropriate internal Services.", 
         "Medium", "Kubernetes Orchestration"),

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
        ("EMBEDDED", "What is Priority Inversion in an RTOS, and how does Priority Inheritance solve it?",
         "Priority Inversion occurs when a low-priority task holds a shared resource (mutex) needed by a high-priority task, and a medium-priority task preempts the low-priority task, effectively blocking the high-priority task indefinitely. Priority Inheritance solves this by temporarily raising the priority of the low-priority task to match the high-priority task until it releases the mutex.", "Advanced", "RTOS Synchronization"),

        ("EMBEDDED", "Explain the difference between SPI and I2C protocols regarding speed, wire count, and arbitration.",
         "SPI is a 4-wire (MOSI, MISO, SCK, CS), full-duplex, master-slave protocol capable of high clock speeds (10-50+ MHz) without arbitration. I2C is a 2-wire (SDA, SCL), half-duplex, multi-master protocol with hardware addressing and clock stretching, typically running at 100 kHz to 3.4 MHz.", "Core", "Hardware Protocols"),

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
        ("VLSI", "Explain Setup Time and Hold Time violations in digital sequential design.",
         "Setup Time is the minimum time data must remain stable before the active clock edge. Hold Time is the minimum time data must remain stable after the active clock edge. Violating either causes metastability in the flip-flop. Setup violations are fixed by reducing combinational logic delay or slowing the clock. Hold violations are fixed by inserting delay buffers on the data path.", "Core", "Digital Timing Analysis"),

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
        ("EV_SMARTGRID", "Why is Cell Balancing essential in high-voltage EV Lithium-Ion battery packs?",
         "Due to manufacturing tolerances, cells have slightly different capacities and self-discharge rates. During charging, the weakest cell reaches maximum voltage first, stopping charging early; during discharge, it empties first, shutting down the pack. Active/passive cell balancing equalizes state of charge, maximizing usable battery range and preventing thermal overcharging.", "Core", "Battery Management Systems"),

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

    for f in flashcards_data:
        cursor.execute("""
            INSERT INTO interview_flashcards (track_code, question, answer, difficulty, key_concept)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(track_code, question) DO UPDATE SET
                answer=excluded.answer,
                difficulty=excluded.difficulty,
                key_concept=excluded.key_concept
        """, f)

    # Seed Projects for Demo Student
    if demo_student_row:
        projects_data = [
            (demo_student_id, track_map["FSD"], "Pydah Smart Campus Resource Tracker", 
             "A unified cloud dashboard tracking seminar hall bookings, laboratory hardware status, and live student attendance using responsive layouts and REST APIs.",
             "Python, Flask, SQLite, Vanilla CSS, Chart.js",
             "https://github.com/pydah-student/smart-campus-tracker",
             "https://smartcampus.pydah.edu.in",
             "Verified & Approved",
             "Commendable architectural separation between data access and presentation layers. Approved by Pydah Innovation Cell.")
        ]

        for p in projects_data:
            cursor.execute("""
                INSERT INTO projects (user_id, track_id, title, summary, tech_stack, github_url, live_demo_url, status, endorsement_remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, title) DO UPDATE SET
                    summary=excluded.summary,
                    tech_stack=excluded.tech_stack,
                    status=excluded.status
            """, p)

    # Seed Placement Opportunities (24 Drives across Standard, Dream, Super Dream)
    placements_data = [
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

        ("Texas Instruments", "Embedded Systems Engineer", "EMBEDDED", "₹ 15.0 - 18.5 LPA", "Super Dream", "Bengaluru", 
         "C/C++, ARM Cortex, FreeRTOS, SPI/I2C/CAN, Hardware Debugging", "25 Nov 2026", "ECE / EEE with hardware projects", "https://careers.ti.com"),

        ("Intel Corporation", "VLSI Verification Engineer", "VLSI", "₹ 16.0 - 22.0 LPA", "Super Dream", "Bengaluru", 
         "SystemVerilog, UVM, Verilog HDL, Static Timing Analysis", "30 Nov 2026", "ECE / EEE (70%+ aggregate)", "https://jobs.intel.com"),

        ("Qualcomm India", "Embedded Firmware Engineer", "EMBEDDED", "₹ 12.0 - 16.0 LPA", "Super Dream", "Hyderabad", 
         "C/C++, RTOS, Microcontrollers, Protocols (I2C/SPI)", "20 Nov 2026", "ECE / EEE / CSE with hardware capstone", "https://qualcomm.com/careers"),

        ("Amazon Web Services (AWS)", "Cloud Support Associate", "DEVOPS", "₹ 14.5 LPA", "Super Dream", "Hyderabad", 
         "Linux, Docker, Networking, Cloud fundamentals, Scripting", "28 Oct 2026", "Graduating Cohort 2026/2027", "https://amazon.jobs"),

        ("Palo Alto Networks", "Cyber Security Operations Analyst", "CYBER", "₹ 16.0 - 19.5 LPA", "Super Dream", "Bengaluru",
         "Threat Analysis, SIEM, Wireshark, OWASP Top 10, Network Defense, Python Scripting", "05 Jan 2027", "CSE / IT / ECE with certified cybersecurity labs or CTF rankings", "https://paloaltonetworks.com/careers"),

        ("CrowdStrike", "Penetration Tester & Vulnerability Analyst", "CYBER", "₹ 14.0 - 18.0 LPA", "Super Dream", "Pune / Remote",
         "Burp Suite, Metasploit, Reverse Engineering, Exploit Analysis, Linux Security", "08 Jan 2027", "All B.Tech streams with hands-on ethical hacking experience", "https://crowdstrike.com/careers"),

        ("PhonePe", "Mobile Application Systems Engineer", "APP", "₹ 15.0 - 19.0 LPA", "Super Dream", "Bengaluru",
         "Flutter, Dart, React Native, REST API sync, Offline Caching, Device Hardware APIs", "12 Jan 2027", "B.Tech with published Play Store or App Store client applications", "https://phonepe.com/careers"),

        ("Swiggy", "Mobile & Frontend Engineering Specialist", "APP", "₹ 12.0 - 15.5 LPA", "Super Dream", "Hyderabad / Bengaluru",
         "Dart/Flutter, Kotlin, React, State Management (Riverpod/Bloc), Performance Profiling", "15 Jan 2027", "Graduating cohort with demonstrated mobile app projects", "https://swiggy.com/careers"),

        ("Tata Motors Electric Mobility", "EV Battery Pack & BMS Systems Engineer", "EV_SMARTGRID", "₹ 10.0 - 13.5 LPA", "Dream", "Pune",
         "Power Electronics, Battery Management Systems (BMS), MATLAB/Simulink, CAN bus, Thermal Control", "30 Jan 2027", "EEE / Mechanical / ECE with electric vehicle capstone", "https://tatamotors.com/careers"),

        ("Ola Electric / Ather Energy", "EV Powertrain & BMS Engineer", "EV_SMARTGRID", "₹ 9.5 - 13.0 LPA", "Dream", "Bengaluru / Hosur", 
         "Power Electronics, BMS, MATLAB/Simulink, CAN bus, Li-Ion testing", "02 Dec 2026", "EEE / Mechanical / ECE graduates", "https://careers.olaelectric.com"),

        ("Bosch Global Software", "Automotive Embedded & IoT Firmware Engineer", "EMBEDDED", "₹ 8.5 - 11.0 LPA", "Dream", "Bengaluru / Coimbatore",
         "Embedded C/C++, ARM Cortex-M, FreeRTOS, CAN Bus, AUTOSAR basics, SPI/I2C Protocols", "20 Jan 2027", "ECE / EEE / Mechanical with embedded systems capstone", "https://bosch.com/careers"),

        ("Schneider Electric", "Smart Grid Automation & SCADA Specialist", "EV_SMARTGRID", "₹ 8.5 - 11.5 LPA", "Dream", "Hyderabad / Vadodara",
         "PLC Programming, SCADA Systems, Modbus/OPC-UA, Renewable Microgrids, Power Distribution", "05 Feb 2027", "EEE / ECE graduates with industrial automation lab experience", "https://se.com/careers"),

        ("L&T Technology Services", "Embedded Firmware & RTOS Specialist", "EMBEDDED", "₹ 7.5 - 9.5 LPA", "Dream", "Mysuru / Chennai",
         "C/C++, Microcontrollers (STM32/ESP32), RTOS Task Scheduling, Hardware Debugging", "25 Jan 2027", "ECE / EEE graduates (60%+ in B.Tech)", "https://ltts.com/careers"),

        ("TCS Digital / Prime", "Systems Engineer - Full Stack", "FSD", "₹ 7.5 - 9.0 LPA", "Dream", "Hyderabad / Bengaluru", 
         "Python, React/Vanilla JS, REST APIs, SQL, Git", "15 Oct 2026", "B.Tech CSE/IT/ECE (60%+ in 10th, 12th, B.Tech)", "https://careers.tcs.com"),

        ("Infosys Springboard Hub", "AI & Data Science Analyst", "AIML", "₹ 8.0 - 9.5 LPA", "Dream", "Bengaluru / Pune", 
         "Python, Pandas, Scikit-Learn, Deep Learning, SQL", "12 Nov 2026", "7.0+ CGPA with Verified Projects", "https://infosys.com/careers"),

        ("Fractal Analytics", "AI & Machine Learning Specialist", "AIML", "₹ 9.0 - 12.0 LPA", "Dream", "Bengaluru / Mumbai",
         "Python, Pandas, Scikit-Learn, NLP, Vector DBs, RAG Architecture, SQL", "10 Feb 2027", "AI & DS / CSE with analytics and data science project portfolio", "https://fractal.ai/careers"),

        ("Cognizant GenC Elevate", "Full Stack Developer", "FSD", "₹ 5.5 - 6.5 LPA", "Standard", "Visakhapatnam / Chennai", 
         "HTML5, CSS3, JavaScript, Relational DB, Clean Code", "05 Nov 2026", "All B.Tech Streams", "https://careers.cognizant.com"),

        ("Accenture Advanced Technology", "Full Stack Application Developer", "FSD", "₹ 6.5 - 8.0 LPA", "Standard", "Hyderabad / Visakhapatnam",
         "HTML5, CSS3, JavaScript/TypeScript, Python/Java, SQL, Git, Agile Development", "15 Feb 2027", "Open to all Engineering branches with fundamental coding proficiency", "https://accenture.com/careers"),

        ("Wipro Turbo", "Cloud Infrastructure & DevOps Associate", "DEVOPS", "₹ 6.5 - 7.5 LPA", "Standard", "Hyderabad / Bengaluru",
         "Linux Administration, Shell Scripting, Docker Basics, CI/CD, Networking Fundamentals", "20 Feb 2027", "All B.Tech streams with 60%+ throughout academics", "https://wipro.com/careers")
    ]

    for p in placements_data:
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
    print("Database pydah_skillpath.db successfully initialized with all departments and clean unique constraints!")

if __name__ == "__main__":
    do_reset = "--reset" in sys.argv or "-r" in sys.argv
    init_database(reset=do_reset)
