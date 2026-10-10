# NatureQuest AI 🌿
> *"A little less scrolling. A little more exploring."*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Hacktoberfest](https://img.shields.io/badge/Hacktoberfest-Touch%20Grass%20Challenge-orange.svg)](https://hacktoberfest.com/)
[![Model](https://img.shields.io/badge/AI%20Engine-Gemma%20Open--Weights-blue.svg)](https://ai.google.dev/gemma)
[![Python](https://img.shields.io/badge/Python-3.11%2B-brightgreen.svg)](https://python.org)

NatureQuest AI is an open-source, distraction-free outdoor companion application built for the **Hacktoberfest Open-Source AI Challenge Week 1: "Touch Grass"**.

---

## 1. Project Overview & Problem Statement

Modern algorithms are engineered to maximize screen time, capture attention, and keep users indoors scrolling infinite feeds. This screen saturation directly contributes to digital fatigue, sedentary routines, and detachment from immediate surroundings.

**NatureQuest AI flips this dynamic:**
Instead of trapping you in an open-ended chatbot conversation, NatureQuest AI uses Google's open-weights **Gemma** model to generate a **finite, structured, actionable micro-mission** tailored to your immediate environment (parks, gardens, university campuses, or neighborhood streets in India and worldwide). Once your mission is ready, the app switches to an **Outdoor Mode** that prompts you to silence notifications, slip your phone into your pocket, and explore the living world with your actual senses.

---

## 2. Key Features

- **Editorial Nature Aesthetic:** Designed with a calm editorial palette (deep forest green, warm ivory, soft sage, earthy amber) and accessible typography.
- **Parametric Mission Generator:** Customize by:
  - **Environment:** Neighborhood, Public Park, Garden, Campus, or Trail.
  - **Available Time:** 10, 15, or 30 minutes.
  - **Difficulty:** Easy (relaxed noticing), Moderate (active searching), or Adventurous (micro-detective).
  - **Interests:** Plants & leaves, birds & calls, insects & pollinators, trees & bark, weather, or mindful silence.
  - **Custom Focus:** Optional short notes (e.g., "after rain scent", "balcony plants").
- **Strict JSON Contract & Schema Validation:** Backend enforces structured outputs including actionable tasks, sensory observation tips, safety reminders, and reflection questions.
- **Distraction-Free Outdoor Mode:**
  - One task at a time with large readable text.
  - Step-by-step progress tracking.
  - Explicit low-screen instructions and safety reminders.
- **Local Privacy & Reflection:**
  - Save personal field notes in browser storage (`localStorage`).
  - **Zero accounts, zero tracking cookies, zero personal data harvesting.**
  - Clear notice that clearing browser data removes local notes.
- **Honest Resilience & Fallbacks:**
  - Live model status badge in navigation bar.
  - If the AI API is unconfigured or unavailable, serves a curated, clearly-labeled **Sample Mission** so the application is always demonstrable. It *never* pretends a fallback came from Gemma.

---

## 3. Screenshots

<!-- Screenshots section with clear placeholders and captions -->

| Screen 1: Landing & Generator | Screen 2: Mission Briefing |
| :---: | :---: |
| ![Landing Page Placeholder](https://raw.githubusercontent.com/placeholder-user/naturequest-ai/main/screenshots/generator.png)<br><sub>*Customizable environment, time, difficulty, and interests.*</sub> | ![Briefing Placeholder](https://raw.githubusercontent.com/placeholder-user/naturequest-ai/main/screenshots/briefing.png)<br><sub>*Structured mission overview with low-screen protocol.*</sub> |

| Screen 3: Outdoor Mode | Screen 4: Field Notes & Reflection |
| :---: | :---: |
| ![Outdoor Mode Placeholder](https://raw.githubusercontent.com/placeholder-user/naturequest-ai/main/screenshots/outdoor_mode.png)<br><sub>*Distraction-free step-by-step field companion.*</sub> | ![Reflection Placeholder](https://raw.githubusercontent.com/placeholder-user/naturequest-ai/main/screenshots/reflection.png)<br><sub>*Post-walk contemplation and private browser notes.*</sub> |

*(Tip: Take real screenshots once running locally and place them in a `screenshots/` directory).*

---

## 4. Architecture

```
naturequest-ai/
├── app.py                 # Flask server, route controllers, validation, and error handling
├── ai_service.py          # Dedicated Gemma AI integration, prompt contract, JSON validation
├── requirements.txt       # Production & dev dependencies (Flask, google-genai, gunicorn, etc.)
├── render.yaml            # Blueprint for zero-friction Render deployment
├── pytest.ini             # Pytest configuration
├── .env.example           # Documented template for environment variables
├── .gitignore             # Git ignore rules for virtual environments and secrets
├── LICENSE                # MIT License
├── templates/
│   └── index.html         # Semantic HTML5 template with all interactive view states
├── static/
│   ├── style.css          # Editorial CSS, responsive layout, dark/light nature tokens
│   └── app.js             # Vanilla JS for form handling, outdoor mode, and local storage
└── tests/
    └── test_app.py        # Automated test suite (health, validation, fallbacks, mocks)
```

---

## 5. How Gemma Is Used

NatureQuest AI uses Google's open-weights **Gemma** model (`gemma-3-4b-it` by default, or other supported Gemma variants like `gemma-2-9b-it`).

### Hosted Inference vs. Local Weights
- **Current Implementation:** Uses hosted inference via the official `google-genai` Python SDK. This provides instant startup, minimal RAM requirements on free-tier cloud environments (like Render), and rapid response times.
- **Why Open-Weights Matter:** Gemma's weights are freely available under open terms. Unlike closed proprietary models where developers are locked into a single provider's walled garden, open-weight models give developers architectural autonomy. If an organization requires air-gapped security, zero external network calls, or offline edge devices, the exact same prompts and schema can run locally via Ollama, llama.cpp, or vLLM.
- **Note on Capabilities:** Gemma is used strictly for imaginative, structured outdoor activity ideation. The model is explicitly constrained **not** to hallucinate live weather, predict precise GPS coordinates, or claim real-time botanical identification.

### Swapping or Upgrading the Model
You can change the model via the `GEMMA_MODEL_ID` environment variable:
```bash
# In your .env or Render dashboard:
GEMMA_MODEL_ID=gemma-3-12b-it
# or
GEMMA_MODEL_ID=gemma-2-9b-it
```

---

## 6. Local Setup Instructions (macOS / Linux)

### Prerequisites
- Python 3.11+ installed (`python3 --version`)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/naturequest-ai.git
cd naturequest-ai
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy the example file:
```bash
cp .env.example .env
```
Edit `.env` and add your Google AI Studio API key (free tier available at [Google AI Studio](https://aistudio.google.com/)):
```ini
PORT=5001
GEMINI_API_KEY=your_actual_api_key_here
GEMMA_MODEL_ID=gemma-3-4b-it
```
*(Note: If you don't provide an API key, the app runs gracefully in **Sample Fallback Mode**).*

### 5. Run the application
```bash
python3 app.py
```
Open your browser and visit: **http://127.0.0.1:5001**

---

## 7. Running Tests

The test suite validates the health endpoint, input constraints, JSON validation, and error recovery using mocked responses (no live API key required):

```bash
pytest
```
Expected output:
```
tests/test_app.py .......... [100%]
======================== 10 passed in 0.50s ========================
```

---

## 8. Deployment on Render

This repository includes a `render.yaml` blueprint ready for zero-downtime deployment on [Render](https://render.com/).

### Step-by-Step Deployment:
1. Push your repository to **GitHub**.
2. Log in to [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** > **Web Service**.
4. Connect your GitHub repository `naturequest-ai`.
5. Configure the service:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60`
6. Under **Environment Variables**, add:
   - `GEMINI_API_KEY` = *(your Google AI Studio key)*
   - `GEMMA_MODEL_ID` = `gemma-3-4b-it`
7. Click **Create Web Service**.
8. Once the build finishes, verify the public URL and test `/api/health`.

---

## 9. Privacy, Safety, and Limitations

- **Privacy First:** No user accounts, cookies, or tracking pixels. Mission progress and field notes are stored strictly in the user's browser `localStorage`.
- **Physical Safety:** Missions explicitly instruct users to watch traffic, respect private property, stay hydrated, and never ingest wild plants.
- **Offline Limitations:** This deployment uses cloud inference for mission creation. True offline generation requires downloading model weights onto an edge device (e.g. Raspberry Pi or local laptop via Ollama).
- **Botanical Accuracy:** The app does not claim to identify real-time plant diseases or wild mushrooms; it promotes observational curiosity and mindfulness.

---

## 10. Why Open Innovation Matters (Touch Grass Theme)

Open innovation in AI is crucial because it decentralizes creative power. When models like **Gemma** are accessible as open weights, developers worldwide can build applications that serve human wellbeing rather than extractive commercial metrics. NatureQuest AI demonstrates that artificial intelligence doesn't have to trap people inside a feedback loop—it can be a gentle catalyst that reminds us of the living earth right outside our doorstep.

---

## 11. Future Improvements

- [ ] Web Speech API integration for optional audio-guided missions without touching the screen.
- [ ] Direct offline edge execution via WebGPU or local Ollama endpoint.
- [ ] Community printable "Nature Bingo" cards for schools and kids.
- [ ] Multilingual prompts in Hindi, Spanish, French, and regional languages.

---

## 12. License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
