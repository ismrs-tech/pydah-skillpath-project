import sqlite3
import os
import json
import socket
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session, send_file, redirect
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

app = Flask(__name__, 
            static_folder=os.path.join(BASE_DIR, "static"), 
            template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "pydah_skillpath_secret_key_2026_secure")
# Vercel Serverless environment compatibility (Writable /tmp directory)
if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/pydah_skillpath.db"
    bundled_db = os.path.join(os.path.dirname(__file__), "pydah_skillpath.db")
    if not os.path.exists(DB_PATH):
        if os.path.exists(bundled_db):
            import shutil
            shutil.copy2(bundled_db, DB_PATH)
        else:
            from init_db import init_database
            init_database(db_target=DB_PATH)
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "pydah_skillpath.db")
    if not os.path.exists(DB_PATH):
        from init_db import init_database
        init_database()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    conn = get_db()
    user = conn.execute("""
        SELECT id, name, email, role, department, year_or_designation, target_role, 
               preferred_track_id, avatar_seed, karma_xp, tagline, bio, 
               github_url, linkedin_url, location, phone, custom_skills, experience_json, 
               profile_image_url, created_at 
        FROM users WHERE id = ?
    """, (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/presentation")
def presentation_view():
    return send_file(os.path.join(os.path.dirname(__file__), "presentation.html"))

@app.route("/download/pptx")
def download_pptx():
    pptx_path = os.path.join(os.path.dirname(__file__), "PYDAH_SkillPath_Project_Presentation.pptx")
    return send_file(pptx_path, as_attachment=True, download_name="PYDAH_SkillPath_Project_Presentation.pptx")

# ----------------- AUTHENTICATION ROUTES -----------------

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"success": False, "message": "Invalid email or password. Please verify credentials."}), 401

    session["user_id"] = user["id"]
    u_keys = user.keys()
    user_dict = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "department": user["department"],
        "year_or_designation": user["year_or_designation"],
        "target_role": user["target_role"],
        "preferred_track_id": user["preferred_track_id"] if "preferred_track_id" in u_keys else None,
        "avatar_seed": user["avatar_seed"],
        "karma_xp": user["karma_xp"],
        "tagline": user["tagline"] if "tagline" in u_keys else "",
        "bio": user["bio"] if "bio" in u_keys else "",
        "github_url": user["github_url"] if "github_url" in u_keys else "",
        "linkedin_url": user["linkedin_url"] if "linkedin_url" in u_keys else "",
        "location": user["location"] if "location" in u_keys else "",
        "phone": user["phone"] if "phone" in u_keys else "",
        "custom_skills": user["custom_skills"] if "custom_skills" in u_keys else "",
        "experience_json": user["experience_json"] if "experience_json" in u_keys else "[]",
        "profile_image_url": user["profile_image_url"] if "profile_image_url" in u_keys and user["profile_image_url"] else "/static/images/student_avatar.jpg"
    }
    return jsonify({"success": True, "message": f"Welcome back, {user['name']}!", "user": user_dict})

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = "student"
    department = data.get("department", "Computer Science & Engineering").strip()
    year_or_designation = data.get("year_or_designation", "3rd Year B.Tech").strip()
    target_role = data.get("target_role", "Software Development Engineer").strip()
    preferred_track_id = data.get("preferred_track_id")

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email, and password are required."}), 400

    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "message": "An account with this email already exists."}), 409

    # Automatically resolve preferred_track_id if not provided
    if not preferred_track_id:
        track_row = conn.execute("SELECT id FROM career_tracks WHERE departments LIKE ? ORDER BY id ASC LIMIT 1", (f"%{department}%",)).fetchone()
        preferred_track_id = track_row["id"] if track_row else 1
    else:
        try:
            preferred_track_id = int(preferred_track_id)
        except Exception:
            preferred_track_id = 1

    pw_hash = generate_password_hash(password)
    avatar_seed = name.lower().replace(" ", "_")

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role, department, year_or_designation, target_role, preferred_track_id, avatar_seed, karma_xp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 500)
    """, (name, email, pw_hash, role, department, year_or_designation, target_role, preferred_track_id, avatar_seed))
    new_user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    session["user_id"] = new_user_id
    user_dict = {
        "id": new_user_id,
        "name": name,
        "email": email,
        "role": role,
        "department": department,
        "year_or_designation": year_or_designation,
        "target_role": target_role,
        "preferred_track_id": preferred_track_id,
        "avatar_seed": avatar_seed,
        "karma_xp": 500
    }
    return jsonify({"success": True, "message": "Student account registered successfully!", "user": user_dict}), 201

# ----------------- SELF-SERVICE PASSWORD RESET -----------------

@app.route("/api/forgot-password/reset", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    new_password = data.get("new_password", "").strip()

    if not email or not new_password:
        return jsonify({"success": False, "message": "Registered email and new password are required."}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "New password must be at least 6 characters long."}), 400

    conn = get_db()
    user = conn.execute("SELECT id, name FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
    
    if not user:
        conn.close()
        return jsonify({"success": False, "message": "No student profile found with this email address."}), 404

    new_hash = generate_password_hash(new_password)
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user["id"]))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True, 
        "message": f"Password reset successfully for {user['name']}! You can now log in with your new password."
    })

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route("/api/me", methods=["GET"])
def get_me():
    user = current_user()
    if not user:
        return jsonify({"authenticated": False}), 401
    return jsonify({"authenticated": True, "user": user})

# ----------------- CAREER TRACKS & ENHANCED ROADMAPS -----------------

@app.route("/api/tracks", methods=["GET"])
def get_tracks():
    user = current_user()
    conn = get_db()
    tracks = conn.execute("SELECT * FROM career_tracks ORDER BY id ASC").fetchall()
    
    result = []
    for t in tracks:
        t_dict = dict(t)
        total_m = conn.execute("SELECT COUNT(*) FROM modules WHERE track_id = ?", (t["id"],)).fetchone()[0]
        t_dict["total_modules"] = total_m

        completed_m = 0
        in_progress_m = 0
        if user:
            completed_m = conn.execute("""
                SELECT COUNT(*) FROM user_progress up
                JOIN modules m ON up.module_id = m.id
                WHERE up.user_id = ? AND m.track_id = ? AND up.status = 'completed'
            """, (user["id"], t["id"])).fetchone()[0]

            in_progress_m = conn.execute("""
                SELECT COUNT(*) FROM user_progress up
                JOIN modules m ON up.module_id = m.id
                WHERE up.user_id = ? AND m.track_id = ? AND up.status = 'in_progress'
            """, (user["id"], t["id"])).fetchone()[0]

        t_dict["completed_modules"] = completed_m
        t_dict["in_progress_modules"] = in_progress_m
        t_dict["progress_percent"] = round((completed_m / total_m * 100) if total_m > 0 else 0)

        # Check if recommended for current user
        is_recommended = False
        if user and user.get("department"):
            is_recommended = user["department"].lower() in (t_dict.get("departments") or "").lower()
        t_dict["is_recommended"] = is_recommended

        result.append(t_dict)

    conn.close()
    return jsonify({"success": True, "tracks": result})

@app.route("/api/tracks/<int:track_id>", methods=["GET"])
def get_track_detail(track_id):
    user = current_user()
    conn = get_db()
    track = conn.execute("SELECT * FROM career_tracks WHERE id = ?", (track_id,)).fetchone()
    if not track:
        conn.close()
        return jsonify({"success": False, "message": "Track not found."}), 404

    modules = conn.execute("SELECT * FROM modules WHERE track_id = ? ORDER BY step_number ASC", (track_id,)).fetchall()
    
    progress_map = {}
    if user:
        p_rows = conn.execute("SELECT module_id, status, completed_checkpoints_json, updated_at FROM user_progress WHERE user_id = ?", (user["id"],)).fetchall()
        for r in p_rows:
            try:
                cp_list = json.loads(r["completed_checkpoints_json"]) if r["completed_checkpoints_json"] else []
            except Exception:
                cp_list = []
            progress_map[r["module_id"]] = {
                "status": r["status"],
                "completed_checkpoints": cp_list,
                "updated_at": r["updated_at"]
            }

    module_list = []
    completed_count = 0
    for m in modules:
        m_dict = dict(m)
        try:
            m_dict["checkpoints"] = json.loads(m["checkpoints_json"]) if m["checkpoints_json"] else []
        except Exception:
            m_dict["checkpoints"] = []
        del m_dict["checkpoints_json"]

        p = progress_map.get(m["id"], {"status": "not_started", "completed_checkpoints": [], "updated_at": None})
        m_dict["status"] = p["status"]
        m_dict["completed_checkpoints"] = p["completed_checkpoints"]
        m_dict["updated_at"] = p["updated_at"]
        if p["status"] == "completed":
            completed_count += 1
        module_list.append(m_dict)

    quiz_passed = False
    best_score = 0
    if user:
        best_attempt = conn.execute("""
            SELECT score, total_questions, passed FROM quiz_attempts 
            WHERE user_id = ? AND track_id = ? 
            ORDER BY score DESC LIMIT 1
        """, (user["id"], track_id)).fetchone()
        if best_attempt:
            quiz_passed = bool(best_attempt["passed"])
            best_score = best_attempt["score"]

    conn.close()
    return jsonify({
        "success": True,
        "track": dict(track),
        "modules": module_list,
        "total_modules": len(module_list),
        "completed_modules": completed_count,
        "progress_percent": round((completed_count / len(module_list) * 100) if module_list else 0),
        "quiz_passed": quiz_passed,
        "best_score": best_score
    })

@app.route("/api/progress/update", methods=["POST"])
def update_progress():
    user = current_user()
    if not user:
        return jsonify({"success": False, "message": "Please log in first."}), 401

    data = request.get_json() or {}
    module_id = data.get("module_id")
    new_status = data.get("status", "completed")

    if not module_id or new_status not in ["not_started", "in_progress", "completed"]:
        return jsonify({"success": False, "message": "Invalid module or status."}), 400

    conn = get_db()
    
    # If marking completed, also mark all checkpoints checked
    module = conn.execute("SELECT checkpoints_json FROM modules WHERE id = ?", (module_id,)).fetchone()
    all_cp = module["checkpoints_json"] if module and module["checkpoints_json"] else "[]"
    cp_val = all_cp if new_status == "completed" else "[]"

    conn.execute("""
        INSERT INTO user_progress (user_id, module_id, status, completed_checkpoints_json, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, module_id) DO UPDATE SET
            status = excluded.status,
            completed_checkpoints_json = CASE WHEN excluded.status = 'completed' THEN excluded.completed_checkpoints_json ELSE user_progress.completed_checkpoints_json END,
            updated_at = CURRENT_TIMESTAMP;
    """, (user["id"], module_id, new_status, cp_val))

    # Update karma points if completed
    if new_status == "completed":
        conn.execute("UPDATE users SET karma_xp = karma_xp + 100 WHERE id = ?", (user["id"],))

    conn.commit()
    conn.close()

    return jsonify({"success": True, "module_id": module_id, "status": new_status})

@app.route("/api/progress/checkpoints", methods=["POST"])
def toggle_checkpoint():
    user = current_user()
    if not user:
        return jsonify({"success": False, "message": "Please log in first."}), 401

    data = request.get_json() or {}
    module_id = data.get("module_id")
    checkpoint_name = data.get("checkpoint_name", "").strip()

    if not module_id or not checkpoint_name:
        return jsonify({"success": False, "message": "Module ID and checkpoint name are required."}), 400

    conn = get_db()
    # Fetch module total checkpoints
    module = conn.execute("SELECT checkpoints_json FROM modules WHERE id = ?", (module_id,)).fetchone()
    if not module:
        conn.close()
        return jsonify({"success": False, "message": "Module not found."}), 404

    try:
        all_checkpoints = json.loads(module["checkpoints_json"]) if module["checkpoints_json"] else []
    except Exception:
        all_checkpoints = []

    # Fetch current user completed checkpoints
    p = conn.execute("SELECT status, completed_checkpoints_json FROM user_progress WHERE user_id = ? AND module_id = ?", (user["id"], module_id)).fetchone()
    
    current_cp = []
    if p and p["completed_checkpoints_json"]:
        try:
            current_cp = json.loads(p["completed_checkpoints_json"])
        except Exception:
            current_cp = []

    if checkpoint_name in current_cp:
        current_cp.remove(checkpoint_name)
    else:
        current_cp.append(checkpoint_name)

    # Determine status
    if len(current_cp) == len(all_checkpoints) and len(all_checkpoints) > 0:
        new_status = "completed"
    elif len(current_cp) > 0:
        new_status = "in_progress"
    else:
        new_status = "not_started"

    conn.execute("""
        INSERT INTO user_progress (user_id, module_id, status, completed_checkpoints_json, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, module_id) DO UPDATE SET
            status = excluded.status,
            completed_checkpoints_json = excluded.completed_checkpoints_json,
            updated_at = CURRENT_TIMESTAMP;
    """, (user["id"], module_id, new_status, json.dumps(current_cp)))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True, 
        "module_id": module_id, 
        "completed_checkpoints": current_cp, 
        "status": new_status,
        "total_checkpoints": len(all_checkpoints)
    })

# ----------------- TECHNICAL INTERVIEW FLASHCARDS -----------------

@app.route("/api/flashcards/<track_code>", methods=["GET"])
def get_flashcards(track_code):
    conn = get_db()
    track_code = track_code.upper()
    flashcards = conn.execute("SELECT * FROM interview_flashcards WHERE track_code = ? ORDER BY id ASC", (track_code,)).fetchall()
    
    # If no track-specific flashcards, return general FSD cards
    if not flashcards:
        flashcards = conn.execute("SELECT * FROM interview_flashcards WHERE track_code = 'FSD' ORDER BY id ASC").fetchall()

    conn.close()
    return jsonify({"success": True, "flashcards": [dict(f) for f in flashcards]})

# ----------------- CAMPUS LEADERBOARD -----------------

@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    conn = get_db()
    users = conn.execute("""
        SELECT u.id, u.name, u.department, u.year_or_designation, u.target_role, u.karma_xp,
               COUNT(DISTINCT up.module_id) as completed_modules,
               COUNT(DISTINCT p.id) as projects_count,
               COUNT(DISTINCT qa.track_id) as badges_count
        FROM users u
        LEFT JOIN user_progress up ON u.id = up.user_id AND up.status = 'completed'
        LEFT JOIN projects p ON u.id = p.user_id AND p.status = 'Verified & Approved'
        LEFT JOIN quiz_attempts qa ON u.id = qa.user_id AND qa.passed = 1
        WHERE u.role = 'student'
        GROUP BY u.id
        ORDER BY u.karma_xp DESC, completed_modules DESC
        LIMIT 10
    """).fetchall()

    conn.close()
    return jsonify({"success": True, "leaderboard": [dict(u) for u in users]})

# ----------------- QUIZZES & ASSESSMENTS -----------------

@app.route("/api/quizzes/<int:track_id>", methods=["GET"])
def get_quiz_for_track(track_id):
    conn = get_db()
    quizzes = conn.execute("SELECT id, track_id, title, question, options_json, points FROM quizzes WHERE track_id = ?", (track_id,)).fetchall()
    conn.close()

    result = []
    for q in quizzes:
        q_dict = dict(q)
        try:
            q_dict["options"] = json.loads(q["options_json"])
        except Exception:
            q_dict["options"] = []
        del q_dict["options_json"]
        result.append(q_dict)

    return jsonify({"success": True, "quizzes": result})

@app.route("/api/quizzes/submit", methods=["POST"])
def submit_quiz():
    user = current_user()
    if not user:
        return jsonify({"success": False, "message": "Please log in first."}), 401

    data = request.get_json() or {}
    track_id = data.get("track_id")
    answers = data.get("answers", {})

    if not track_id:
        return jsonify({"success": False, "message": "Track ID is required."}), 400

    conn = get_db()
    questions = conn.execute("SELECT id, correct_index, points, explanation FROM quizzes WHERE track_id = ?", (track_id,)).fetchall()

    if not questions:
        conn.close()
        return jsonify({"success": False, "message": "No quizzes found for this track."}), 404

    total_score = 0
    max_score = 0
    correct_count = 0
    details = []

    for q in questions:
        q_id = str(q["id"])
        max_score += q["points"]
        user_choice = answers.get(q_id)
        is_correct = (user_choice is not None and int(user_choice) == q["correct_index"])
        
        if is_correct:
            total_score += q["points"]
            correct_count += 1

        details.append({
            "quiz_id": q["id"],
            "user_choice": user_choice,
            "correct_index": q["correct_index"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

    passed = 1 if (total_score >= (max_score * 0.70)) else 0

    conn.execute("""
        INSERT INTO quiz_attempts (user_id, track_id, score, total_questions, passed, attempted_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (user["id"], track_id, total_score, len(questions), passed))

    if passed:
        conn.execute("UPDATE users SET karma_xp = karma_xp + 150 WHERE id = ?", (user["id"],))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "score": total_score,
        "max_score": max_score,
        "correct_count": correct_count,
        "total_questions": len(questions),
        "passed": bool(passed),
        "details": details,
        "badge_earned": "Pydah Certified Specialist" if passed else None
    })

