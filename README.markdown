# Aarogya - Cyfuture Hackathon

Aarogya is an innovative healthcare portal designed to enhance patient care through artificial intelligence and machine learning. Developed for the Cyfuture Hackathon, Aarogya streamlines healthcare workflows with features tailored for patients and providers. 

## Features

- **Automated Clinical Documentation** (Working on local machine) : The Automated Clinical Documentation app uses voice recognition and NLP to generate structured clinical notes from doctor-patient conversations. It streamlines documentation, reducing administrative burden for healthcare providers.

- ***Documentation:*** https://aarogya-hackathon.onrender.com/documentation3

- ***demo Video:***
   [Watch Demo Video](/notes.mp4)


- **Symptom Checker** (Live): Powered by Google Gemini AI, this feature analyzes user-reported symptoms to provide potential diagnoses, enhancing patient accessibility to health insights.

- ***Documentation:*** https://aarogya-hackathon.onrender.com/documentation1

- ***demo Video:***
   [Watch Demo Video](/symptoms.mp4)
#

- **Predictive Patient Risk Models** (Live): Utilizes a machine learning model (`RandomForestClassifier`) to predict hospital readmission risks based on patient data, supporting proactive care.

- ***Documentation:*** https://aarogya-hackathon.onrender.com/documentation2

- ***demo Video:***
   [Watch Demo Video](/readmission%20risk.mp4)
#
  



## Why Speech-to-Text is Demoed Locally

The Automated Clinical Documentation feature uses the Vosk speech-to-text model, which requires PyAudio and the PortAudio C library. Render’s free tier does not support installing system-level libraries like PortAudio, preventing PyAudio from being deployed. To ensure a functional live demo, we implemented a text input interface for clinical notes at `/notes`. The NLP Explanation page details this workaround. The full speech-to-text capability is showcased in our local demo video, available in the Cyfuture-Hackathon repository.

## Setup Instructions

### Live Demo

- Visit https://aarogya-hackathon.onrender.com.
- Note: Render’s free tier may experience \~30-second cold starts after inactivity.

### Local Demo

To run the app locally, including the speech-to-text feature:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/<your-username>/Cyfuture-Hackathon.git
   cd Cyfuture-Hackathon
   ```

2. **Install Dependencies**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install vosk pyaudio
   ```

3. **Run the App**:

   ```bash
   python app.py
   ```

   - Access `http://127.0.0.1:5000/` 
   - Ensure `model/vosk-model-small-hi-0.22` is present.
   - Replace `vosk-model-small-hi-0.22` with `vosk-model-hi-0.22` for better Accuracy
   - Download Vosk NLP model from `https://alphacephei.com/vosk/models`

## Screenshot

![Home Page](/homepage.png)



- **Frontend**: Flask, Tailwind CSS (blue/white/gray healthcare theme).
- **Backend**: Python, Flask, scikit-learn (RandomForestClassifier), Google Gemini AI.
- **Deployment**: Render free tier, with Gunicorn.
- **NLP**: Vosk speech-to-text (local demo), mocked with text input online.
- **Model**: Pre-trained `readmission_model.pkl` for hospital readmission predictions.
- **Constraints**: Render’s free tier lacks PortAudio, limiting PyAudio deployment.



## References

### NLP model:
 Small model (Lesser Accuracy): [vosk-model-small-hi-0.22](https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip)

 For Better Accuracy: [vosk-model-hi-0.22](https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip)

### DataSet:
 [kaggle dataset](https://www.kaggle.com/datasets/dubradave/hospital-readmissions/data)