import eventlet
eventlet.monkey_patch()
from flask import Flask, Blueprint, render_template, request, session, jsonify, make_response
from flask_socketio import SocketIO
import os
import json
import pyaudio
import numpy
from datetime import datetime
import pickle
import pandas as pd
import plotly.express as px
import plotly.io as pio
import vosk
import webrtcvad
import google.generativeai as genai
import re


# ------------------------- Configuration -------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*", use_reloader=False)

# Load predictive model
with open('model/readmission_model.pkl', 'rb') as f:
    model_dict = pickle.load(f)
    risk_model = model_dict['model']
    risk_metadata = model_dict['metadata']

# Vosk model configuration
VOSK_MODEL_PATH = "./model/vosk-model-small-hi-0.22/vosk-model-small-hi-0.22"
assert os.path.exists(VOSK_MODEL_PATH), "❌ Vosk model path is missing!"
vosk_model = vosk.Model(VOSK_MODEL_PATH)
recognizer = vosk.KaldiRecognizer(vosk_model, 16000)
vad = webrtcvad.Vad()
vad.set_mode(2)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY")) 
audio_data = []
stream = None

# Load dataset for dropdown options (Risk Prediction)
df = pd.read_csv('./Datasets/hospital_readmissions.csv')
AGE_BRACKETS = sorted(df['age'].dropna().unique().tolist())
DIAGNOSES = ['Circulatory', 'Respiratory', 'Diabetes', 'Digestive', 'Injury', 'Musculoskeletal']
age_weights = {'[40-50)': 1, '[50-60)': 2, '[60-70)': 3, '[70-80)': 4, '[80-90)': 5, '[90-100)': 6}
diagnosis_weight = {'Circulatory': 2, 'Respiratory': 1.7, 'Diabetes': 1, 'Digestive': 0.8, 'Injury': 0.5, 'Musculoskeletal': 0.7}

# ------------------------- Blueprints -------------------------
risk_bp = Blueprint('risk', __name__, url_prefix='/risk')
notes_bp = Blueprint('notes', __name__, url_prefix='/notes')
symptom_bp = Blueprint('symptomchecker', __name__, url_prefix='/symptomchecker')
# ------------------------- Homepage -------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/documentation1')
def documentation1():
    return render_template('documentation1.html')

@app.route('/documentation2')
def documentation2():
    return render_template('documentation2.html')

@app.route('/documentation3')
def documentation3():
    return render_template('documentation3.html')


@app.route('/team')
def team():
    return render_template('team.html')



# ------------------------- AI Symptom Checker -------------------------
SYMPTOM_TO_SPECIALTY = {
    "fever": "General Physician",
    "cough": "Pulmonologist",
    "chest pain": "Cardiologist",
    "abdominal pain": "Gastroenterologist",
    "headache": "Neurologist",
    "sore throat": "ENT Specialist",
    "fatigue": "General Physician",
    "shortness of breath": "Pulmonologist",
    "joint pain": "Rheumatologist",
    "skin rash": "Dermatologist"
}

# Fallback triage logic
def get_triage_level(symptoms):
    urgent_keywords = ["chest pain", "shortness of breath", "severe headache"]
    moderate_keywords = ["fever", "abdominal pain", "joint pain"]
    
    symptoms = symptoms.lower()
    if any(keyword in symptoms for keyword in urgent_keywords):
        return "Urgent: Seek immediate medical attention."
    elif any(keyword in symptoms for keyword in moderate_keywords):
        return "Moderate: Consult a doctor within 24-48 hours."
    else:
        return "Mild: Monitor symptoms and consult if they persist."

# Fallback doctor recommendation
def get_doctor_recommendation(symptoms):
    symptoms = symptoms.lower().split(",")
    specialties = set()
    for symptom in symptoms:
        symptom = symptom.strip()
        for key, specialty in SYMPTOM_TO_SPECIALTY.items():
            if key in symptom:
                specialties.add(specialty)
    return list(specialties) if specialties else ["General Physician"]

