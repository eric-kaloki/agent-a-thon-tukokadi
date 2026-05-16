# TukoKadi: Gamified Civic Education AI 🗳️

![TukoKadi UI Preview](ui_preview.png) *(Placeholder for actual screenshot/demo link)*

**TukoKadi** is a multi-agent civic participation system built for the Kenya Special Challenge. It acts as the trusted front door for every Kenyan voter, providing real-time, verified civic education, polling station location, and fact-checking, all delivered through a fun, gamified experience.

## 🎯 The Problem We Are Solving

Many voters, especially first-timers or those from marginalized areas, know they are registered but feel lost about the actual voting process, their constitutional rights, or how to identify misinformation. Traditional civic education can be bureaucratic, dry, or inaccessible. 

TukoKadi bridges this gap by offering a warm, conversational AI that speaks the user's language (English, Kiswahili, or Sheng), gamifies learning to encourage continuous engagement (XP, levels, and badges), and provides instant, verified answers based strictly on the Kenyan Constitution and IEBC guidelines.

## 🧠 Agent Architecture

TukoKadi uses a hub-and-spoke multi-agent architecture built with the **Google Agent Development Kit (ADK)** and powered by **Gemini 2.5 Pro/Flash**.

### 1. The Root Orchestrator: Msaidizi
*   **Role**: The welcoming front door. Understands user intent, detects language, and routes the query to the correct specialist agent without answering substantive questions itself.
*   **Sub-Agents**: Routes to Mwalimu, Mwenza, Kiongozi, or Ukweli.

### 2. The Specialists
*   **Mwalimu (Civic Education)**: A gamified teacher that quizzes users on constitutional rights, tracks XP/streaks, and awards badges. 
*   **Mwenza (Election Day Guide)**: Provides quick, practical USSD-style answers about what to bring, voting hours, and how to report issues.
*   **Kiongozi (Polling Locator)**: Helps voters find their assigned polling station based on their County and Ward.
*   **Ukweli (Misinformation Fact-Checker)**: Evaluates claims and images against official IEBC and Constitutional sources, returning a strict VERIFIED, FALSE, or UNVERIFIED verdict.

### 🛠️ Tools Used
Every specialist agent is equipped with the `VertexAiSearchTool`, connected directly to a curated data store of official Kenyan civic documents (`kenya-civic-docs-ds_1778928130432`). This ensures 100% citation-backed responses and prevents hallucination.

---

## 🚀 How to Run Locally

1. **Clone the Repository**:
   ```bash
   git clone <your-repo-url>
   cd tukokadi
   ```

2. **Set up the Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Authenticate with Google Cloud**:
   Ensure you have access to the GCP project hosting the Vertex AI Search datastore.
   ```bash
   gcloud auth application-default login
   gcloud auth application-default set-quota-project charged-polymer-443312-t9
   ```

4. **Start the Server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```

5. **View the App**:
   Open `http://localhost:8080` in your web browser.

---

## 🌍 How to Interact with the Deployed Version

*   **Web Interface**: Visit our production URL (e.g., `https://tukokadi-xxxx.a.run.app`) to experience the premium chat interface, complete with real-time gamification progress (XP and Levels).
*   **WhatsApp (Simulation)**: The system includes a plug-and-play webhook at `/whatsapp/webhook`. You can test it using a REST client (like Postman) by sending a `POST` request with form data `Body="CHANGAMOTO"` and `From="+254700000000"`.

---

## 👥 Team

*   **Eric Kaloki**
*   **Jame Kilonzo**
*   **Maurice Ochola**
*   **Dancan Onduso**
