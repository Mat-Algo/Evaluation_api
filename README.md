# 📝 Assignment Evaluation API

**Assignment Evaluation API** provides automated evaluation of student assignments, including detailed scoring, personalized feedback, and SWOT analysis, powered by Google Gemini LLM.

---

## 🚀 Features

* **Automated Scoring**: Assign scores per question on a 0–10 scale with correctness flags.
* **Personalized Feedback**: Constructive, human-like feedback highlighting strengths and improvement areas.
* **SWOT Analysis**: Generates overall Strengths, Weaknesses, Opportunities, and Threats summary.
* **Question Generation**: Create customized tests with specified question count, difficulty, and topics.
* **Alternative Questions**: Produce three distinct variations for any given subtopic.
* **Health Check**: Simple endpoint to verify service availability.

---

## 📦 Tech Stack

| Component          | Technology            | Role                                    |
| ------------------ | --------------------- | --------------------------------------- |
| **API Framework**  | FastAPI               | HTTP endpoints & request handling       |
| **LLM Client**     | Google Gemini (genai) | Prompt-based content generation         |
| **Serialization**  | Pydantic              | Data validation & modeling              |
| **Env Management** | python-dotenv         | Secure loading of environment variables |
| **Deployment**     | Render (render.yaml)  | Web service configuration & auto-deploy |

---

## 🔧 Installation

1. **Clone repository**

   ```bash
   git clone https://github.com/your-org/assignment-eval-api.git
   cd assignment-eval-api
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   Create a `.env` file with:

   ```env
   GEMINI_API_KEY=your_google_gemini_api_key
   ```

---

## 🚀 Running Locally

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔌 Environment Variables

| Name             | Description                      |
| ---------------- | -------------------------------- |
| `GEMINI_API_KEY` | API key for Google Gemini client |

---

## 🖇️ Deployment (Render)

Configure `render.yaml`:

```yaml
services:
  - type: web
    name: assignment-eval-api
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: bash start.sh
    envVars:
      - key: GEMINI_API_KEY
        sync: false
```

Deploy by linking to your GitHub repo in Render.

---

## 📖 API Endpoints

### 1. Evaluate Submission

**POST** `/evaluate`

* **Request Body** (`Submission`):

  ```json
  {
    "items": [
      {
        "question_id": "q1",
        "question": "What is photosynthesis?",
        "actual_answer": "Process by plants...",
        "expected_answer": "Conversion of light..."
      }
    ]
  }
  ```

* **Response** (`ScoreResponse`):

  ```json
  {
    "total_score": 8.5,
    "details": [
      {
        "question_id": "q1",
        "question": "What is photosynthesis?",
        "score": 8.5,
        "correct": true,
        "feedback": "Good description, add..."
      }
    ]
  }
  ```

### 2. SWOT Analysis

**POST** `/swot`

* **Request Body**: same as `/evaluate`
* **Response** (`SWOTResponse`):

  ```json
  {
    "strengths": "Your explanations are clear...",
    "weaknesses": "Missing detail on...",
    "opportunities": "Review chapter on...",
    "threats": "Watch for misconceptions..."
  }
  ```

### 3. Generate Questions

**POST** `/generate-qa`

* **Request Body** (`QuestionGenerationRequest`): specify title, subject, class, dates, question type, count, difficulty, topics, instructions, etc.
* **Response** (`QuestionGenerationResponse`):

  ```json
  {
    "questions": [
      {"question": "...", "expected_answer": "..."},
      ...
    ]
  }
  ```

### 4. Generate Alternatives

**POST** `/generate-alternatives`

* **Request Body** (`AlternativeRequest`): provide `id`, `subtopic`, `difficulty`, `marks`, etc.
* **Response**: list of three `AlternativeQuestion` objects.

### 5. Health Check

**GET** `/health-check`

* **Response**: `{ "status": "ok" }`

---

## 🛠️ Contributing

Contributions welcome! Please open issues or PRs, following the existing code style and adding tests as needed.

---

## 📄 License

MIT license