# Call Gemini AI for symptom analysis in JSON format
def analyze_symptoms_with_gemini(symptoms, latitude=None, longitude=None):
    model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
    
    # Prompt 1: Default symptom analysis (no location)
    prompt_no_location = f"""
    Analyze the following symptoms: {symptoms}
    Provide the response in JSON format with the following structure:
    {{
        "triage_level": "string (e.g., 'Urgent: Seek immediate medical attention.', 'Moderate: Consult a doctor within 24-48 hours.', or 'Mild: Monitor symptoms and consult if they persist.')",
        "doctor_recommendations": ["string (specialty 1)", "string (specialty 2)", ...],
        "analysis": "string (brief description of possible conditions and advice)"
    }}
    Ensure the triage_level is one of the specified strings, and doctor_recommendations is a list of medical specialties.
    """

    # Prompt 2: Symptom analysis with location-based doctor recommendations
    prompt_with_location = f"""
    Analyze the following symptoms: {symptoms}
    Provide the response in JSON format with the following structure:
    {{
        "triage_level": "string (e.g., 'Urgent: Seek immediate medical attention.', 'Moderate: Consult a doctor within 24-48 hours.', or 'Mild: Monitor symptoms and consult if they persist.')",
        "doctor_recommendations": ["string (specialty and location-based doctor or clinic recommendation 1)", "string (specialty and location-based doctor or clinic recommendation 2)", ...],
        "analysis": "string (brief description of possible conditions and advice)"
    }}
    Ensure the triage_level is one of the specified strings. 
    For doctor_recommendations, please include medical specialties and specific doctor or clinic recommendations near the location (latitude: {latitude}, longitude: {longitude}). If no specific doctors are found, include only the relevant specialties.
    """

    # Choose prompt based on whether location is provided
    prompt = prompt_with_location if latitude and longitude else prompt_no_location

    try:
        response = model.generate_content(prompt)
        if response and response.text:
            # Clean up the response to extract JSON (Gemini may wrap it in ```json ... ```)
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            result = json.loads(response_text)
            
            # Validate JSON structure
            triage = result.get("triage_level", get_triage_level(symptoms))
            doctors = result.get("doctor_recommendations", get_doctor_recommendation(symptoms))
            analysis = result.get("analysis", "No analysis provided by AI.")
            return triage, doctors, analysis
        return get_triage_level(symptoms), get_doctor_recommendation(symptoms), "Unable to configure AI response."
    except Exception as e:
        # Fallback to rule-based logic on error
        return get_triage_level(symptoms), get_doctor_recommendation(symptoms), f"Error analyzing symptoms: {str(e)}"

@symptom_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        symptoms = request.form.get("symptoms")
        if not symptoms:
            return render_template("SymptomChecker.html", error="Please enter symptoms.")
        
        # Get location data if provided
        use_location = request.form.get("use_location")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        
        # Convert latitude and longitude to float if provided, else None
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except ValueError:
            latitude, longitude = None, None
        
        # Validate location data if use_location is checked
        if use_location and (not latitude or not longitude):
            return render_template("SymptomChecker.html", error="Location data is invalid or not provided. Please allow location access or uncheck 'Recommend Doctors near me'.")
        
        # Get triage level, doctor recommendations, and analysis from Gemini AI
        triage, doctors, analysis = analyze_symptoms_with_gemini(symptoms, latitude, longitude)
        
        return render_template(
            "SymptomChecker.html",
            symptoms=symptoms,
            triage=triage,
            doctors=doctors,
            analysis=analysis
        )
    
    return render_template("SymptomChecker.html")


# ------------------------- Predictive Patient Risk Routes -------------------------
def create_risk_chart(risk_score):
    fig = px.bar(
        x=['Risk Score'], y=[risk_score], 
        range_y=[0, 100], text=[f"{risk_score}/100"],
        title="Readmission Risk Score"
    )
    fig.update_traces(marker_color=['#e74c3c' if risk_score >= 70 else '#f39c12' if risk_score >= 30 else '#2ecc71'])
    fig.update_layout(yaxis_title="Score", showlegend=False)
    return pio.to_html(fig, full_html=False)

