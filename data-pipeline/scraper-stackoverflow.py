import requests
import time
import json
import argparse

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape Stack Overflow Q&A pairs for a specific tag')
    parser.add_argument('--keyword', type=str, required=True, help='The tag/keyword to search for (e.g., gradio, python, etc.)')
    args = parser.parse_args()

    API_URL = "https://api.stackexchange.com/2.3/questions"
    params = {
        "order": "desc",
        "sort": "activity",
        "tagged": args.keyword,
        "site": "stackoverflow",
        "filter": "withbody",
        "pagesize": 100,
        "page": 1
    }

    questions_with_answers = []
    while True:
        response = requests.get(API_URL, params=params).json()
        items = response.get("items", [])
        
        for q in items:
            if q.get("answer_count", 0) > 0:
                questions_with_answers.append(q)
        
        if not response.get("has_more"):
            break
        params["page"] += 1
        time.sleep(1)

    print(f"Total Questions with Answers Fetched: {len(questions_with_answers)}")

    API_URL_ANS = "https://api.stackexchange.com/2.3/questions/{}/answers"
    qa_pairs = []
    for q in questions_with_answers:
        q_id = q["question_id"]
        ans_resp = requests.get(API_URL_ANS.format(q_id), params={
            "order": "desc",
            "sort": "votes",
            "site": "stackoverflow",
            "filter": "withbody"
        }).json()
        
        answers = ans_resp.get("items", [])
        if answers:
            qa_pairs.append({
                "question": q["title"],
                "answer": answers[0]["body"],
                "link": q["link"]
            })
        time.sleep(0.5)

    print(f"Total Final Q&A Pairs Collected: {len(qa_pairs)}")

    # Save to JSON file with keyword in filename
    output_file = f"{args.keyword}_qa_pairs.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)

    print(f"Saved to {output_file} ✅")

if __name__ == "__main__":
    main()
