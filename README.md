Aarogya - Cyfuture Hackathon
Aarogya is an innovative healthcare portal designed to enhance patient care through artificial intelligence and machine learning. Aarogya streamlines healthcare workflows with features tailored for patients and providers. This repository contains the deployed version of the app, hosted on Render’s free tier, while the Cyfuture-Hackathon repository includes the complete prototype with all dependencies, including the Vosk speech-to-text model.
Features

Symptom Checker (Live): Powered by Google Gemini AI, this feature analyzes user-reported symptoms to provide potential diagnoses, enhancing patient accessibility to health insights.
Predictive Patient Risk Models (Live): Utilizes a machine learning model (RandomForestClassifier) to predict hospital readmission risks based on patient data, supporting proactive care.
Automated Clinical Documentation (Live): Simulates note-taking with text input in the live demo, replacing speech-to-text due to Render’s limitations. The full speech-to-text feature, using Vosk, is demoed locally (see below).
Team Page (Live): Introduces the Aarogya development team.

Demo Video
Watch our demo video to see the full functionality of Aarogya, including the speech-to-text feature running locally with Vosk, alongside the live app’s features.
Why Speech-to-Text is Demoed Locally
The Automated Clinical Documentation feature uses the Vosk speech-to-text model, which requires PyAudio and the PortAudio C library. Render’s free tier does not support installing system-level libraries like PortAudio, preventing PyAudio from being deployed. To ensure a functional live demo, we implemented a text input interface for clinical notes at /notes. The NLP Explanation page details this workaround. The full speech-to-text capability is showcased in our local demo video, available in the Cyfuture-Hackathon repository.


Local Demo
To run the app locally, including the speech-to-text feature:

Clone the Repository:
git clone https://github.com/<your-username>/Cyfuture-Hackathon.git
cd Cyfuture-Hackathon


Install Dependencies:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install vosk pyaudio


Run the App:
python app.py


Access http://127.0.0.1:5000/notes to test speech-to-text.
Ensure model/vosk-model-hi-0.22 is present.



Screenshots

Technical Details

Frontend: Flask, Tailwind CSS (blue/white/gray healthcare theme).
Backend: Python, Flask, scikit-learn (RandomForestClassifier), Google Gemini AI.
Deployment: Render free tier, with Gunicorn.
NLP: Vosk speech-to-text (local demo), mocked with text input online.
Model: Pre-trained readmission_model.pkl for hospital readmission predictions.
Constraints: Render’s free tier lacks PortAudio, limiting PyAudio deployment.

Cyfuture-Hackathon Repository
The Cyfuture-Hackathon repository contains the full prototype, including:

All source files.
Vosk model (vosk-model-small-hi-0.22).
Dependencies for local speech-to-text testing.
Additional datasets or scripts used during development.

Team
Aarogya was developed by a dedicated team of innovators. Visit our Team Page to learn more.
Acknowledgments
Thank you to the Cyfuture Hackathon organizers for this opportunity to showcase Aarogya. We hope our solution demonstrates the potential of AI in healthcare.
