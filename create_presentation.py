import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen standard
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    COLOR_BG_DARK = RGBColor(11, 19, 40)        # Deep Navy / Obsidian
    COLOR_BG_CARD = RGBColor(20, 32, 60)        # Card surface
    COLOR_ORANGE = RGBColor(234, 88, 12)        # Pydah Orange
    COLOR_ORANGE_LIGHT = RGBColor(249, 115, 22)  # Bright Orange
    COLOR_GOLD = RGBColor(245, 158, 11)         # Gold / Amber
    COLOR_WHITE = RGBColor(255, 255, 255)       # Pure White
    COLOR_MUTED = RGBColor(160, 174, 192)       # Slate Gray
    COLOR_ACCENT_GREEN = RGBColor(16, 185, 129) # Emerald Green

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide, color=COLOR_BG_DARK):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="PYDAH SKILLPATH"):
        # Header banner line
        accent_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.6), Inches(0.12), Inches(0.85))
        accent_bar.fill.solid()
        accent_bar.fill.fore_color.rgb = COLOR_ORANGE
        accent_bar.line.fill.background()

        tb = slide.shapes.add_textbox(Inches(1.1), Inches(0.55), Inches(11), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        
        # Category sub
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_GOLD
        
        # Main Title
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE

    # ----------------------------------------------------
    # SLIDE 1: TITLE & TEAM MEMBERS
    # ----------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, COLOR_BG_DARK)

    # Decorative top badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.8), Inches(4.2), Inches(0.5))
    badge.fill.solid()
    badge.fill.fore_color.rgb = COLOR_BG_CARD
    badge.line.color.rgb = COLOR_ORANGE
    badge.line.width = Pt(1)
    b_tf = badge.text_frame
    b_tf.text = "PYDAH EDUCATIONAL ACADEMY"
    b_tf.paragraphs[0].font.size = Pt(12)
    b_tf.paragraphs[0].font.bold = True
    b_tf.paragraphs[0].font.color.rgb = COLOR_GOLD
    b_tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Project Title
    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(2.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p1 = tf1.paragraphs[0]
    p1.text = "PYDAH SkillPath"
    p1.font.size = Pt(48)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_ORANGE_LIGHT

    p2 = tf1.add_paragraph()
    p2.text = "Career Pathways, Skill Validation & Placement Acceleration Platform"
    p2.font.size = Pt(22)
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = "A full-stack, student-centric ecosystem designed to master industry-ready tech stacks and fast-track campus recruitments."
    p3.font.size = Pt(14)
    p3.font.color.rgb = COLOR_MUTED
    p3.space_before = Pt(6)

    # Team Members Card
    card_w = Inches(11.33)
    card_h = Inches(2.3)
    team_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(4.3), card_w, card_h)
    team_card.fill.solid()
    team_card.fill.fore_color.rgb = COLOR_BG_CARD
    team_card.line.color.rgb = COLOR_ORANGE
    team_card.line.width = Pt(1.5)

    tc_tf = team_card.text_frame
    tc_tf.word_wrap = True
    
    tc_p = tc_tf.paragraphs[0]
    tc_p.text = "PROJECT DEVELOPMENT TEAM"
    tc_p.font.size = Pt(13)
    tc_p.font.bold = True
    tc_p.font.color.rgb = COLOR_GOLD
    tc_p.space_after = Pt(10)

    members = [
        "1. I. Sirumanirajasree",
        "2. J. Veera Rishitha",
        "3. K. Srimahalakshmi",
        "4. N. Trilokesh"
    ]
    
    # 2x2 grid for team members
    for i, m in enumerate(members):
        col = i % 2
        row = i // 2
        col_x = Inches(1.4) if col == 0 else Inches(6.8)
        row_y = Inches(5.1) if row == 0 else Inches(5.8)
        
        m_box = s1.shapes.add_textbox(col_x, row_y, Inches(5.0), Inches(0.6))
        m_tf = m_box.text_frame
        m_p = m_tf.paragraphs[0]
        m_p.text = m
        m_p.font.size = Pt(16)
        m_p.font.bold = True
        m_p.font.color.rgb = COLOR_WHITE

    # ----------------------------------------------------
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # ----------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "The Core Engineering & Placement Challenge", "Problem Statement")

    probs = [
        ("Curriculum vs Industry Disconnect", 
         "Standard academic syllabi rarely keep pace with fast-evolving industry requirements like Cloud DevOps, GenAI RAG pipelines, and modern full-stack architectures demanded by TCS Prime and AWS.",
         COLOR_ORANGE),
        ("Unstructured Student Learning", 
         "Students frequently get overwhelmed by fragmented tutorials, leading to burnout without measurable milestone progression or hands-on repository proofs.",
         COLOR_GOLD),
        ("Placement Directorate Verification Bottleneck", 
         "College placement officers face difficulty evaluating student project authenticity and technical readiness before forwarding candidate batches to tier-1 recruiters.",
         COLOR_ACCENT_GREEN)
    ]

    for idx, (title, desc, color) in enumerate(probs):
        box_y = Inches(1.8 + idx * 1.7)
        box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), box_y, Inches(11.7), Inches(1.4))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_BG_CARD
        box.line.color.rgb = color
        box.line.width = Pt(1)

        btf = box.text_frame
        btf.word_wrap = True
        bp1 = btf.paragraphs[0]
        bp1.text = f"❌  {title}"
        bp1.font.size = Pt(17)
        bp1.font.bold = True
        bp1.font.color.rgb = color

        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.size = Pt(13)
        bp2.font.color.rgb = COLOR_WHITE
        bp2.space_before = Pt(4)

    # ----------------------------------------------------
    # SLIDE 3: PROPOSED SOLUTION (PYDAH SKILLPATH)
    # ----------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "PYDAH SkillPath: The Unified Career Ecosystem", "Proposed Solution")

    pillars = [
        ("Interactive Roadmaps", "Step-by-step visual career blueprints with granular sub-topic checkpoints for self-paced progress tracking.", COLOR_ORANGE),
        ("Gamified Karma XP", "Continuous learning incentives rewarding completed modules (+100 XP), quizzes (+150 XP), and verified projects (+200 XP).", COLOR_GOLD),
        ("Placement Radar", "Automated skill-matching matching student completed competencies directly with high-package placement drives (> ₹7 - 16 LPA).", COLOR_ACCENT_GREEN),
        ("Verified Credentials", "Cryptographically verifiable Skill Passport & ATS-friendly resume export empowering students with ready-to-use application assets.", RGBColor(14, 165, 233))
    ]

    for idx, (title, desc, color) in enumerate(pillars):
        col = idx % 2
        row = idx // 2
        bx = Inches(0.8 + col * 5.9)
        by = Inches(1.8 + row * 2.6)

        cbox = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, by, Inches(5.6), Inches(2.3))
        cbox.fill.solid()
        cbox.fill.fore_color.rgb = COLOR_BG_CARD
        cbox.line.color.rgb = color
        cbox.line.width = Pt(1.5)

        c_tf = cbox.text_frame
        c_tf.word_wrap = True
        cp1 = c_tf.paragraphs[0]
        cp1.text = f"✨ {title}"
        cp1.font.size = Pt(18)
        cp1.font.bold = True
        cp1.font.color.rgb = color

        cp2 = c_tf.add_paragraph()
        cp2.text = desc
        cp2.font.size = Pt(14)
        cp2.font.color.rgb = COLOR_WHITE
        cp2.space_before = Pt(8)

    # ----------------------------------------------------
    # SLIDE 4: SPECIALIZED CAREER TRACKS
    # ----------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "5 Industry-Aligned Engineering Roadmaps", "Curriculum Pathways")

    tracks = [
        ("Full Stack & Cloud Architect (FSD)", "HTML5/CSS3 Layouts, ES6+, Flask REST APIs, Relational SQL (3NF), Auth/OWASP, Docker Containers & Cloud Deployment.", "Very High Demand • 90 Hours"),
        ("Artificial Intelligence & GenAI (AIML)", "Data Science with Pandas/NumPy, Applied Scikit-Learn ML, PyTorch Deep Learning, Vector DBs, and LLM RAG Pipelines.", "Explosive Growth • 110 Hours"),
        ("Cloud Native, DevOps & SRE (DEVOPS)", "Linux CLI Administration, Bash Scripting, GitOps & GitHub Actions CI/CD, Kubernetes Clusters & Terraform IaC.", "High Demand • 85 Hours"),
        ("Cybersecurity & Penetration Testing", "TCP/IP Handshakes, Wireshark Packet Inspection, Nmap Scanning, OWASP Top 10 Exploitation & Burp Suite Auditing.", "Critical Sector • 80 Hours"),
        ("Mobile App Development (Flutter/React Native)", "Dart OOP, Reactive Widget Trees, Material 3 Layouts, Riverpod State Management & Offline SQLite Storage.", "High Demand • 75 Hours")
    ]

    for idx, (tname, tdesc, tmeta) in enumerate(tracks):
        by = Inches(1.7 + idx * 1.05)
        rbox = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), by, Inches(11.7), Inches(0.95))
        rbox.fill.solid()
        rbox.fill.fore_color.rgb = COLOR_BG_CARD
        rbox.line.color.rgb = COLOR_ORANGE if idx == 0 else COLOR_BG_DARK
        rbox.line.width = Pt(1)

        rtf = rbox.text_frame
        rtf.word_wrap = True
        rp1 = rtf.paragraphs[0]
        rp1.text = f"{idx+1}. {tname}  [{tmeta}]"
        rp1.font.size = Pt(14)
        rp1.font.bold = True
        rp1.font.color.rgb = COLOR_GOLD if idx == 0 else COLOR_WHITE

        rp2 = rtf.add_paragraph()
        rp2.text = tdesc
        rp2.font.size = Pt(11)
        rp2.font.color.rgb = COLOR_MUTED

    # ----------------------------------------------------
    # SLIDE 5: SYSTEM ARCHITECTURE & DATA FLOW
    # ----------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "High-Performance Full-Stack Architecture", "System Architecture")

    layers = [
        ("Presentation Layer (Client SPA)", "• Single Page Application (Vanilla HTML5/CSS3/ES6+)\n• Dynamic Reactive UI (Tabs, Modals, Checklists)\n• Lucide Vector Icons & Circular Radial SVG Gauges\n• Specialized Landscape A4 Print Stylesheets", COLOR_ORANGE),
        ("Application & API Layer (Server)", "• Python 3.11+ / 3.14 Runtime\n• Flask WSGI Microframework & RESTful Endpoints\n• Werkzeug PBKDF2/Scrypt Password Encryption\n• Session Authentication & Zero External NPM Bloat", COLOR_GOLD),
        ("Persistence Layer (Relational DB)", "• SQLite 3 Zero-Config Embedded Engine\n• Strict PRAGMA foreign_keys = ON & Constraints\n• Atomic Upserts (ON CONFLICT DO UPDATE)\n• Tables: Users, Tracks, Checkpoints, Quizzes, Placements", COLOR_ACCENT_GREEN)
    ]

    for idx, (lname, ldetails, lcolor) in enumerate(layers):
        bx = Inches(0.8 + idx * 3.9)
        lbox = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, Inches(1.8), Inches(3.7), Inches(5.0))
        lbox.fill.solid()
        lbox.fill.fore_color.rgb = COLOR_BG_CARD
        lbox.line.color.rgb = lcolor
        lbox.line.width = Pt(1.5)

        ltf = lbox.text_frame
        ltf.word_wrap = True
        lp1 = ltf.paragraphs[0]
        lp1.text = lname
        lp1.font.size = Pt(15)
        lp1.font.bold = True
        lp1.font.color.rgb = lcolor
        lp1.space_after = Pt(14)

        lp2 = ltf.add_paragraph()
        lp2.text = ldetails
        lp2.font.size = Pt(13)
        lp2.font.color.rgb = COLOR_WHITE
        lp2.line_spacing = 1.3

    # ----------------------------------------------------
    # SLIDE 6: FORMULAS & ALGORITHMS
    # ----------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Analytical Metrics: Readiness & Placement Matching", "Algorithms & Metrics")

    algos = [
        ("1. Career Readiness Index (CRI)",
         "Formula:\nReadiness % = Min( 99,  38 + (Completed Modules × 7) + (Quizzes Passed × 12) + (Approved Projects × 8) )\n\nPurpose:\nCombines theoretical baseline (38%) with practical execution (modules & projects) to benchmark student eligibility against tier-1 companies (TCS Prime, AWS).",
         COLOR_ORANGE),
        ("2. Skill Karma XP (Gamification)",
         "Formula:\nTotal Karma XP = Base (500) + (Modules × 100 XP) + (Quizzes × 150 XP) + (Projects × 200 XP)\n\nPurpose:\nPowers the Campus Leaderboard with podium medals (🥇 🥈 🥉) to recognize top student talent and motivate daily consistent practice.",
         COLOR_GOLD),
        ("3. Placement Radar Match Percentage",
         "Formula:\nMatch % = Max( 40,  Min( 98,  (Matched Skills / Total Drive Required Skills × 80) + 20 ) )\n\nPurpose:\nPerforms real-time string token matching comparing candidate verified skills with company job eligibility criteria.",
         COLOR_ACCENT_GREEN)
    ]

    for idx, (atitle, adesc, acolor) in enumerate(algos):
        bx = Inches(0.8 + idx * 3.9)
        abox = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, Inches(1.8), Inches(3.7), Inches(5.0))
        abox.fill.solid()
        abox.fill.fore_color.rgb = COLOR_BG_CARD
        abox.line.color.rgb = acolor
        abox.line.width = Pt(1.5)

        atf = abox.text_frame
        atf.word_wrap = True
        ap1 = atf.paragraphs[0]
        ap1.text = atitle
        ap1.font.size = Pt(15)
        ap1.font.bold = True
        ap1.font.color.rgb = acolor
        ap1.space_after = Pt(12)

        ap2 = atf.add_paragraph()
        ap2.text = adesc
        ap2.font.size = Pt(12)
        ap2.font.color.rgb = COLOR_WHITE
        ap2.line_spacing = 1.25

    # ----------------------------------------------------
    # SLIDE 7: KEY INNOVATIONS IMPLEMENTED
    # ----------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Feature Highlights & Campus Innovations", "System Highlights")

    innovations = [
        ("Granular Sub-Checkpoints", "Module competencies are broken into micro-tasks (e.g. Flexbox, Grid, Media Queries) that calculate real-time completion in SQLite.", COLOR_ORANGE),
        ("Technical Interview Flashcards", "Dedicated interview arena featuring actual screening questions asked by TCS Prime, AWS, Cognizant, and Qualcomm with 1-click reveal answers.", COLOR_GOLD),
        ("Self-Service Password Reset", "100% direct password recovery without faculty bottlenecks, securely updating Werkzeug password hashes.", COLOR_ACCENT_GREEN),
        ("Placement Radar Filters", "Filter drives by Package Tier (Super Dream > 10 LPA, Dream > 7 LPA, Standard) and Location (Hyderabad, Vizag, Bengaluru).", RGBColor(14, 165, 233)),
        ("ATS Resume Generator", "1-click export compiling student verified proficiencies and capstone repositories into an ATS-friendly bulleted block for easy resume copy-pasting.", RGBColor(168, 85, 247)),
        ("Royal Academic Diploma", "Official verified skill certificate with Royal Parchment and Midnight Obsidian themes, gold wax seal, and 1-page A4 print optimization.", RGBColor(244, 63, 94))
    ]

    for idx, (ititle, idesc, icolor) in enumerate(innovations):
        col = idx % 3
        row = idx // 3
        bx = Inches(0.8 + col * 3.9)
        by = Inches(1.8 + row * 2.6)

        ibox = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, by, Inches(3.7), Inches(2.35))
        ibox.fill.solid()
        ibox.fill.fore_color.rgb = COLOR_BG_CARD
        ibox.line.color.rgb = icolor
        ibox.line.width = Pt(1.5)

        itf = ibox.text_frame
        itf.word_wrap = True
        ip1 = itf.paragraphs[0]
        ip1.text = f"🔹 {ititle}"
        ip1.font.size = Pt(15)
        ip1.font.bold = True
        ip1.font.color.rgb = icolor

        ip2 = itf.add_paragraph()
        ip2.text = idesc
        ip2.font.size = Pt(12)
        ip2.font.color.rgb = COLOR_WHITE
        ip2.space_before = Pt(6)

    # ----------------------------------------------------
    # SLIDE 8: TESTING, SECURITY & VALIDATION
    # ----------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Verification & Enterprise Security Standards", "Quality & Testing")

    tests = [
        ("Authentication & Password Encryption", "Tested with Werkzeug PBKDF2:SHA256 salted hashes. Passwords are never stored in plain text. Verified session-based role authorization (student vs admin)."),
        ("Idempotent Checkpoint Progress", "Verified atomic database transactions using SQLite `ON CONFLICT(user_id, module_id) DO UPDATE` to prevent race conditions during rapid clicking."),
        ("Placement Tier Filter Precision", "Verified API queries filtering by salary bracket (`Super Dream`, `Dream`) and regional hiring locations with 0ms latency."),
        ("One-Page Landscape A4 Print Validation", "Tested `@page { size: landscape A4; margin: 8mm; }` ensuring zero multi-page spillover when exporting official diploma certificates to PDF.")
    ]

    for idx, (ttitle, tdesc) in enumerate(tests):
        by = Inches(1.8 + idx * 1.3)
        tbox = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), by, Inches(11.7), Inches(1.15))
        tbox.fill.solid()
        tbox.fill.fore_color.rgb = COLOR_BG_CARD
        tbox.line.color.rgb = COLOR_ACCENT_GREEN
        tbox.line.width = Pt(1)

        ttf = tbox.text_frame
        ttf.word_wrap = True
        tp1 = ttf.paragraphs[0]
        tp1.text = f"✅  {ttitle}"
        tp1.font.size = Pt(15)
        tp1.font.bold = True
        tp1.font.color.rgb = COLOR_ACCENT_GREEN

        tp2 = ttf.add_paragraph()
        tp2.text = tdesc
        tp2.font.size = Pt(12)
        tp2.font.color.rgb = COLOR_WHITE
        tp2.space_before = Pt(4)

    # ----------------------------------------------------
    # SLIDE 9: DEPLOYMENT & PRODUCTION READINESS
    # ----------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Deployment Strategy & Cloud Deliverables", "Production Readiness")

    deploys = [
        ("Containerized Dockerfile", "Built with lightweight `python:3.11-slim`, non-root security (`pydahuser`), Gunicorn concurrency (`--workers 2 --threads 4`), and container healthchecks.", COLOR_ORANGE),
        ("Dynamic Port Cloud WSGI", "Procfile configured with `gunicorn app:app --bind 0.0.0.0:$PORT` for instant 1-click deployment on Render, Railway, or Heroku.", COLOR_GOLD),
        ("Local One-Click Launcher", "`run.bat` allows any faculty or student to start the platform immediately on Windows without touching command-line configurations.", COLOR_ACCENT_GREEN)
    ]

    for idx, (dtitle, ddesc, dcolor) in enumerate(deploys):
        by = Inches(1.8 + idx * 1.7)
        dbox = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), by, Inches(11.7), Inches(1.4))
        dbox.fill.solid()
        dbox.fill.fore_color.rgb = COLOR_BG_CARD
        dbox.line.color.rgb = dcolor
        dbox.line.width = Pt(1.5)

        dtf = dbox.text_frame
        dtf.word_wrap = True
        dp1 = dtf.paragraphs[0]
        dp1.text = f"🚀  {dtitle}"
        dp1.font.size = Pt(17)
        dp1.font.bold = True
        dp1.font.color.rgb = dcolor

        dp2 = dtf.add_paragraph()
        dp2.text = ddesc
        dp2.font.size = Pt(13)
        dp2.font.color.rgb = COLOR_WHITE
        dp2.space_before = Pt(6)

    # ----------------------------------------------------
    # SLIDE 10: CONCLUSION & TEAM ACKNOWLEDGEMENT
    # ----------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)

    tbox_c = s10.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.33), Inches(1.5))
    tf_c = tbox_c.text_frame
    tf_c.word_wrap = True
    cp_c1 = tf_c.paragraphs[0]
    cp_c1.text = "Thank You!"
    cp_c1.font.size = Pt(44)
    cp_c1.font.bold = True
    cp_c1.font.color.rgb = COLOR_ORANGE_LIGHT
    cp_c1.alignment = PP_ALIGN.CENTER

    cp_c2 = tf_c.add_paragraph()
    cp_c2.text = "Empowering Students • Engineering Futures • Fast-Tracking Careers"
    cp_c2.font.size = Pt(18)
    cp_c2.font.color.rgb = COLOR_WHITE
    cp_c2.alignment = PP_ALIGN.CENTER
    cp_c2.space_before = Pt(8)

    # Final Team Box
    f_card = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(3.2), Inches(9.33), Inches(3.2))
    f_card.fill.solid()
    f_card.fill.fore_color.rgb = COLOR_BG_CARD
    f_card.line.color.rgb = COLOR_GOLD
    f_card.line.width = Pt(2)

    ftf = f_card.text_frame
    ftf.word_wrap = True
    ftp = ftf.paragraphs[0]
    ftp.text = "PYDAH SkillPath Project Team"
    ftp.font.size = Pt(18)
    ftp.font.bold = True
    ftp.font.color.rgb = COLOR_GOLD
    ftp.alignment = PP_ALIGN.CENTER
    ftp.space_after = Pt(16)

    for m in members:
        mp = ftf.add_paragraph()
        mp.text = m
        mp.font.size = Pt(15)
        mp.font.color.rgb = COLOR_WHITE
        mp.alignment = PP_ALIGN.CENTER
        mp.space_before = Pt(6)

    # Save presentation file
    output_path = os.path.join(os.path.dirname(__file__), "PYDAH_SkillPath_Project_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    create_deck()
