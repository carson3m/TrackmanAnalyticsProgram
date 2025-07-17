'''
from flask import Flask, request, jsonify, render_template, send_file, abort
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, bcrypt, User
from flask_login import login_required, current_user
from models import User  # <- forces Alembic to "see" the model
import pandas as pd
import sys
import json
import os

from store.data_store import data_store  # If you're using this somewhere else

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../PythonFiles')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AnalyticsBackend.routes.session_api import session_bp
from PythonFiles.core.statistics import calculate_whiff_rate, calculate_strike_rate, calculate_zone_rate
from PythonFiles.core.player_metrics import PlayerMetricsAnalyzer
from PythonFiles.core.session_manager import SessionManager

app = Flask(__name__)
CORS(app)

app.register_blueprint(session_bp, url_prefix="/api")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key'  # 🔐 Needed for sessions or login
app.session_manager = SessionManager()
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

uploaded_df = None
TEMP_CSV_PATH = "temp_uploaded.csv"
from flask.cli import with_appcontext
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect here if not logged in

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))

        flash("Invalid username or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/admin-only")
@login_required
def admin_only():
    if current_user.role != "admin":
        return jsonify({"error": "Access denied"}), 403
    return jsonify({"message": "Welcome, admin!"})

@app.cli.command("create-user")
@with_appcontext
def create_user():
    from models import User, db
    username = input("Username: ")
    password = input("Password: ")
    role = input("Role (admin/coach/viewer): ").strip().lower()

    if role not in ("admin", "coach", "viewer"):
        print("❌ Invalid role.")
        return

    if User.query.filter_by(username=username).first():
        print("❌ User already exists.")
        return

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"✅ Created user '{username}' with role '{role}'")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/live_mode")
def live_mode():
    return render_template("live_mode.html")

@app.route("/upload_csv", methods=["GET"])
@login_required
def show_csv_upload():
    if current_user.role != "admin":
        return "Access denied", 403
    return render_template("upload_csv.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You’ve been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/api/upload_csv", methods=["POST"])
def upload_csv():
    if current_user.role != 'admin':
        return abort(403)  # Forbidden
    global uploaded_df
    file = request.files.get("csv_file")
    if not file or not file.filename.endswith(".csv"):
        return "Invalid file", 400

    uploaded_df = pd.read_csv(file)
    uploaded_df.to_csv(TEMP_CSV_PATH, index=False)  # Save temporarily

    teams = uploaded_df['PitcherTeam'].dropna().unique().tolist() if 'PitcherTeam' in uploaded_df.columns else []
    return render_template("select_pitcher.html", teams=teams)

@app.route("/api/set_pitcher", methods=["POST"])
def set_pitcher():
    from PythonFiles.core.session_manager import SessionManager
    pitcher = request.form.get("pitcher")

    if not hasattr(app, "session_manager"):
        app.session_manager = SessionManager()

    app.session_manager.context_manager.pitcher_name = pitcher
    return f"✅ Pitcher set to: {pitcher}"

@app.route("/api/team_pitchers", methods=["GET"])
def get_team_pitchers():
    global uploaded_df
    team = request.args.get("team")

    if uploaded_df is None and os.path.exists(TEMP_CSV_PATH):
        uploaded_df = pd.read_csv(TEMP_CSV_PATH)

    if uploaded_df is None or team is None:
        return jsonify([])

    if 'Pitcher' not in uploaded_df.columns or 'PitcherTeam' not in uploaded_df.columns:
        return jsonify([])

    pitchers = uploaded_df[uploaded_df['PitcherTeam'] == team]['Pitcher'].dropna().unique().tolist()
    return jsonify(pitchers)

@app.route("/download_pdf", methods=["GET"])
def download_pdf():
    global uploaded_df
    team = request.args.get("team")
    pitcher = request.args.get("pitcher")

    if uploaded_df is None or team is None or pitcher is None:
        return "Missing data", 400

    df = uploaded_df[(uploaded_df['PitcherTeam'] == team) & (uploaded_df['Pitcher'] == pitcher)]
    if df.empty:
        return "No matching data found", 404

    analyzer = PlayerMetricsAnalyzer(df, pitcher)
    per_pitch_df = analyzer.per_pitch_type_metrics_df()

    pitch_col = analyzer.get_pitch_type_column()
    df = df[df[pitch_col].notna()]
    df = df.dropna(subset=["HorzBreak", "InducedVertBreak", "RelSide", "RelHeight"])

    # Plotting functions (match your plot_func structure)
    def plot_breaks(ax):
        for pitch_type, group in df.groupby(pitch_col):
            ax.scatter(group["HorzBreak"], group["InducedVertBreak"], label=pitch_type)
        ax.set_xlabel("Horizontal Break (in)")
        ax.set_ylabel("Vertical Break (in)")
        ax.set_title("Pitch Breaks")
        # Set fixed limits
        ax.set_xlim(-30, 30)
        ax.set_ylim(-30, 30)

        # Equal aspect ratio
        ax.set_aspect('equal', adjustable='box')
        ax.grid(True)
        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)
        ax.legend()

    def plot_release_points(ax):
        for pitch_type, group in df.groupby(pitch_col):
            ax.scatter(group["RelSide"], group["RelHeight"], label=pitch_type)

        ax.set_xlabel("Horizontal Release Side (ft)")
        ax.set_ylabel("Vertical Release Height (ft)")
        ax.set_title("Release Points")

        # Set fixed limits
        ax.set_xlim(-3.5, 3.5)
        ax.set_ylim(1, 7)

        # Equal aspect ratio
        ax.set_aspect('equal', adjustable='box')

        ax.grid(True)
        ax.legend()

    from PythonFiles.summary.export import export_summary_to_pdf

    pdf_path = export_summary_to_pdf(
        player_name=pitcher,
        summary_text="",  # optional string summary if you want to include it later
        plot_funcs=[plot_breaks, plot_release_points],
        metrics_df=per_pitch_df
    )

    return send_file(pdf_path, as_attachment=True)

@app.route("/api/receive_pitch", methods=["POST"])
def receive_pitch():
    try:
        pitch_json = request.get_json()
        print("[API] 🟢 Received pitch data:")
        print(json.dumps(pitch_json, indent=2))

        app.session_manager.on_new_pitch(pitch_json)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"[API] ❌ Error processing pitch data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/csv_summary", methods=["GET"])
@login_required
def show_summary():
    global uploaded_df
    team = request.args.get("team")
    pitcher = request.args.get("pitcher")

    if uploaded_df is None and os.path.exists(TEMP_CSV_PATH):
        uploaded_df = pd.read_csv(TEMP_CSV_PATH)

    if uploaded_df is None or team is None or pitcher is None:
        return "Missing data", 400


    df = uploaded_df[(uploaded_df['PitcherTeam'] == team) & (uploaded_df['Pitcher'] == pitcher)]
    if df.empty:
        print(f"No matching data for team={team}, pitcher={pitcher}")
        print("Available teams:", uploaded_df['PitcherTeam'].unique())
        print("Available pitchers for team:", uploaded_df[uploaded_df['PitcherTeam'] == team]['Pitcher'].unique())
        return "No matching data found", 404


    whiff = calculate_whiff_rate(df)
    strike = calculate_strike_rate(df)
    zone = calculate_zone_rate(df)

    metrics = {
        "whiff_rate": whiff,
        "strike_rate": strike,
        "zone_rate": zone
    }

    analyzer = PlayerMetricsAnalyzer(df, pitcher)
    per_pitch_df = analyzer.per_pitch_type_metrics_df()

    # Plotting setup
    pitch_col = analyzer.get_pitch_type_column()
    breaks_data, release_data = [], []

    if pitch_col and pitch_col in df.columns:
        df = df[df[pitch_col].notna()]

        # Remove rows with missing data needed for plots
        df = df.dropna(subset=["HorzBreak", "InducedVertBreak", "RelSide", "RelHeight"])

        for pitch_type, group in df.groupby(pitch_col):
            breaks_data.append({
                "x": group["HorzBreak"].tolist(),
                "y": group["InducedVertBreak"].tolist(),
                "mode": "markers",
                "name": pitch_type
            })
            release_data.append({
                "x": group["RelSide"].tolist(),
                "y": group["RelHeight"].tolist(),
                "mode": "markers",
                "name": pitch_type
            })

    return render_template("csv_summary.html",
                        metrics=metrics,
                        pitch_table=per_pitch_df.to_html(classes="table table-striped", index=False),
                        breaks_data=breaks_data,
                        release_data=release_data,
                        team=team,
                        pitcher=pitcher)  # 👈 This is key

@app.route("/api/start_session", methods=["POST"])
def start_session():
    app.session_manager.start_live_mode()
    return jsonify({"status": "started"})

@app.route("/api/stop_session", methods=["POST"])
def stop_session():
    app.session_manager.stop()
    return jsonify({"status": "stopped"})


if __name__ == "__main__":
    print("Starting Flask app on http://127.0.0.1:5050 ...")
    app.run(host="0.0.0.0", port=5050, debug=True)
'''