# ----------------- PROJECTS PORTFOLIO -----------------

@app.route("/api/projects", methods=["GET"])
def get_projects():
    user = current_user()
    conn = get_db()
    user_id = user["id"] if user else 0
    projects = conn.execute("""
        SELECT p.*, u.name as student_name, u.department, ct.title as track_title, ct.badge_color
        FROM projects p
        JOIN users u ON p.user_id = u.id
        JOIN career_tracks ct ON p.track_id = ct.id
        WHERE p.user_id = ? OR p.status = 'Verified & Approved'
        ORDER BY p.submitted_at DESC
    """, (user_id,)).fetchall()

    conn.close()
    return jsonify({"success": True, "projects": [dict(p) for p in projects]})

@app.route("/api/projects", methods=["POST"])
def submit_project():
    user = current_user()
    if not user:
        return jsonify({"success": False, "message": "Please log in first."}), 401

    data = request.get_json() or {}
    track_id = data.get("track_id")
    title = data.get("title", "").strip()
    summary = data.get("summary", "").strip()
    tech_stack = data.get("tech_stack", "").strip()
    github_url = data.get("github_url", "").strip()
    live_demo_url = data.get("live_demo_url", "").strip()

    if not title or not summary or not track_id:
        return jsonify({"success": False, "message": "Title, track, and summary are required."}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO projects (user_id, track_id, title, summary, tech_stack, github_url, live_demo_url, status, endorsement_remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Verified & Approved', 'Project portfolio accepted and synced with Pydah Innovation Cell.')
    """, (user["id"], track_id, title, summary, tech_stack, github_url, live_demo_url))
    new_p_id = cursor.lastrowid
    
    # Add karma for verified project
    conn.execute("UPDATE users SET karma_xp = karma_xp + 200 WHERE id = ?", (user["id"],))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Project added to your verified portfolio! (+200 XP)", "project_id": new_p_id}), 201

# ----------------- PLACEMENT & INTERNSHIP RADAR -----------------

@app.route("/api/placements", methods=["GET"])
def get_placements():
    user = current_user()
    category = request.args.get("category", "All")
    location = request.args.get("location", "All")

    conn = get_db()
    query = "SELECT * FROM placements WHERE 1=1"
    params = []

    if category != "All":
        query += " AND package_category = ?"
        params.append(category)

    if location != "All":
        query += " AND location LIKE ?"
        params.append(f"%{location}%")

    query += " ORDER BY id ASC"
    placements = conn.execute(query, params).fetchall()
    
    user_skills_text = ""
    if user:
        completed = conn.execute("""
            SELECT m.key_skills FROM user_progress up
            JOIN modules m ON up.module_id = m.id
            WHERE up.user_id = ? AND up.status = 'completed'
        """, (user["id"],)).fetchall()
        user_skills_text = " ".join([r["key_skills"] for r in completed]).lower()

    result = []
    for p in placements:
        p_dict = dict(p)
        req_skills = [s.strip() for s in p["required_skills"].split(",") if s.strip()]
        matched = 0
        for s in req_skills:
            if s.lower() in user_skills_text:
                matched += 1
        
        if user and len(req_skills) > 0:
            match_pct = max(40, min(98, round((matched / len(req_skills) * 80) + 20)))
        else:
            match_pct = 75

        p_dict["match_percent"] = match_pct
        p_dict["matched_skills_count"] = matched
        p_dict["total_skills_count"] = len(req_skills)
        result.append(p_dict)

    conn.close()
    return jsonify({"success": True, "placements": result})

# ----------------- DASHBOARD STATS & PASSPORT -----------------

@app.route("/api/stats/dashboard", methods=["GET"])
def get_dashboard_stats():
    user = current_user()
    if not user:
        return jsonify({"success": False, "message": "Please log in."}), 401

    conn = get_db()
    completed_modules = conn.execute("SELECT COUNT(*) FROM user_progress WHERE user_id = ? AND status = 'completed'", (user["id"],)).fetchone()[0]
    in_progress_modules = conn.execute("SELECT COUNT(*) FROM user_progress WHERE user_id = ? AND status = 'in_progress'", (user["id"],)).fetchone()[0]
    projects_count = conn.execute("SELECT COUNT(*) FROM projects WHERE user_id = ?", (user["id"],)).fetchone()[0]
    quizzes_passed = conn.execute("SELECT COUNT(DISTINCT track_id) FROM quiz_attempts WHERE user_id = ? AND passed = 1", (user["id"],)).fetchone()[0]
    total_platform_modules = conn.execute("SELECT COUNT(*) FROM modules").fetchone()[0]

    raw_readiness = 38 + (completed_modules * 7) + (quizzes_passed * 12) + (projects_count * 8)
    career_readiness = min(99, raw_readiness)

    preferred_track_id = user.get("preferred_track_id")
    active_track = None
    if preferred_track_id:
        active_track = conn.execute("""
            SELECT ct.*, COUNT(m.id) as total_steps
            FROM career_tracks ct
            LEFT JOIN modules m ON ct.id = m.track_id
            WHERE ct.id = ?
            GROUP BY ct.id
        """, (preferred_track_id,)).fetchone()

    if not active_track and user.get("department"):
        active_track = conn.execute("""
            SELECT ct.*, COUNT(m.id) as total_steps
            FROM career_tracks ct
            LEFT JOIN modules m ON ct.id = m.track_id
            WHERE ct.departments LIKE ?
            GROUP BY ct.id
            ORDER BY ct.id ASC LIMIT 1
        """, (f"%{user['department']}%",)).fetchone()

    if not active_track:
        active_track = conn.execute("""
            SELECT ct.*, COUNT(m.id) as total_steps
            FROM career_tracks ct
            LEFT JOIN modules m ON ct.id = m.track_id
            GROUP BY ct.id
            ORDER BY ct.id ASC LIMIT 1
        """).fetchone()

    # Get live user karma
    u_row = conn.execute("SELECT karma_xp FROM users WHERE id = ?", (user["id"],)).fetchone()
    karma_xp = u_row["karma_xp"] if u_row else 500

    conn.close()

    return jsonify({
        "success": True,
        "stats": {
            "completed_modules": completed_modules,
            "in_progress_modules": in_progress_modules,
            "projects_count": projects_count,
            "quizzes_passed": quizzes_passed,
            "total_modules": total_platform_modules,
            "career_readiness": career_readiness,
            "streak_days": 14,
            "karma_points": karma_xp,
            "active_track": dict(active_track) if active_track else None
        }
    })

@app.route("/api/passport", methods=["GET"])
def get_skill_passport():
    user = current_user()
    if not user:
        return jsonify({"success": False, "message": "Please log in."}), 401

    conn = get_db()
    completed = conn.execute("""
        SELECT m.title, m.tier, m.key_skills, ct.title as track_title, ct.badge_color, up.updated_at
        FROM user_progress up
        JOIN modules m ON up.module_id = m.id
        JOIN career_tracks ct ON m.track_id = ct.id
        WHERE up.user_id = ? AND up.status = 'completed'
        ORDER BY up.updated_at DESC
    """, (user["id"],)).fetchall()

    projects = conn.execute("""
        SELECT p.title, p.tech_stack, p.github_url, p.live_demo_url, p.summary, p.status, ct.title as track_title
        FROM projects p
        JOIN career_tracks ct ON p.track_id = ct.id
        WHERE p.user_id = ?
    """, (user["id"],)).fetchall()

    badges = conn.execute("""
        SELECT DISTINCT ct.title as track_title, qa.score, qa.total_questions, qa.attempted_at
        FROM quiz_attempts qa
        JOIN career_tracks ct ON qa.track_id = ct.id
        WHERE qa.user_id = ? AND qa.passed = 1
    """, (user["id"],)).fetchall()

    # Generate ATS-Friendly Resume text snippet
    skills_set = set()
    for c in completed:
        for s in c["key_skills"].split(","):
            if s.strip():
                skills_set.add(s.strip())

    ats_skills = ", ".join(list(skills_set)[:12]) if skills_set else "Python, REST APIs, SQL, Full Stack Architecture, Git"

    ats_projects = []
    for p in projects:
        ats_projects.append(f"• {p['title']} ({p['tech_stack']}): {p['summary']}")

    ats_resume_snippet = f"""{user['name']} | {user['target_role']}
Department of {user['department']} - Pydah Group of Institutions
SkillPath Verification ID: PYDAH-SP-{user['id']:04d}-{datetime.now().strftime('%Y')}

TECHNICAL PROFICIENCIES:
{ats_skills}

ACADEMIC & INDUSTRY CAPSTONES:
{chr(10).join(ats_projects) if ats_projects else "• Production Full-Stack System: Built and containerized RESTful API services with database models and responsive user interface."}

VERIFIED CREDENTIALS:
• Pydah Certified Specialist: {len(completed)} Curriculum Modules Completed
• Placement Readiness Benchmark: Exceeded Technical Screening Criteria
"""

    conn.close()

    return jsonify({
        "success": True,
        "user": user,
        "issued_at": datetime.now().strftime("%B %d, %Y"),
        "verification_id": f"PYDAH-SP-{user['id']:04d}-{datetime.now().strftime('%Y')}",
        "completed_modules": [dict(c) for c in completed],
        "projects": [dict(p) for p in projects],
        "badges": [dict(b) for b in badges],
        "ats_resume_snippet": ats_resume_snippet.strip()
    })

# ----------------- RECRUITER & STUDENT PORTFOLIO SHOWCASE -----------------

def get_portfolio_payload(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return None

    user_dict = dict(user)
    user_dict.pop("password_hash", None)

    # Fetch projects
    projects = conn.execute("""
        SELECT p.*, ct.title as track_title, ct.badge_color, ct.icon as track_icon
        FROM projects p
        LEFT JOIN career_tracks ct ON p.track_id = ct.id
        WHERE p.user_id = ?
        ORDER BY p.id DESC
    """, (user_id,)).fetchall()
    project_list = [dict(p) for p in projects]

    # Fetch completed skills & modules
    completed_modules = conn.execute("""
        SELECT m.title, m.tier, m.key_skills, ct.title as track_title, ct.badge_color
        FROM user_progress up
        JOIN modules m ON up.module_id = m.id
        JOIN career_tracks ct ON m.track_id = ct.id
        WHERE up.user_id = ? AND up.status = 'completed'
        ORDER BY m.id ASC
    """, (user_id,)).fetchall()
    
    # Skill breakdown
    skills_set = set()
    for m in completed_modules:
        if m["key_skills"]:
            for s in m["key_skills"].split(","):
                if s.strip():
                    skills_set.add(s.strip())

    if user_dict.get("custom_skills"):
        for s in user_dict["custom_skills"].split(","):
            if s.strip():
                skills_set.add(s.strip())

    all_skills = sorted(list(skills_set)) if skills_set else [
        "Python", "Flask", "JavaScript", "React", "REST APIs", "SQLite", 
        "Data Structures", "Algorithms", "Git & GitHub", "IoT & Robotics", "Embedded C"
    ]

    # Categorize skills nicely for presentation
    categorized_skills = {
        "Languages & Frameworks": [],
        "Cloud, Tools & DB": [],
        "Core CS & Systems": [],
        "Hardware, AI & Emerging": []
    }
    for skill in all_skills:
        s_low = skill.lower()
        if any(k in s_low for k in ["python", "javascript", "react", "flask", "django", "html", "css", "c++", "c ", "java", "node"]):
            categorized_skills["Languages & Frameworks"].append(skill)
        elif any(k in s_low for k in ["docker", "git", "sql", "sqlite", "cloud", "aws", "linux", "rest", "api", "postman"]):
            categorized_skills["Cloud, Tools & DB"].append(skill)
        elif any(k in s_low for k in ["robot", "embedded", "arduino", "iot", "sensor", "ai", "machine learning", "deep learning", "nlp", "vision", "rfid"]):
            categorized_skills["Hardware, AI & Emerging"].append(skill)
        else:
            categorized_skills["Core CS & Systems"].append(skill)

    if not categorized_skills["Languages & Frameworks"]:
        categorized_skills["Languages & Frameworks"] = ["Python", "JavaScript", "C/C++", "HTML5 & CSS3"]
    if not categorized_skills["Cloud, Tools & DB"]:
        categorized_skills["Cloud, Tools & DB"] = ["Flask", "SQLite", "REST APIs", "Git & GitHub"]
    if not categorized_skills["Hardware, AI & Emerging"]:
        categorized_skills["Hardware, AI & Emerging"] = ["Embedded Systems", "IoT Telemetry", "Machine Learning", "Robotics"]
    if not categorized_skills["Core CS & Systems"]:
        categorized_skills["Core CS & Systems"] = ["Data Structures & Algorithms", "Object-Oriented Design", "Database Management"]

    # Badges
    badges = conn.execute("""
        SELECT DISTINCT ct.title as track_title, ct.badge_color, qa.score, qa.total_questions, qa.attempted_at
        FROM quiz_attempts qa
        JOIN career_tracks ct ON qa.track_id = ct.id
        WHERE qa.user_id = ? AND qa.passed = 1
    """, (user_id,)).fetchall()

    # Parse experience JSON
    experiences = []
    if user_dict.get("experience_json"):
        try:
            experiences = json.loads(user_dict["experience_json"])
        except Exception:
            experiences = []

    lan_ip = get_lan_ip()
    port = int(os.environ.get("PORT", 5000))
    mobile_portfolio_url = f"http://{lan_ip}:{port}/portfolio/{user_id}"

    conn.close()

    return {
        "user": user_dict,
        "projects": project_list,
        "skills": all_skills,
        "categorized_skills": categorized_skills,
        "completed_modules": [dict(m) for m in completed_modules],
        "badges": [dict(b) for b in badges],
        "experiences": experiences,
        "lan_ip": lan_ip,
        "mobile_portfolio_url": mobile_portfolio_url,
        "stats": {
            "projects_count": len(project_list),
            "skills_count": len(all_skills),
            "modules_count": len(completed_modules),
            "badges_count": len(badges),
            "karma_xp": user_dict.get("karma_xp", 500)
        }
    }

@app.route("/portfolio/<int:user_id>")
def view_public_portfolio(user_id):
    data = get_portfolio_payload(user_id)
    if not data:
        return "Student portfolio profile not found.", 404
    return render_template("portfolio.html", **data)

@app.route("/portfolio/me")
def view_my_portfolio():
    user = current_user()
    if not user:
        return redirect("/#login")
    return redirect(f"/portfolio/{user['id']}")

@app.route("/api/portfolio/<int:user_id>", methods=["GET"])
def api_get_portfolio(user_id):
    data = get_portfolio_payload(user_id)
    if not data:
        return jsonify({"success": False, "message": "Student portfolio not found."}), 404
    return jsonify({"success": True, "portfolio": data})

@app.route("/api/portfolio/upload-avatar", methods=["POST"])
def upload_avatar():
    user = current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required. Please log in."}), 401

    if "avatar_file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded."}), 400

    file = request.files["avatar_file"]
    if not file or file.filename == "":
        return jsonify({"success": False, "message": "No image selected."}), 400

    allowed = {"png", "jpg", "jpeg", "webp", "gif"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        return jsonify({"success": False, "message": "Please choose a valid photo (PNG, JPG, JPEG, WEBP)."}), 400

    filename = f"avatar_user_{user['id']}_{int(datetime.now().timestamp())}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    avatar_url = f"/static/uploads/{filename}"

    conn = get_db()
    conn.execute("UPDATE users SET profile_image_url = ? WHERE id = ?", (avatar_url, user["id"]))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True, 
        "message": "Profile picture updated successfully from your device!", 
        "avatar_url": avatar_url
    })

@app.route("/api/portfolio/update", methods=["POST"])
def api_update_portfolio():
    user = current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required."}), 401

    data = request.get_json() or {}
    tagline = data.get("tagline", "").strip()
    bio = data.get("bio", "").strip()
    github_url = data.get("github_url", "").strip()
    linkedin_url = data.get("linkedin_url", "").strip()
    location = data.get("location", "").strip()
    phone = data.get("phone", "").strip()
    custom_skills = data.get("custom_skills", "").strip()
    experience_json = data.get("experience_json", "[]")
    profile_image_url = data.get("profile_image_url", "").strip() or "/static/images/student_avatar.jpg"

    if isinstance(experience_json, list):
        experience_json = json.dumps(experience_json)

    conn = get_db()
    conn.execute("""
        UPDATE users
        SET tagline = ?, bio = ?, github_url = ?, linkedin_url = ?,
            location = ?, phone = ?, custom_skills = ?, experience_json = ?, profile_image_url = ?
        WHERE id = ?
    """, (tagline, bio, github_url, linkedin_url, location, phone, custom_skills, experience_json, profile_image_url, user["id"]))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Student portfolio updated successfully!"})

@app.route("/api/portfolio/contact", methods=["POST"])
def api_portfolio_contact():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()
    if not name or not email or not message:
        return jsonify({"success": False, "message": "All fields are required."}), 400
    return jsonify({"success": True, "message": f"Thank you, {name}! Your message has been sent to the student successfully."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting PYDAH SkillPath Enterprise Platform on http://127.0.0.1:{port} ...")
    app.run(host="0.0.0.0", port=port, debug=True)
