import sqlite3
import os
import json
import shutil

DB_PATH = os.path.join(os.path.dirname(__file__), "pydah_skillpath.db")
BAK_PATH = os.path.join(os.path.dirname(__file__), "pydah_skillpath.db.bak")

def migrate():
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    # Backup
    shutil.copy2(DB_PATH, BAK_PATH)
    print(f"Backed up database to {BAK_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")

    # 1. Add preferred_track_id to users if not present
    cursor.execute("PRAGMA table_info(users);")
    user_cols = [c[1] for c in cursor.fetchall()]
    if "preferred_track_id" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN preferred_track_id INTEGER;")
        print("Added preferred_track_id column to users table.")

    # 2. Add departments to career_tracks if not present
    cursor.execute("PRAGMA table_info(career_tracks);")
    track_cols = [c[1] for c in cursor.fetchall()]
    if "departments" not in track_cols:
        cursor.execute("ALTER TABLE career_tracks ADD COLUMN departments TEXT;")
        print("Added departments column to career_tracks table.")

    # 3. Add new tracks if not present
    new_tracks = [
        ("FSD", "Full Stack Web & Cloud Architect", "Master frontend frameworks, scalable microservices, databases, and automated cloud deployments.", "Software Engineering", "code-2", "#ea580c", 90, "Very High", "Computer Science & Engineering, Information Technology"),
        ("AIML", "Artificial Intelligence & Generative AI", "From Python foundations and Deep Learning to Vector Databases, Transformers, and LLM RAG pipelines.", "AI & Data Science", "sparkles", "#f59e0b", 110, "Explosive", "Artificial Intelligence & Data Science, Computer Science & Engineering"),
        ("DEVOPS", "Cloud Native, DevOps & Site Reliability", "Build resilient CI/CD pipelines, Docker containers, Kubernetes clusters, and Terraform infrastructure.", "Cloud Infrastructure", "cloud", "#0ea5e9", 85, "High", "Computer Science & Engineering, Information Technology"),
        ("CYBER", "Cybersecurity & Ethical Penetration Testing", "Defensive network engineering, OWASP security, threat intelligence, and vulnerability remediation.", "Information Security", "shield-check", "#ef4444", 80, "Critical", "Computer Science & Engineering, Information Technology, Electronics & Communication"),
        ("APP", "Mobile App Development (Flutter & React Native)", "Cross-platform mobile applications, reactive state management, device hardware APIs, and store releases.", "Mobile Engineering", "smartphone", "#10b981", 75, "High", "Computer Science & Engineering, Information Technology"),
        ("EMBEDDED", "Embedded Systems, IoT & Robotics", "Master ARM Cortex, ESP32 microcontrollers, RTOS, sensor telemetry, PCB protocols, and ROS robotics.", "Hardware & IoT Systems", "cpu", "#06b6d4", 85, "Very High", "Electronics & Communication, Electrical & Electronics"),
        ("VLSI", "VLSI Design & Digital Verification", "Verilog HDL, FPGA prototyping, ASIC design flows, static timing analysis, and digital system design.", "Semiconductor & Chip Design", "microchip", "#8b5cf6", 95, "Very High", "Electronics & Communication"),
        ("EV_SMARTGRID", "Electric Vehicles (EV) & Smart Automation", "EV powertrains, Battery Management Systems (BMS), PLC automation, SCADA, and smart renewable grids.", "Power Tech & Automation", "zap", "#22c55e", 80, "High", "Electrical & Electronics")
    ]

    for code, title, tagline, cat, icon, color, hrs, demand, depts in new_tracks:
        cursor.execute("SELECT id FROM career_tracks WHERE code = ?", (code,))
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                UPDATE career_tracks 
                SET title = ?, tagline = ?, category = ?, icon = ?, badge_color = ?, estimated_hours = ?, demand_level = ?, departments = ?
                WHERE id = ?
            """, (title, tagline, cat, icon, color, hrs, demand, depts, row[0]))
        else:
            cursor.execute("""
                INSERT INTO career_tracks (code, title, tagline, category, icon, badge_color, estimated_hours, demand_level, departments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, title, tagline, cat, icon, color, hrs, demand, depts))

    conn.commit()

    # Map track codes to IDs
    cursor.execute("SELECT id, code FROM career_tracks")
    track_map = {r[1]: r[0] for r in cursor.fetchall()}

    # 4. Deduplicate modules:
    # Find canonical module for each (track_id, step_number)
    cursor.execute("SELECT id, track_id, step_number FROM modules ORDER BY id ASC")
    all_modules = cursor.fetchall()
    
    seen = {}
    id_remap = {} # duplicate_id -> canonical_id
    duplicate_ids = []

    for mid, tid, step in all_modules:
        key = (tid, step)
        if key not in seen:
            seen[key] = mid
        else:
            canonical_id = seen[key]
            id_remap[mid] = canonical_id
            duplicate_ids.append(mid)

    print(f"Found {len(duplicate_ids)} duplicate module entries to clean up.")

    # Re-map user_progress pointing to duplicate module IDs
    for dup_id, canon_id in id_remap.items():
        # Check if user already has record for canon_id
        cursor.execute("SELECT id, user_id FROM user_progress WHERE module_id = ?", (dup_id,))
        dup_progress = cursor.fetchall()
        for prog_id, uid in dup_progress:
            cursor.execute("SELECT id FROM user_progress WHERE user_id = ? AND module_id = ?", (uid, canon_id))
            canon_prog = cursor.fetchone()
            if canon_prog:
                # Merge or delete the duplicate progress entry
                cursor.execute("DELETE FROM user_progress WHERE id = ?", (prog_id,))
            else:
                cursor.execute("UPDATE user_progress SET module_id = ? WHERE id = ?", (canon_id, prog_id))

    # Now delete the duplicate modules
    if duplicate_ids:
        cursor.execute(f"DELETE FROM modules WHERE id IN ({','.join(map(str, duplicate_ids))})")
        print(f"Deleted duplicate modules: {duplicate_ids}")

    # 5. Insert modules for new tracks (EMBEDDED, VLSI, EV_SMARTGRID) if not present
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

    new_module_sets = embedded_modules + vlsi_modules + ev_modules
    for m in new_module_sets:
        cursor.execute("SELECT id FROM modules WHERE track_id = ? AND step_number = ?", (m[0], m[1]))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO modules (track_id, step_number, title, tier, description, key_skills, resources, project_prompt, checkpoints_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, m)
            print(f"Added module: {m[2]}")

    # 6. Quizzes deduplication and additions
    cursor.execute("SELECT id, track_id, title FROM quizzes ORDER BY id ASC")
    all_quizzes = cursor.fetchall()
    seen_q = {}
    dup_q = []
    for qid, tid, title in all_quizzes:
        key = (tid, title)
        if key not in seen_q:
            seen_q[key] = qid
        else:
            dup_q.append(qid)
    if dup_q:
        cursor.execute(f"DELETE FROM quizzes WHERE id IN ({','.join(map(str, dup_q))})")
        print(f"Deleted duplicate quizzes: {dup_q}")

    new_quizzes = [
        (track_map["EMBEDDED"], "Microcontroller Hardware Interrupts",
         "What happens when a high-priority hardware interrupt fires while the CPU is executing the main loop in an ARM Cortex-M?",
         '["The CPU crashes immediately", "The CPU pushes register context to the stack and jumps to the Interrupt Vector Handler", "The interrupt is permanently ignored until reboot", "The compiler converts the loop to C++"]', 1,
         "ARM Cortex-M hardware automatically saves the context (R0-R3, R12, LR, PC, xPSR) to the active stack and executes the ISR.", 25),
        
        (track_map["EMBEDDED"], "CAN Bus Arbitration",
         "How does CAN bus resolve collisions when two nodes transmit simultaneously?",
         '["First node to transmit always wins", "Non-destructive bitwise arbitration where the lower identifier (dominant 0) wins", "Both messages are corrupted and discarded", "The bus master chooses randomly"]', 1,
         "In CAN arbitration, dominant bits (0) overwrite recessive bits (1). The node with the lower message ID continues transmitting without interruption.", 25),

        (track_map["VLSI"], "Verilog Assignments",
         "Which assignment operator should be used for clocked sequential registers (flip-flops) in an always @(posedge clk) block in Verilog?",
         '["Blocking assignment (=)", "Non-blocking assignment (<=)", "Continuous assignment (assign)", "Pointer dereference (*)"]', 1,
         "Non-blocking assignments (<=) schedule evaluations concurrently, accurately modeling physical flip-flop clock edge registers and preventing simulation race conditions.", 25),

        (track_map["EV_SMARTGRID"], "BLDC Inverter Switching",
         "What is the role of Space Vector PWM (SVPWM) in an electric vehicle 3-phase motor inverter?",
         '["Increases battery pack voltage", "Maximizes DC bus voltage utilization and reduces motor current harmonic distortion", "Converts AC to DC", "Monitors tire pressure"]', 1,
         "SVPWM provides up to 15.5% higher DC bus voltage utilization than conventional sinusoidal PWM with lower total harmonic distortion (THD).", 25)
    ]

    for q in new_quizzes:
        cursor.execute("SELECT id FROM quizzes WHERE track_id = ? AND title = ?", (q[0], q[1]))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO quizzes (track_id, title, question, options_json, correct_index, explanation, points)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, q)

    # 7. Deduplicate interview flashcards
    cursor.execute("SELECT id, track_code, question FROM interview_flashcards ORDER BY id ASC")
    all_fc = cursor.fetchall()
    seen_fc = {}
    dup_fc = []
    for fid, code, q in all_fc:
        key = (code, q)
        if key not in seen_fc:
            seen_fc[key] = fid
        else:
            dup_fc.append(fid)
    if dup_fc:
        cursor.execute(f"DELETE FROM interview_flashcards WHERE id IN ({','.join(map(str, dup_fc))})")
        print(f"Deleted duplicate flashcards: {dup_fc}")

    new_flashcards = [
        ("EMBEDDED", "What is Priority Inversion in an RTOS, and how does Priority Inheritance solve it?",
         "Priority Inversion occurs when a low-priority task holds a shared resource (mutex) needed by a high-priority task, and a medium-priority task preempts the low-priority task, effectively blocking the high-priority task indefinitely. Priority Inheritance solves this by temporarily raising the priority of the low-priority task to match the high-priority task until it releases the mutex.", "Advanced", "RTOS Synchronization"),

        ("EMBEDDED", "Explain the difference between SPI and I2C protocols regarding speed, wire count, and arbitration.",
         "SPI is a 4-wire (MOSI, MISO, SCK, CS), full-duplex, master-slave protocol capable of high clock speeds (10-50+ MHz) without arbitration. I2C is a 2-wire (SDA, SCL), half-duplex, multi-master protocol with hardware addressing and clock stretching, typically running at 100 kHz to 3.4 MHz.", "Core", "Hardware Protocols"),

        ("VLSI", "Explain Setup Time and Hold Time violations in digital sequential design.",
         "Setup Time is the minimum time data must remain stable before the active clock edge. Hold Time is the minimum time data must remain stable after the active clock edge. Violating either causes metastability in the flip-flop. Setup violations are fixed by reducing combinational logic delay or slowing the clock. Hold violations are fixed by inserting delay buffers on the data path.", "Core", "Digital Timing Analysis"),

        ("EV_SMARTGRID", "Why is Cell Balancing essential in high-voltage EV Lithium-Ion battery packs?",
         "Due to manufacturing tolerances, cells have slightly different capacities and self-discharge rates. During charging, the weakest cell reaches maximum voltage first, stopping charging early; during discharge, it empties first, shutting down the pack. Active/passive cell balancing equalizes state of charge, maximizing usable battery range and preventing thermal overcharging.", "Core", "Battery Management Systems")
    ]

    for fc in new_flashcards:
        cursor.execute("SELECT id FROM interview_flashcards WHERE track_code = ? AND question = ?", (fc[0], fc[1]))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO interview_flashcards (track_code, question, answer, difficulty, key_concept)
                VALUES (?, ?, ?, ?, ?)
            """, fc)

    # 8. Deduplicate placements
    cursor.execute("SELECT id, company, role FROM placements ORDER BY id ASC")
    all_pl = cursor.fetchall()
    seen_pl = {}
    dup_pl = []
    for pid, comp, role in all_pl:
        key = (comp, role)
        if key not in seen_pl:
            seen_pl[key] = pid
        else:
            dup_pl.append(pid)
    if dup_pl:
        cursor.execute(f"DELETE FROM placements WHERE id IN ({','.join(map(str, dup_pl))})")
        print(f"Deleted duplicate placements: {dup_pl}")

    new_placements = [
        ("Texas Instruments", "Embedded Systems Engineer", "EMBEDDED", "₹ 15.0 - 18.5 LPA", "Super Dream", "Bengaluru", "C/C++, ARM Cortex, FreeRTOS, SPI/I2C/CAN, Hardware Debugging", "25 Nov 2026", "ECE / EEE with hardware projects", "https://careers.ti.com"),
        ("Intel Corporation", "VLSI Verification Engineer", "VLSI", "₹ 16.0 - 22.0 LPA", "Super Dream", "Bengaluru", "SystemVerilog, UVM, Verilog HDL, Static Timing Analysis", "30 Nov 2026", "ECE / EEE (70%+ aggregate)", "https://jobs.intel.com"),
        ("Ola Electric / Ather Energy", "EV Powertrain & BMS Engineer", "EV_SMARTGRID", "₹ 9.5 - 13.0 LPA", "Dream", "Bengaluru / Hosur", "Power Electronics, BMS, MATLAB/Simulink, CAN bus, Li-Ion testing", "02 Dec 2026", "EEE / Mechanical / ECE graduates", "https://careers.olaelectric.com")
    ]

    for pl in new_placements:
        cursor.execute("SELECT id FROM placements WHERE company = ? AND role = ?", (pl[0], pl[1]))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO placements (company, role, track_code, package_or_stipend, package_category, location, required_skills, deadline, eligibility, apply_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, pl)

    # 9. Update users preferred_track_id based on department
    dept_default_track = {
        "Electronics & Communication": track_map["EMBEDDED"],
        "Artificial Intelligence & Data Science": track_map["AIML"],
        "Artificial Intelligence & DS": track_map["AIML"],
        "Electrical & Electronics": track_map["EV_SMARTGRID"],
        "Information Technology": track_map["FSD"],
        "Computer Science & Engineering": track_map["FSD"]
    }

    cursor.execute("SELECT id, department, preferred_track_id FROM users")
    users = cursor.fetchall()
    for uid, dept, pref_id in users:
        if not pref_id:
            target_track = dept_default_track.get(dept, track_map["FSD"])
            cursor.execute("UPDATE users SET preferred_track_id = ? WHERE id = ?", (target_track, uid))
            print(f"Set preferred_track_id={target_track} for user ID {uid} ({dept})")

    # 10. Student Portfolio Migration & Seeding
    cursor.execute("PRAGMA table_info(users);")
    curr_user_cols = [c[1] for c in cursor.fetchall()]
    portfolio_columns = [
        ("tagline", "TEXT DEFAULT 'Computer Science Student, Python Developer & Robotics Enthusiast'"),
        ("bio", "TEXT"),
        ("github_url", "TEXT DEFAULT 'https://github.com/ismrs-tech'"),
        ("linkedin_url", "TEXT DEFAULT 'https://linkedin.com/in/pydah-student'"),
        ("location", "TEXT DEFAULT 'Kakinada, Andhra Pradesh, India'"),
        ("phone", "TEXT DEFAULT '+91 98765 43210'"),
        ("custom_skills", "TEXT DEFAULT 'Python, Flask, JavaScript, React, REST APIs, SQLite, Machine Learning, Robotics & IoT, Git & GitHub, Embedded C, Docker'"),
        ("experience_json", "TEXT DEFAULT '[]'"),
        ("profile_image_url", "TEXT DEFAULT '/static/images/student_avatar.jpg'")
    ]
    for col_name, col_def in portfolio_columns:
        if col_name not in curr_user_cols:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def};")
            print(f"Added {col_name} column to users table.")

    # Seed rich portfolio for demo student (Venkata Sai Teja)
    demo_bio = (
        "Passionate Computer Science diploma / B.Tech student specializing in Python development, "
        "Artificial Intelligence, Machine Learning, Robotics, and IoT. Building innovative embedded systems "
        "and intelligent software solutions to solve real-world problems. Experienced in mentoring students "
        "in STEM innovations, hands-on microcontrollers, and full-stack software development at Pydah Educational Academy."
    )
    demo_exp = json.dumps([
        {
            "role": "ATL Trainer | Robotics, IoT & AI/ML Instructor",
            "organization": "Atal Tinkering Lab / Pydah Innovation Cell",
            "period": "2025 - Present",
            "description": "Conduct Robotics, IoT, AI, and Machine Learning training sessions for students. Teach Python programming, Arduino, sensors, and embedded systems through hands-on practical demonstrations."
        },
        {
            "role": "Full Stack & Embedded Systems Lead",
            "organization": "Pydah Student Developer Community",
            "period": "2024 - 2025",
            "description": "Built and deployed cloud-connected IoT prototypes and full-stack web applications. Led capstone project development and technical workshops."
        },
        {
            "role": "Diploma / B.Tech in Computer Science & Engineering",
            "organization": "Pydah Group of Institutions, Kakinada",
            "period": "2023 - 2026",
            "description": "Focusing on software development, data structures, algorithms, microcontrollers, digital electronics, and cloud native architectures."
        }
    ])

    cursor.execute("""
        UPDATE users 
        SET tagline = COALESCE(tagline, 'Computer Science Student, Python Developer & Robotics Enthusiast'),
            bio = COALESCE(bio, ?),
            github_url = COALESCE(github_url, 'https://github.com/ismrs-tech'),
            linkedin_url = COALESCE(linkedin_url, 'https://linkedin.com/in/pydah-student'),
            location = COALESCE(location, 'Kakinada, Andhra Pradesh, India'),
            phone = COALESCE(phone, '+91 98765 43210'),
            custom_skills = COALESCE(custom_skills, 'Python, Flask, JavaScript, React, REST APIs, SQLite, Machine Learning, Robotics & IoT, Git & GitHub, Embedded C, Docker'),
            experience_json = CASE WHEN experience_json IS NULL OR experience_json = '[]' THEN ? ELSE experience_json END,
            profile_image_url = COALESCE(profile_image_url, '/static/images/student_avatar.jpg')
        WHERE LOWER(email) = 'student@pydah.edu.in'
    """, (demo_bio, demo_exp))

    # Add showcase projects matching reference portfolio for student 1
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = 'student@pydah.edu.in'")
    student_row = cursor.fetchone()
    if student_row:
        student_id = student_row[0]
        fsd_track_id = track_map.get("FSD", 1)
        embedded_track_id = track_map.get("EMBEDDED", fsd_track_id)
        aiml_track_id = track_map.get("AIML", fsd_track_id)

        showcase_projects = [
            (student_id, aiml_track_id, "BRIGHTER – AI Voice Assistant", "Intelligent desktop voice assistant listening to voice commands, executing desktop tasks, launching web applications, and responding via speech synthesis.", "Python, SpeechRecognition, Pyttsx3, OS Automation", "https://github.com/ismrs-tech/brighter-ai-assistant", "https://ismrs-tech.github.io/ismrs-portfolio/#projects", "Verified & Approved", "Verified by Pydah Innovation Cell. Excellent speech processing pipeline."),
            (student_id, embedded_track_id, "RFID Automatic Toll Gate System", "Automated toll collection system identifying authorized RFID cards, automatically opening servo barrier gates, and displaying status on 16x2 LCD display.", "Arduino C++, RFID RC522, Servo Actuator, I2C LCD", "https://github.com/ismrs-tech/rfid-toll-gate", "https://ismrs-tech.github.io/ismrs-portfolio/#projects", "Verified & Approved", "Verified by Pydah Innovation Cell. Outstanding hardware circuit design."),
            (student_id, embedded_track_id, "Fire Alarm & Detection Safety System", "Real-time safety system monitoring flame and smoke levels continuously, triggering immediate loud buzzer alerts and LED status for laboratory and residential protection.", "Embedded C, Flame Sensor, MQ-2 Smoke Sensor, Buzzer", "https://github.com/ismrs-tech/fire-alarm-system", "https://ismrs-tech.github.io/ismrs-portfolio/#projects", "Verified & Approved", "Verified by Pydah Innovation Cell. Critical safety IoT implementation."),
            (student_id, embedded_track_id, "Smart Electronic Door Lock", "Secure access control system providing keyless electronic authentication via RFID/Keypad input and automated servo motor door deadbolt actuation.", "Arduino, RC522, Servo, 4x4 Matrix Keypad, EEPROM", "https://github.com/ismrs-tech/smart-door-lock", "https://ismrs-tech.github.io/ismrs-portfolio/#projects", "Verified & Approved", "Verified by Pydah Innovation Cell. Clean security architecture."),
            (student_id, aiml_track_id, "Intelligent Python Desktop Chatbot", "Conversational desktop chatbot built in Python capable of understanding user queries, processing input intent with NLP pattern matching, and offering assistance.", "Python, NLTK, Tkinter GUI, JSON Knowledge Base", "https://github.com/ismrs-tech/python-chatbot", "https://ismrs-tech.github.io/ismrs-portfolio/#projects", "Verified & Approved", "Verified by Pydah Innovation Cell. Good modular intent parser."),
            (student_id, fsd_track_id, "Pydah Smart Campus Resource Tracker", "Production full-stack web application for automated laboratory inventory and equipment checkout across engineering departments.", "Python, Flask, SQLite, Vanilla CSS, Chart.js", "https://github.com/ismrs-tech/pydah-skillpath-project", "http://127.0.0.1:5000", "Verified & Approved", "Verified by Pydah Innovation Cell. Excellent full-stack implementation.")
        ]

        for p in showcase_projects:
            cursor.execute("SELECT id FROM projects WHERE user_id = ? AND title = ?", (p[0], p[2]))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO projects (user_id, track_id, title, summary, tech_stack, github_url, live_demo_url, status, endorsement_remarks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, p)
                print(f"Added showcase project: {p[2]}")

    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()
    print("Migration and deduplication completed successfully!")

if __name__ == "__main__":
    migrate()
