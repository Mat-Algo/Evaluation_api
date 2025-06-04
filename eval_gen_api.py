import os
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(
    title="Assignment Evaluation API",
    description="Evaluate student assignments and provide SWOT analysis using Gemini LLM",
    version="1.0.0"
)

# Pydantic models
class QuestionItem(BaseModel):
    question_id: str
    question: str
    actual_answer: str
    expected_answer: str

class Submission(BaseModel):
    items: List[QuestionItem]

class ScoreDetail(BaseModel):
    question_id: str
    question: str
    score: float  
    correct: bool
    feedback: str
    
class ScoreResponse(BaseModel):
    total_score: float
    details: List[ScoreDetail]


class SWOTResponse(BaseModel):
    strengths: str
    weaknesses: str
    opportunities: str
    threats: str

class QuestionGenerationRequest(BaseModel):
    title: str
    subject: str
    class_: str  # `class` is a reserved keyword
    start_date: str
    end_date: str
    question_type: str
    number_of_questions: int
    difficulty: str
    topics: str
    instructions: str
    description: str
    max_score: int
    passing_score: int

class GeneratedQuestion(BaseModel):
    question: str
    expected_answer: str

class QuestionGenerationResponse(BaseModel):
    test_title: str
    subject: str
    class_: str
    questions: List[GeneratedQuestion]

def build_question_generation_prompt(payload: QuestionGenerationRequest) -> str:
    return f"""
You are a highly experienced school teacher tasked with creating a test.

Please generate {payload.number_of_questions} **{payload.question_type}** questions based on the topic **{payload.topics}**, for the subject **{payload.subject}**, targeted at **{payload.class_}** students. The difficulty should be **{payload.difficulty}** level.

Make sure the questions:
- Are clear and age-appropriate.
- Do NOT repeat the same concept.
- Follow these instructions: {payload.instructions}

For each question, provide an expected answer clearly. Return the output as a JSON array with fields:
- `question`: the full question text.
- `expected_answer`: the correct answer to that question. 

### Example format:
[
  {{
    "question": "What is ...?",
    "expected_answer": "..."
  }},
  ...
]

ONLY return a valid JSON array and nothing else. Now generate the questions:
    """

def build_evaluation_prompt(items: List[QuestionItem]) -> str:
    prompt = (
        """
        You are an expert teacher with deep knowledge in the subject matter. Evaluate the following student responses to a set of questions. For each response, provide a detailed assessment by:
        Assigning a score out of 0-10 based on accuracy, completeness, and clarity.
        Indicating whether the answer is correct (True) or incorrect (False).
        Providing customized, constructive feedback that highlights strengths, identifies errors or gaps, and offers specific guidance for improvement. Make sure it sounds very natural and personalised like an actual person would advise.
        Return the evaluation as a JSON array, where each object contains the fields: question (the question text or identifier), score (integer from 0 to 10), correct (boolean), and feedback (a string with detailed feedback). Ensure the feedback is clear, encouraging, and actionable.
        """
    )
    for idx, item in enumerate(items, 1):
        prompt += f"{idx}. Question: {item.question}\n"
        prompt += f"Student Answer: {item.actual_answer}\n"
        prompt += f"Expected Answer: {item.expected_answer}\n\n"
    return prompt

# Endpoint 1: evaluation
@app.post("/evaluate", response_model=ScoreResponse)
async def evaluate(submission: Submission):
    prompt = build_evaluation_prompt(submission.items)
    try:
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        content = resp.text
        if content.strip().startswith("```"):
            lines = content.strip().splitlines()
            content = "\n".join(lines[1:-1])

        raw = json.loads(content)
        total = 0.0
        details = []

        # Match each returned entry to the original submission item by index
        for entry, original_item in zip(raw, submission.items):
            score = float(entry.get("score", 0))
            correct = bool(entry.get("correct", False))
            feedback = entry.get("feedback", "")
            question = entry.get("question", "")

            details.append(ScoreDetail(
                question_id=original_item.question_id,  # add this line
                question=question,
                score=score,
                correct=correct,
                feedback=feedback
            ))
            total += score

        return ScoreResponse(total_score=total, details=details)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
def build_swot_prompt(items: List[QuestionItem]) -> str:
    context = "\n".join(
        f"Question: {item.question}\nStudent Answer: {item.actual_answer}\nExpected Answer: {item.expected_answer}\n"
        for item in items
    )
    prompt = (
        """
You are an educational expert with extensive experience in student assessment and performance analysis.

Review the following set of student responses (along with the expected answers) and provide a ingle, overall SWOT analysis summarizing the student's overall performance — not per question.

Focus on:
- **Strengths**: What are the overall areas where this student shows strong understanding or skill across the test? Provide general patterns and examples.
- **Weaknesses**: What general mistakes, gaps, or weaknesses appear across the responses?
- **Opportunities**: What can this student do to improve overall? Suggest strategies, resources, or approaches they can take.
- **Threats**: Are there any risks or challenges (like misconceptions, bad habits, or external issues) that might limit their progress?

- Make sure that the analysis is very helpful, natural and very human like as if how a real person would advice and not robotic
- Also always use "you" instead of student should do this,etc. Make it sound personalised to that particular person

RETURN FORMAT:
Return the SWOT analysis as a single JSON object with these four keys:
- strengths (string)
- weaknesses (string)
- opportunities (string)
- threats (string)

Be detailed, constructive, and base your analysis on overall trends, not per-question breakdowns.

""" + context
    )
    return prompt

# Endpoint 2: SWOT analysis
@app.post("/swot", response_model=SWOTResponse)
async def swot_analysis(submission: Submission):
    prompt = build_swot_prompt(submission.items)
    try:
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        content = resp.text
        if content.strip().startswith("```"):
            lines = content.strip().splitlines()
            content = "\n".join(lines[1:-1])
        import json
        data = json.loads(content)
        return SWOTResponse(
        strengths=data.get("strengths", ""),
        weaknesses=data.get("weaknesses", ""),
        opportunities=data.get("opportunities", ""),
        threats=data.get("threats", "")
    )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/generate-qa", response_model=QuestionGenerationResponse)
async def generate_questions(request: QuestionGenerationRequest):
    prompt = build_question_generation_prompt(request)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        content = response.text.strip()

        if content.startswith("```"):
            content = "\n".join(content.splitlines()[1:-1])

        questions_json = json.loads(content)

        return QuestionGenerationResponse(
            test_title=request.title,
            subject=request.subject,
            class_=request.class_,
            questions=[
                GeneratedQuestion(question=q["question"], expected_answer=q["expected_answer"])
                for q in questions_json
            ]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini Error: {str(e)}")
    
@app.get("/health-check")
async def health_check():
    return {"status": "ok"}


