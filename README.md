# 🩺 Medical Assistant

An AI-powered web application that assists doctors by **transcribing doctor-patient conversations**, extracting symptoms, and providing **diagnosis & prescription suggestions** using the **Gemini API**.  
The app also integrates **Retrieval-Augmented Generation (RAG)** with **FAISS** and **Sentence Transformers** to retrieve relevant medical knowledge from a local document base before generating responses.

---

## 🚀 Features
- **🎤 Audio Recording in Browser** – Record short doctor-patient interactions directly from the web UI.
- **📝 Speech-to-Text Transcription** – Converts recorded audio to text using SpeechRecognition and Google Web Speech API.
- **🧠 AI-Powered Diagnosis** – Uses Gemini API to provide diagnosis and prescription suggestions based on symptoms.
- **📄 RAG Integration** – FAISS-powered document retrieval from a small medical knowledge base for context-aware responses.
- **🌐 Full Web App** – Built with Flask backend and Jinja frontend for a seamless user experience.
- **⚡ Prompt Engineering** – Fine-tuned prompts to improve the accuracy and relevance of AI responses.

---

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **Frontend:** HTML (Jinja Templates), JavaScript
- **AI/ML:** Google Generative AI (Gemini API), FAISS, Sentence Transformers
- **Speech-to-Text:** SpeechRecognition, Google Web Speech API
- **Others:** HTML5 Audio Recording, CSS

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Thendralk/Med-Assistant.git
cd Med-Assistant
````

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Add API Keys

Create a `config.py` file:

```python
GOOGLE_API_KEY = "your_gemini_api_key"
```

### 5️⃣ Run the Application

```bash
python app.py
```

Visit: **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 🖥️ Usage

1. Open the app in your browser.
2. Click **🎤 Record Audio (5 sec)** to record doctor-patient conversation.
3. Wait for transcription to complete.
4. AI will process the transcription, retrieve relevant medical knowledge, and return a suggested diagnosis and prescription.

---

## 📄 Example Workflow

* Doctor: *"The patient has had a fever for 3 days with mild cough."*
* App Transcribes → `"Patient has fever for 3 days and mild cough"`
* Gemini API generates:

  > **Diagnosis:** Likely viral fever with mild respiratory infection.
  > **Prescription:** Paracetamol 500mg twice daily, hydration, rest. Follow up if fever persists beyond 3 days.

---

## 🏗️ Future Improvements

* ✅ Longer audio recording duration
* ✅ Real-time transcription while recording
* ✅ Integration with EHR systems
* ✅ Support for multiple languages

---

## 📜 License

This project is licensed under the MIT License. You are free to use, modify, and distribute it.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 👩‍💻 Author

**\[Thendral Kabilan]**
[GitHub Profile](https://github.com/Thendralk)
[LinkedIn](www.linkedin.com/in/thendral-kabilan)


