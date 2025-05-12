import pytest
import requests
import time

def send_request_to_model(prompt, max_tokens, server_url):
    """
    Send a request to a language model server.

    Args:
        prompt (str): The input prompt for the server.
        max_tokens (int): Maximum number of tokens to generate.
        server_url (str): URL of the language model server.

    Returns:
        str: The response text from the model.
    """
    try:
        response = requests.post(
            server_url,
            json={"prompt": prompt, "max_tokens": max_tokens},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            return None
    except requests.RequestException:
        return None

def test_language_model_comparison():
    """
    Test the vLLM language model by comparing its responses to a commercial-grade model
    and evaluating the similarity using a judge model.
    """
    # Configuration
    vllm_server_url = "http://localhost:8000/generate"
    judge_model_server_url = "https://api.commercial-model.com/generate"
    similarity_model_server_url = "https://api.similarity-judge.com/evaluate"
    max_tokens = 128

    # Fixed question dataset
    questions = [
        "What is the capital of France?",
        "Explain the theory of relativity.",
        "What are the benefits of renewable energy?",
        "How does machine learning work?",
        "What is the importance of biodiversity?"
    ]

    # Gather responses from vLLM
    vllm_responses = []
    for question in questions:
        response = send_request_to_model(question, max_tokens, vllm_server_url)
        assert response is not None, f"vLLM failed to respond for question: {question}"
        vllm_responses.append(response)

    # Gather responses from the judge model
    judge_responses = []
    for question in questions:
        response = send_request_to_model(question, max_tokens, judge_model_server_url)
        assert response is not None, f"Judge model failed to respond for question: {question}"
        judge_responses.append(response)

    # Compare responses using the similarity judge model
    results = []
    for vllm_response, judge_response in zip(vllm_responses, judge_responses):
        similarity_prompt = (
            f"Compare the following two answers for their similarity in main concept:\n"
            f"Answer 1: {vllm_response}\n"
            f"Answer 2: {judge_response}\n"
            f"Provide a similarity score between 0 and 1."
        )
        similarity_score = send_request_to_model(similarity_prompt, max_tokens, similarity_model_server_url)
        assert similarity_score is not None, "Similarity judge model failed to respond."
        try:
            similarity_score = float(similarity_score.strip())
        except ValueError:
            pytest.fail(f"Invalid similarity score received: {similarity_score}")
        results.append(similarity_score)

    # Evaluate pass/fail based on similarity threshold
    similarity_threshold = 0.7  # Define a threshold for passing
    for i, score in enumerate(results):
        if score >= similarity_threshold:
            print(f"Question {i + 1}: PASS (Similarity Score: {score:.2f})")
        else:
            print(f"Question {i + 1}: FAIL (Similarity Score: {score:.2f})")

    # Assert that all questions pass the similarity threshold
    assert all(score >= similarity_threshold for score in results), "Some questions failed the similarity test."