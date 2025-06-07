# Aarogya - Cyfuture Hackathon

Aarogya is an innovative healthcare portal designed to enhance patient care through artificial intelligence and machine learning. Developed for the Cyfuture Hackathon, Aarogya streamlines healthcare workflows with features tailored for patients and providers. 

## Features

 ### Automated Clinical Documentation:
 
 The Automated Clinical Documentation app uses voice recognition and NLP to generate structured clinical notes from doctor-patient conversations. It streamlines documentation, reducing administrative burden for   healthcare providers.

- ***Documentation:*** https://aarogya-hackathon.onrender.com/documentation3
- Note: Render’s free tier may experience \~30-second cold starts after inactivity.

- ***demo Video:***
   




https://github.com/user-attachments/assets/3fe6b3b7-150f-41b1-bf55-aca1d0e3d669



#

### Symptom Checker
Powered by Google Gemini AI, this feature analyzes user-reported symptoms to provide potential diagnoses, enhancing patient accessibility to health insights.

- ***Documentation:*** https://aarogya-hackathon.onrender.com/documentation1
- Note: Render’s free tier may experience \~30-second cold starts after inactivity.

- ***demo Video:***
   

https://github.com/user-attachments/assets/6ea957e5-c009-4c1c-a48f-b6448838b430


#

### Predictive Patient Risk Models :
Utilizes a machine learning model (`RandomForestClassifier`) to predict hospital readmission risks based on patient data, supporting proactive care.

- ***Documentation:*** https://aarogya-hackathon.onrender.com/documentation2
- Note: Render’s free tier may experience \~30-second cold starts after inactivity.

- ***demo Video:***
  

https://github.com/user-attachments/assets/431d1b27-2d82-41b0-8cc0-a03af5a8fca4


#

## Setup Instructions

### Live Demo

- Visit https://aarogya-hackathon.onrender.com.
- Note: Render’s free tier may experience \~30-second cold starts after inactivity.

### Local Demo

To run the app locally, including the speech-to-text feature:

 1. **Clone the Repository**:

    ```bash
    git clone https://github.com/shreyash729/Cyfuture-Hackathon.git
    cd Cyfuture-Hackathon
    ```


2. **creates a virtual environment**:
   ```bash
   python -m venv venv
   ```
3. **Set Up Gemini Api Key**:
   ```bash
   set GOOGLE_API_KEY=YOUR_GEMINI_API_KEY   # replace it with your api key
   ```
4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

 4. **Run the App**:

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