def create_feature_importance_chart(factors):
    df_factors = pd.DataFrame(factors)
    df_factors['impact_num'] = df_factors['impact'].str.replace('%', '').astype(float)
    df_factors = df_factors.sort_values('impact_num', ascending=True)
    fig = px.bar(
        df_factors, x='impact_num', y='explanation', orientation='h',
        title="Contributing Factors", labels={'impact_num': 'Impact (%)', 'explanation': 'Factor'},
        text='impact'
    )
    fig.update_traces(marker_color='#3498db', textposition='outside', texttemplate='%{text}%')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis={'range': [0, df_factors['impact_num'].max() + 5]}, hovermode='y', margin={'l': 150})
    return pio.to_html(fig, full_html=False)

def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default
@risk_bp.route('/', methods=['GET', 'POST'])
def risk_form():
    return render_template('form.html', age_brackets=AGE_BRACKETS, diagnoses=DIAGNOSES)

@risk_bp.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            age_raw = request.form.get('age', '')
            diagnosis_raw = request.form.get('primary_diag')
            age = age_weights.get(age_raw, 1.0)
            diag_weight = diagnosis_weight.get(diagnosis_raw, 1.0)
            time_in_hospital = safe_int(request.form.get('time_in_hospital'))
            n_emergency = safe_int(request.form.get('n_emergency'))
            total_visits = safe_int(request.form.get('total_visits'))
            n_medications = safe_int(request.form.get('n_medications'))

            patient_data = {
                'age_time_in_hospital': age * time_in_hospital,
                'age_time_in_hospital_medication': age * time_in_hospital * n_medications * 0.5,
                'age_diagnosis': age * diag_weight,
                'age_emergency_visits': age * n_emergency,
                'age_total_visits': age * total_visits
            }

            df_input = pd.DataFrame([patient_data])
            probability = risk_model.predict_proba(df_input)[0][1]
            risk_score = int(probability * 100)

            feature_importances = dict(zip(risk_metadata['features'], risk_model.feature_importances_))

            explanations = {
                'age_time_in_hospital': lambda v: f"Age-weighted hospital stay: {v}",
                'age_time_in_hospital_medication': lambda v: f"Age-weighted medication load: {v}",
                'age_diagnosis': lambda v: f"Age-weighted diagnosis: {v}",
                'age_emergency_visits': lambda v: f"Age-weighted emergency visits: {v}",
                'age_total_visits': lambda v: f"Age-weighted total visits: {v}"
            }

            factor_analysis = []
            for feature, value in patient_data.items():
                importance = feature_importances.get(feature, 0)
                if importance > 0.01:
                    explanation = explanations.get(feature, lambda v: f"{feature}: {v}")(value)
                    factor_analysis.append({
                        'factor': feature,
                        'value': value,
                        'importance': float(importance),
                        'explanation': explanation,
                        'impact': f"{importance * 100:.1f}%"
                    })

            risk_chart = create_risk_chart(risk_score)
            importance_chart = create_feature_importance_chart(factor_analysis) if factor_analysis else "<p>No contributing factors to display.</p>"

            return render_template('result.html',
                                   patient_data=patient_data,
                                   probability=probability,
                                   risk_score=risk_score,
                                   factors=factor_analysis[:10],
                                   top_3_factors=factor_analysis,
                                   risk_chart=risk_chart,
                                   importance_chart=importance_chart)
        except Exception as e:
            print(f"Prediction Error: {e}")
            return render_template('form.html', error=str(e), age_brackets=AGE_BRACKETS, diagnoses=DIAGNOSES)

# ------------------------- Automated Clinical Notes Routes -------------------------

@notes_bp.route('/', methods=['GET'])
def notes():
    return render_template('notes.html')


