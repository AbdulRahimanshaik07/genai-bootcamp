import os
import json
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
from bson import ObjectId


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Secret key for sessions
    app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-change-me")

    # MongoDB configuration
    mongo_uri = os.getenv(
        "MONGODB_URI",
        "mongodb+srv://shaikabdul:1234@build.yiikjuc.mongodb.net/?retryWrites=true&w=majority&appName=Build",
    )
    mongo_db_name = os.getenv("MONGODB_DB", "makeskilled_bootcamp")
    mongo_collection = os.getenv("MONGODB_COLLECTION", "colleges")

    # Initialize Mongo only once
    try:
        client = MongoClient(mongo_uri)
        db = client[mongo_db_name]
        app.mongo_colleges = db[mongo_collection]
        app.mongo_events = db[os.getenv("MONGODB_EVENTS_COLLECTION", "events")]
    except Exception as exc:  # Fallback if URI is invalid/unreachable
        app.mongo_colleges = None
        app.mongo_events = None
        app.logger.error(f"MongoDB connection failed: {exc}")

    # Ensure data directory for JSON persistence exists
    data_dir = Path(app.root_path) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    app.reg_json_path = data_dir / "registrations.json"
    if not app.reg_json_path.exists():
        app.reg_json_path.write_text("[]", encoding="utf-8")
    
    # Feedback JSON paths
    app.student_feedback_path = data_dir / "student_feedback.json"
    app.faculty_feedback_path = data_dir / "faculty_feedback.json"
    if not app.student_feedback_path.exists():
        app.student_feedback_path.write_text("[]", encoding="utf-8")
    if not app.faculty_feedback_path.exists():
        app.faculty_feedback_path.write_text("[]", encoding="utf-8")

    @app.route("/")
    def index():
        # Fetch feedback data for public display
        student_feedback = []
        faculty_feedback = []
        try:
            student_data = json.loads(app.student_feedback_path.read_text(encoding="utf-8"))
            if isinstance(student_data, list):
                student_feedback = student_data
        except Exception:
            student_feedback = []
        try:
            faculty_data = json.loads(app.faculty_feedback_path.read_text(encoding="utf-8"))
            if isinstance(faculty_data, list):
                faculty_feedback = faculty_data
        except Exception:
            faculty_feedback = []
        
        return render_template("index.html", student_feedback=student_feedback, faculty_feedback=faculty_feedback)

    # ---------------------- Public APIs ----------------------
    @app.get("/api/events")
    def list_events():
        events = []
        if getattr(app, "mongo_events", None) is not None:
            try:
                for ev in app.mongo_events.find().sort("startDate", 1):
                    ev["id"] = str(ev.pop("_id"))
                    events.append(ev)
            except Exception as exc:
                app.logger.error(f"Failed to fetch events: {exc}")
        return jsonify({"ok": True, "events": events})

    @app.post("/api/register-college")
    def register_college():
        try:
            payload = request.get_json(force=True)
        except Exception:
            return jsonify({"ok": False, "error": "Invalid JSON body"}), 400

        required = [
            "collegeName",
            "hodName",
            "email",
            "phone",
            "city",
            "state",
        ]
        missing = [k for k in required if not payload.get(k)]
        if missing:
            return (
                jsonify({"ok": False, "error": f"Missing fields: {', '.join(missing)}"}),
                400,
            )

        record = {
            "collegeName": str(payload["collegeName"]).strip(),
            "hodName": str(payload["hodName"]).strip(),
            "email": str(payload["email"]).strip().lower(),
            "phone": str(payload["phone"]).strip(),
            "city": str(payload["city"]).strip(),
            "state": str(payload["state"]).strip(),
            "createdAt": datetime.utcnow().isoformat() + "Z",
        }

        # Persist to MongoDB if available
        mongo_error = None
        if getattr(app, "mongo_colleges", None) is not None:
            try:
                app.mongo_colleges.insert_one(record.copy())
            except Exception as exc:
                mongo_error = str(exc)

        # Always append to JSON as a reliable local log
        try:
            existing = json.loads(app.reg_json_path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
            existing.append(record)
            app.reg_json_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            return jsonify({"ok": False, "error": f"Failed to persist locally: {exc}"}), 500

        resp = {"ok": True, "message": "Registration received"}
        if mongo_error:
            resp["warning"] = f"MongoDB write failed: {mongo_error}"
        return jsonify(resp), 201

    @app.post("/api/submit-feedback")
    def submit_feedback():
        try:
            payload = request.get_json(force=True)
        except Exception:
            return jsonify({"ok": False, "error": "Invalid JSON body"}), 400

        feedback_type = payload.get("type", "").strip().lower()
        if feedback_type not in ["student", "faculty"]:
            return jsonify({"ok": False, "error": "Invalid feedback type"}), 400

        required = ["name", "email", "rating", "message"]
        missing = [k for k in required if not payload.get(k)]
        if missing:
            return (
                jsonify({"ok": False, "error": f"Missing fields: {', '.join(missing)}"}),
                400,
            )

        record = {
            "name": str(payload["name"]).strip(),
            "email": str(payload["email"]).strip().lower(),
            "rating": int(payload["rating"]),
            "message": str(payload["message"]).strip(),
            "college": str(payload.get("college", "")).strip(),
            "createdAt": datetime.utcnow().isoformat() + "Z",
        }

        # Save to appropriate JSON file
        try:
            feedback_path = (
                app.student_feedback_path
                if feedback_type == "student"
                else app.faculty_feedback_path
            )
            existing = json.loads(feedback_path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
            existing.append(record)
            feedback_path.write_text(
                json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as exc:
            return jsonify({"ok": False, "error": f"Failed to save feedback: {exc}"}), 500

        return jsonify({"ok": True, "message": "Feedback submitted successfully"}), 201

    # ---------------------- Admin Views ----------------------
    def is_admin() -> bool:
        return bool(session.get("admin_authenticated"))

    @app.get("/admin")
    def admin_login_page():
        if is_admin():
            return redirect(url_for("admin_dashboard"))
        return render_template("admin.html", mode="login")

    @app.route("/admin/login", methods=["POST"])
    def admin_login():
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        admin_user = os.getenv("ADMIN_USERNAME", "admin")
        admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")
        
        # Debug logging
        app.logger.info(f"Login attempt - Username: {username}, Expected: {admin_user}")
        
        if username == admin_user and password == admin_pass:
            session["admin_authenticated"] = True
            session.permanent = True
            app.logger.info("Login successful")
            return redirect(url_for("admin_dashboard"))
        
        app.logger.warning("Login failed - Invalid credentials")
        return render_template("admin.html", mode="login", error="Invalid credentials")

    @app.get("/admin/dashboard")
    def admin_dashboard():
        if not is_admin():
            return redirect(url_for("admin_login_page"))
        # Fetch events and registrations for initial render
        events = []
        if getattr(app, "mongo_events", None) is not None:
            try:
                for ev in app.mongo_events.find().sort("startDate", 1):
                    ev["id"] = str(ev.pop("_id"))
                    events.append(ev)
            except Exception as exc:
                app.logger.error(f"Events fetch failed: {exc}")
        registrations = []
        try:
            existing = json.loads(app.reg_json_path.read_text(encoding="utf-8"))
            if isinstance(existing, list):
                registrations = existing
        except Exception:
            registrations = []
        
        # Fetch feedback data
        student_feedback = []
        faculty_feedback = []
        try:
            student_data = json.loads(app.student_feedback_path.read_text(encoding="utf-8"))
            if isinstance(student_data, list):
                student_feedback = student_data
        except Exception:
            student_feedback = []
        try:
            faculty_data = json.loads(app.faculty_feedback_path.read_text(encoding="utf-8"))
            if isinstance(faculty_data, list):
                faculty_feedback = faculty_data
        except Exception:
            faculty_feedback = []
        
        return render_template("admin.html", mode="dashboard", events=events, registrations=registrations, 
                             student_feedback=student_feedback, faculty_feedback=faculty_feedback)

    @app.route("/admin/logout", methods=["POST"])
    def admin_logout():
        session.clear()
        return redirect(url_for("index"))

    # ---------------------- Admin APIs (protected) ----------------------
    def require_admin():
        if not is_admin():
            return jsonify({"ok": False, "error": "Unauthorized"}), 401
        return None

    @app.route("/api/admin/events", methods=["POST"])
    def admin_create_event():
        unauthorized = require_admin()
        if unauthorized:
            return unauthorized
        try:
            payload = request.get_json(force=True)
        except Exception:
            return jsonify({"ok": False, "error": "Invalid JSON"}), 400
        required = ["title", "location", "startDate", "endDate"]
        missing = [k for k in required if not payload.get(k)]
        if missing:
            return jsonify({"ok": False, "error": f"Missing: {', '.join(missing)}"}), 400
        record = {
            "title": str(payload["title"]).strip(),
            "location": str(payload["location"]).strip(),
            "startDate": str(payload["startDate"]).strip(),
            "endDate": str(payload["endDate"]).strip(),
            "type": str(payload.get("type", "Gen AI")).strip(),
        }
        if getattr(app, "mongo_events", None) is None:
            return jsonify({"ok": False, "error": "DB not available"}), 500
        try:
            ins = app.mongo_events.insert_one(record)
            record["id"] = str(ins.inserted_id)
            return jsonify({"ok": True, "event": record}), 201
        except Exception as exc:
            return jsonify({"ok": False, "error": f"DB insert failed: {exc}"}), 500

    @app.route("/api/admin/events/<event_id>", methods=["PUT"])
    def admin_update_event(event_id: str):
        unauthorized = require_admin()
        if unauthorized:
            return unauthorized
        try:
            payload = request.get_json(force=True)
        except Exception:
            return jsonify({"ok": False, "error": "Invalid JSON"}), 400
        if getattr(app, "mongo_events", None) is None:
            return jsonify({"ok": False, "error": "DB not available"}), 500
        try:
            oid = ObjectId(event_id)
        except Exception:
            return jsonify({"ok": False, "error": "Invalid id"}), 400
        update = {k: v for k, v in payload.items() if k in {"title", "location", "startDate", "endDate", "type"}}
        if not update:
            return jsonify({"ok": False, "error": "Nothing to update"}), 400
        try:
            app.mongo_events.update_one({"_id": oid}, {"$set": update})
            return jsonify({"ok": True})
        except Exception as exc:
            return jsonify({"ok": False, "error": f"DB update failed: {exc}"}), 500

    @app.route("/api/admin/events/<event_id>", methods=["DELETE"])
    def admin_delete_event(event_id: str):
        unauthorized = require_admin()
        if unauthorized:
            return unauthorized
        if getattr(app, "mongo_events", None) is None:
            return jsonify({"ok": False, "error": "DB not available"}), 500
        try:
            oid = ObjectId(event_id)
        except Exception:
            return jsonify({"ok": False, "error": "Invalid id"}), 400
        try:
            app.mongo_events.delete_one({"_id": oid})
            return jsonify({"ok": True})
        except Exception as exc:
            return jsonify({"ok": False, "error": f"DB delete failed: {exc}"}), 500

    @app.get("/api/admin/registrations")
    def admin_list_registrations():
        unauthorized = require_admin()
        if unauthorized:
            return unauthorized
        try:
            existing = json.loads(app.reg_json_path.read_text(encoding="utf-8"))
        except Exception:
            existing = []
        return jsonify({"ok": True, "registrations": existing})

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


