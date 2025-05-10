import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash # For creating a default admin user
from dotenv import load_dotenv
import uuid # For generating unique filenames for audio
import markdown # For rendering About page content

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.orm import joinedload # Import joinedload

from src.models.user import db, User
from src.models.voice import ClonedVoice # Import ClonedVoice model
from src.elevenlabs_actions import initialize_elevenlabs, clone_voice as elevenlabs_clone_voice, text_to_speech as elevenlabs_text_to_speech
from src.gemini_textfx import generate_text_effect, TEXTFX_MODELS # Import TEXTFX_MODELS to access output_type

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"), template_folder=os.path.join(os.path.dirname(__file__), "templates"))
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "a_very_strong_default_secret_key_for_development_!@#$%")
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
app.config["GENERATED_AUDIO_FOLDER"] = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_audio")
app.config["ABOUT_CONTENT_FILE"] = os.path.join(os.path.dirname(os.path.dirname(__file__)), "about_content.md")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {"wav", "mp3", "flac", "ogg", "m4a"}

# Database setup
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{os.getenv(
    'DB_USERNAME', 'root')}:{os.getenv(
        'DB_PASSWORD', 'password')}@{os.getenv(
            'DB_HOST', 'localhost')}:{os.getenv(
                'DB_PORT', '3306')}/{os.getenv(
                    'DB_NAME', 'fanvoice_db')}" 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "handle_login" 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if ELEVENLABS_API_KEY:
    initialize_elevenlabs(ELEVENLABS_API_KEY)
else:
    print("CRITICAL: ELEVENLABS_API_KEY not found. ElevenLabs features will not work.")

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])
if not os.path.exists(app.config["GENERATED_AUDIO_FOLDER"]):
    os.makedirs(app.config["GENERATED_AUDIO_FOLDER"])
if not os.path.exists(os.path.join(os.path.dirname(__file__), "templates")):
    os.makedirs(os.path.join(os.path.dirname(__file__), "templates"))

with app.app_context():
    db.create_all() # Ensures tables exist

    # Handle migration from 'admin' to 'artist'
    artist_user = User.query.filter_by(username="artist").first()
    if not artist_user:
        old_admin_user = User.query.filter_by(username="admin").first()
        if old_admin_user:
            # Delete ClonedVoice records associated with the old admin user
            ClonedVoice.query.filter_by(user_id=old_admin_user.id).delete()
            print(f"Deleted ClonedVoice records for old admin user ID: {old_admin_user.id}")
            db.session.delete(old_admin_user)
            print(f"Old 'admin' user ({old_admin_user.username}) removed.")
            db.session.commit() # Commit deletions before creating new user

        # Create the new 'artist' user
        new_artist_user = User(username="artist", email="artist@example.com", role="admin") # role is still 'admin' for permissions
        new_artist_user.set_password("artistpw")
        db.session.add(new_artist_user)
        db.session.commit() 
        print("Default 'artist' user created with username 'artist' and password 'artistpw'")

    # Handle migration from 'testuser' to 'fan'
    fan_user = User.query.filter_by(username="fan").first()
    if not fan_user:
        old_test_user = User.query.filter_by(username="testuser").first()
        if old_test_user:
            # Delete ClonedVoice records associated with the old testuser
            ClonedVoice.query.filter_by(user_id=old_test_user.id).delete()
            print(f"Deleted ClonedVoice records for old testuser ID: {old_test_user.id}")
            db.session.delete(old_test_user)
            print(f"Old 'testuser' user ({old_test_user.username}) removed.")
            db.session.commit() # Commit deletions before creating new user

        # Create the new 'fan' user
        new_fan_user = User(username="fan", email="fan@example.com", role="user")
        new_fan_user.set_password("fanpw")
        db.session.add(new_fan_user)
        db.session.commit()
        print("Default 'fan' user created with username 'fan' and password 'fanpw'")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
@login_required
def index_page():
    voices_for_dropdown = []
    if current_user.role == 'admin':
        # Eagerly load the related User object to avoid UndefinedError in template
        voices_for_dropdown = ClonedVoice.query.options(joinedload(ClonedVoice.user)).all()
    return render_template("index.html", cloned_voices=voices_for_dropdown)

@app.route("/about")
def handle_about_page():
    try:
        with open(app.config["ABOUT_CONTENT_FILE"], "r", encoding="utf-8") as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content)
    except FileNotFoundError:
        html_content = "<p>About content not found.</p>"
    except Exception as e:
        html_content = f"<p>Error loading About page: {str(e)}</p>"
    return render_template("about.html", content=html_content)

