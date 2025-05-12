import pytest
import requests
import subprocess
import time
import os
import sys

# Configuration
VLLM_SERVER_URL = "http://localhost:8000"
TEST_DATASET = [
    {"question": "What is the capital of France?", "expected_answer": "Paris"},
    {"question": "Who wrote 'Pride and Prejudice'?", "expected_answer": "Jane Austen"},
    {"question": "What is the square root of 64?", "expected_answer": "8"},
    {"question": "What is the chemical symbol for water?", "expected_answer": "H2O"},
    {"question": "Who painted the Mona Lisa?", "expected_answer": "Leonardo da Vinci"},
]
PASS_THRESHOLD = 0.8  # Minimum accuracy required to pass the test


@pytest.fixture(scope="session")
def start_vllm_server():
    """
    Fixture to start the vLLM server before running the tests and shut it down afterward.
    """
    # Command to start the vLLM server
    model_name = os.getenv("MODEL_NAME", "/home/cc/model/whole_model")
    command = [
        "python",
        "-m",
        "vllm.entrypoints.openai.api_server",
        "--model",
        model_name,
        "--dtype",
        "float16",
    ]

    print("Starting vLLM server...")
    sys.stdout.flush()  # Ensure the output is flushed to the console
    process = subprocess.Popen(command, stdout=None, stderr=None)  # Allow output to flow to the console

    # Wait for the server to start and check health
    max_retries = 6
    retry_interval = 10  # seconds
    for attempt in range(max_retries):
        print(f"Waiting for vLLM server to be ready (attempt {attempt + 1}/{max_retries})...")
        sys.stdout.flush()  # Ensure the output is flushed to the console
        time.sleep(retry_interval)
        try:
            response = requests.get(f"{VLLM_SERVER_URL}/health", timeout=5)
            if response.status_code == 200:
                print("vLLM server is ready.")
                sys.stdout.flush()  # Ensure the output is flushed to the console
                break
        except requests.RequestException:
            print("vLLM server is not ready yet.")
            sys.stdout.flush()  # Ensure the output is flushed to the console
    else:
        process.terminate()
        raise RuntimeError("vLLM server failed to start after multiple attempts.")

    yield  # Run the tests

    # Shut down the server after tests
    print("Shutting down vLLM server...")
    sys.stdout.flush()  # Ensure the output is flushed to the console
    process.terminate()
    process.wait()


def send_request_to_vllm(question, expected_answer):
    """
    Sends a request to the vLLM server's /score endpoint and retrieves the score.

    Args:
        question (str): The input question for the language model.
        expected_answer (str): The expected answer to compare against.

    Returns:
        float: The score returned by the model.
    """
    try:
        response = requests.post(
            f"{VLLM_SERVER_URL}/score",
            json={"question": question, "expected_answer": expected_answer},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("score", 0.0)
        else:
            print(f"Error: Received status code {response.status_code}")
            sys.stdout.flush()  # Ensure the output is flushed to the console
            return 0.0
    except requests.RequestException as e:
        print(f"Error: Failed to connect to vLLM server. {e}")
        sys.stdout.flush()  # Ensure the output is flushed to the console
        return 0.0


def test_model_accuracy(start_vllm_server):
    """
    Test the accuracy of the fine-tuned language model hosted with vLLM using the /score endpoint.
    """
    total_tests = len(TEST_DATASET)
    passing_tests = 0

    for i, test_case in enumerate(TEST_DATASET):
        question = test_case["question"]
        expected_answer = test_case["expected_answer"]

        print(f"Test {i + 1}/{total_tests}: {question}")
        sys.stdout.flush()  # Ensure the output is flushed to the console
        score = send_request_to_vllm(question, expected_answer)

        print(f"  Model Score: {score}")
        print(f"  Expected Answer: {expected_answer}")
        sys.stdout.flush()  # Ensure the output is flushed to the console

        # Check if the score meets the threshold for passing
        if score >= 0.5:  # Assuming a score of 0.5 or higher is considered a pass
            print("  Result: PASS")
            passing_tests += 1
        else:
            print("  Result: FAIL")
        sys.stdout.flush()  # Ensure the output is flushed to the console

    # Calculate accuracy
    accuracy = passing_tests / total_tests
    print(f"\nFinal Results:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passing Tests: {passing_tests}")
    print(f"  Accuracy: {accuracy:.2%}")
    sys.stdout.flush()  # Ensure the output is flushed to the console

    # Determine pass/fail
    assert accuracy >= PASS_THRESHOLD, f"Test failed with accuracy {accuracy:.2%} (threshold: {PASS_THRESHOLD:.2%})"