def generate_medical_notes(transcript):
    today = datetime.today().date().isoformat()
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    Based on the following doctor-patient conversation, generate a JSON output with this format (tip: Prescribe medicines and give diagonosis by your own intelligence by understanding conversation):
    {{
      "patient_info": {{
        "age": "value_or_null",
        "name": "value_or_null",
        "Dateofvisit": "{today}"
      }},
      "ClinicalNotes": {{
        "ChiefComplaint": "value_or_null",
        "HistoryofPresentIllness": "value_or_null",
        "Diagnosis": "value_or_null",
        "Medicines": [
          {{
            "name": "value_or_null",
            "dosage": "value_or_null",
            "frequency": "value_or_null",
            "duration": "value_or_null",
            "reason": "value_or_null"
          }}
        ]
      }}
    }}
    Conversation: {transcript}
    """
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            print(f"📝 Raw AI response: {response.text}")  # Log raw response
            cleaned_text = re.sub(r'^```json\s*|\s*```$', '', response.text, flags=re.MULTILINE).strip()
            print(f"📝 Cleaned AI response: {cleaned_text}")  # Log cleaned response
            try:
                return json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}, Response: {cleaned_text}")
                return {"error": f"Invalid JSON response from AI: {cleaned_text}"}
        return {"error": "AI response unavailable"}
    except Exception as e:
        print(f"❌ Error generating medical notes: {e}")
        return {"error": f"Error generating notes: {e}"}
    
@socketio.on('start_Recording')
def handle_start_call():
    global stream
    if stream is None:
        print("🎤 Transcription started...")
        stream = pyaudio.PyAudio().open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000
        )
        socketio.start_background_task(target=convo_detection)

def is_speech(chunk):
    try:
        return vad.is_speech(chunk, sample_rate=16000)
    except:
        return True

def convo_detection():
    global stream
    try:
        while stream is not None:
            data = stream.read(2000, exception_on_overflow=False)
            if not data or not is_speech(data):
                continue
            audio_data.append(data)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    print(f"📝 Recognized: {text}")
                    socketio.emit('transcription_update', {'text': text})
            eventlet.sleep(0.001)
    except Exception as e:
        print(f"❌ Error in voice detection: {e}")

@socketio.on('stop_Recording')
def handle_stop_call():
    global stream, audio_data
    if stream:
        stream.stop_stream()
        stream.close()
        stream = None
    socketio.emit('main_task_initialised')
    print("🛑 Transcription stopped.")
    final_transcript = []
    for data in audio_data:
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                final_transcript.append(text)
    transcript = " ".join(final_transcript)
    audio_data = []
    print(f"📋 Final transcript: {transcript}")
    if not transcript.strip():
        print("⚠️ Empty transcript. Skipping AI processing.")
        socketio.emit('transcription_error', {'transcript': "", 'notes': "No valid transcription."})
        return
    structured_notes = generate_medical_notes(transcript)
    socketio.emit('transcription_complete', structured_notes)

@notes_bp.route('/display_result', methods=['POST', 'GET'])
def display_result():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        session['result'] = data
        session.modified = True
        return jsonify({'success': True})
    else:  # GET
        result = session.get('result', {})
        return render_template('notes_result.html', result=result)
    

    
@notes_bp.route('/save_patient_info', methods=['POST'])
def save_patient_info():
    try:
        data = request.get_json()
        patient_info = data.get('patient_info', {})
        if not patient_info:
            return jsonify({'success': False, 'error': 'No patient info provided'}), 400
        session['result'] = session.get('result', {})
        session['result']['patient_info'] = {
            'name': patient_info.get('name', None),
            'age': patient_info.get('age', None),
            'Dateofvisit': patient_info.get('Dateofvisit', None)
        }
        session.modified = True
        return jsonify({'success': True, 'patient_info': session['result']['patient_info']})
    except Exception as e:
        print(f"❌ Error saving patient info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notes_bp.route('/save_clinical_notes', methods=['POST'])
def save_clinical_notes():
    try:
        data = request.get_json()
        clinical_notes = data.get('ClinicalNotes', {})
        if not clinical_notes:
            return jsonify({'success': False, 'error': 'No clinical notes provided'}), 400
        session['result'] = session.get('result', {})
        session['result']['ClinicalNotes'] = {
            'ChiefComplaint': clinical_notes.get('ChiefComplaint', None),
            'HistoryofPresentIllness': clinical_notes.get('HistoryofPresentIllness', None),
            'Diagnosis': clinical_notes.get('Diagnosis', None),
            'Medicines': clinical_notes.get('Medicines', None)
        }
        session.modified = True
        return jsonify({'success': True, 'ClinicalNotes': session['result']['ClinicalNotes']})
    except Exception as e:
        print(f"❌ Error saving clinical notes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Register Blueprints
app.register_blueprint(risk_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(symptom_bp)

if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    socketio.run(app, debug=False, port=5000)