@app.route("/login", methods=["GET", "POST"])
def handle_login():
    if current_user.is_authenticated:
        return redirect(url_for("index_page")) 
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("index_page"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def handle_logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("handle_login"))

@app.route("/upload_voice", methods=["POST"])
@login_required
def handle_voice_upload():
    if not ELEVENLABS_API_KEY:
        flash("ElevenLabs API key not configured on server.", "danger")
        return redirect(url_for("index_page"))
    if "voice_file" not in request.files:
        flash("No voice sample file part", "danger")
        return redirect(url_for("index_page"))
    file = request.files["voice_file"]
    voice_name = request.form.get("voice_name")
    if not voice_name:
        flash("Voice name is required.", "danger")
        return redirect(url_for("index_page"))
    if file.filename == "":
        flash("No selected file", "danger")
        return redirect(url_for("index_page"))
    if file and allowed_file(file.filename):
        secure_fn = secure_filename(file.filename)
        filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}_{secure_fn}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        try:
            file.save(file_path)
        except Exception as e:
            flash(f"Failed to save uploaded file: {str(e)}", "danger")
            return redirect(url_for("index_page"))
        cloned_voice_id_elevenlabs = elevenlabs_clone_voice(file_path, voice_name, ELEVENLABS_API_KEY)
        if cloned_voice_id_elevenlabs:
            try:
                new_cloned_voice_entry = ClonedVoice(
                    voice_id_elevenlabs=cloned_voice_id_elevenlabs,
                    name=voice_name,
                    user_id=current_user.id
                )
                db.session.add(new_cloned_voice_entry)
                db.session.commit()
                flash(f"Voice '{voice_name}' cloned successfully with ID: {cloned_voice_id_elevenlabs}!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Voice cloned with ElevenLabs, but failed to save to database: {str(e)}", "danger")
        else:
            flash("Failed to clone voice via ElevenLabs API.", "danger")
        return redirect(url_for("index_page"))
    else:
        flash("File type not allowed. Please upload MP3 or WAV.", "danger")
        return redirect(url_for("index_page"))

@app.route("/api/textfx_generate", methods=["POST"])
@login_required
def handle_textfx_generate():
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        return jsonify({"error": "Gemini API key not configured on server."}), 500
    data = request.get_json()
    input_text = data.get("text")
    effect_full_name = data.get("tool")
    if not input_text or not effect_full_name:
        return jsonify({"error": "Missing text or tool in request"}), 400
    
    creative_text_result = generate_text_effect(effect_full_name, input_text)
    
    if "Error:" in creative_text_result:
         return jsonify({"error": "Content generation issue", "details": creative_text_result}), 400
    
    effect_key = None
    for key, model_data in TEXTFX_MODELS.items():
        if effect_full_name == model_data["name"]:
            effect_key = key
            break
    
    output_type = TEXTFX_MODELS.get(effect_key, {}).get("output_type", "single_sentence") 

    processed_results = [{"text": creative_text_result}]

    return jsonify({"message": "Creative text generated successfully", "results": processed_results, "output_type": output_type}), 200

@app.route("/api/text_to_speech", methods=["POST"])
@login_required
def handle_text_to_speech():
    if not ELEVENLABS_API_KEY:
        return jsonify({"error": "ElevenLabs API key not configured on server."}), 500
    data = request.get_json()
    text_to_narrate = data.get("text")
    voice_id_to_use = data.get("voice_id")
    if not text_to_narrate or not voice_id_to_use:
        return jsonify({"error": "Missing text or voice_id in request"}), 400
    
    output_filename = f"speech_{voice_id_to_use.replace("-", "")[:8]}_{current_user.id}_{uuid.uuid4().hex[:6]}.mp3"
    output_path = os.path.join(app.config["GENERATED_AUDIO_FOLDER"], output_filename)
    
    generated_audio_file_path = elevenlabs_text_to_speech(text_to_narrate, voice_id_to_use, ELEVENLABS_API_KEY, output_path)
    
    if generated_audio_file_path:
        audio_url = url_for("serve_generated_audio", filename=output_filename, _external=False)
        return jsonify({"message": "Speech generated successfully", "audio_url": audio_url}), 200
    else:
        return jsonify({"error": "Failed to generate speech via ElevenLabs API."}), 500

@app.route("/generated_audio/<filename>")
@login_required
def serve_generated_audio(filename):
    return send_from_directory(app.config["GENERATED_AUDIO_FOLDER"], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

