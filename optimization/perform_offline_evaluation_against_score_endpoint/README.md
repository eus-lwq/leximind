# Offline Evaluation Against Score Endpoint

This folder contains scripts and utilities to perform offline evaluation of language models against a scoring endpoint. The goal is to test the performance, accuracy, and similarity of responses generated by the models under different scenarios.

## Files and Their Descriptions

### [`test_score.py`](./test_score.py)
- **Description**: This script evaluates the accuracy of a fine-tuned language model hosted with vLLM by comparing its responses to a predefined dataset of questions and expected answers.
- **Test Scenarios**:
  1. **Accuracy Testing**:
     - Compares the model's responses to the expected answers.
     - Calculates metrics such as accuracy and pass/fail rate.
  2. **Threshold Validation**:
     - Ensures the model achieves a minimum accuracy threshold (default: 80%).
  3. **Server Management**:
     - Starts the vLLM server before the tests and shuts it down afterward.
- **Key Metrics**:
  - Accuracy
  - Pass/Fail rate

---

### [`test_language_model_comparison.py`](./test_language_model_comparison.py)
- **Description**: This script compares the responses of the vLLM language model to a commercial-grade model and evaluates their similarity using a judge model.
- **Test Scenarios**:
  1. **Response Comparison**:
     - Gathers responses from the vLLM model and a commercial-grade model for a fixed set of questions.
  2. **Similarity Scoring**:
     - Uses a similarity judge model to compare the responses and assigns a similarity score between 0 and 1.
  3. **Threshold Validation**:
     - Ensures the similarity score meets a predefined threshold (default: 0.7).
- **Key Metrics**:
  - Similarity score
  - Pass/Fail rate for similarity threshold

---

## Test Scenarios in Detail

### `test_score.py`
1. **Dataset-Based Accuracy Testing**:
   - The script uses a fixed dataset of questions and expected answers.
   - For each question, the model's response is scored against the expected answer using the `/score` endpoint.
   - A score of 0.5 or higher is considered a pass for each question.

2. **Performance Metrics**:
   - The script calculates the overall accuracy of the model based on the number of passing tests.
   - If the accuracy falls below the threshold (default: 80%), the test fails.

3. **Server Management**:
   - The script starts the vLLM server before running the tests and ensures it is properly shut down afterward.
   - Includes retries to ensure the server is ready before starting the tests.

---

### `test_language_model_comparison.py`
1. **Response Collection**:
   - The script sends a fixed set of questions to both the vLLM model and a commercial-grade model.
   - Collects the responses from both models for comparison.

2. **Similarity Scoring**:
   - Uses a similarity judge model to compare the responses from the two models.
   - The judge model assigns a similarity score between 0 and 1 based on the conceptual similarity of the responses.

3. **Threshold Validation**:
   - A similarity threshold (default: 0.7) is used to determine whether the responses are sufficiently similar.
   - If the similarity score for any question falls below the threshold, the test fails.

4. **Pass/Fail Reporting**:
   - The script reports the similarity score for each question and whether it passes or fails the threshold.

---

## Key Metrics Evaluated
1. **Accuracy**:
   - Measures how closely the model's responses match the expected answers.
2. **Similarity**:
   - Evaluates the conceptual similarity between responses from different models.
3. **Threshold Validation**:
   - Ensures the model meets predefined thresholds for accuracy and similarity.

---

## How to Use

1. **Prepare the Environment**:
   - Ensure the required dependencies are installed (e.g., `pytest`, `requests`).
   - Place the model in the appropriate directory (e.g., `/home/cc/model/whole_model`).

2. **Run the Tests**:
   - Use `pytest` to execute the tests:
     ```bash
     pytest test_score.py
     pytest test_language_model_comparison.py
     ```

3. **Analyze the Results**:
   - Review the output for accuracy, similarity scores, and pass/fail rates.
   - Use the metrics to evaluate the model's performance and suitability for deployment.
