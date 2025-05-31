import requests

# Replace with your actual Render URL
BASE_URL = "https://evaluation-api-nrx0.onrender.com"

# --- Evaluate endpoint ---
evaluate_url = f"{BASE_URL}/evaluate"

evaluate_payload = {
    "items": [
        {
            "question_id": "q1",
            "question": "What is the capital of France?",
            "actual_answer": "Paris",
            "expected_answer": "Paris"
        },
        {
            "question_id": "q2",
            "question": "What is 2 + 2?",
            "actual_answer": "5",
            "expected_answer": "4"
        }
    ]
}

# Send POST request to /evaluate
eval_response = requests.post(evaluate_url, json=evaluate_payload)

print("=== /evaluate ===")
print("Status Code:", eval_response.status_code)
print("Response JSON:")
print(eval_response.json())