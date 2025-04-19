import requests
import json
import os

GITHUB_REPO = "ApolloAuto/apollo"
TOKEN = json.load(open("config.json"))["github_token"]
HEADERS = {"Authorization": f"token {TOKEN}"}
BASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
OUTPUT_FILE = "apollo_qa_pairs_with_question.json"

def get_issues_by_page(page_num):
    response = requests.get(BASE_URL, headers=HEADERS, params={
        "state": "closed",
        "per_page": 30,
        "page": page_num
    })
    if response.status_code == 422:
        print(f"🔚 Reached last page: {page_num}")
        return []
    response.raise_for_status()
    return response.json()

def get_comments(issue_url):
    comments_url = issue_url + "/comments"
    response = requests.get(comments_url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def extract_qa_pairs(issues):
    qa_pairs = []
    for issue in issues:
        if "pull_request" in issue:
            continue  # skip PRs

        title = issue["title"].strip()
        body = issue.get("body")
        body = body.strip() if body else ""
        q = f"{title}\n\n{body}" if body else title

        html_url = issue["html_url"]
        comments = get_comments(issue["url"])

        if comments:
            a = comments[0].get("body", "")
            a = a.strip() if a else ""
        else:
            a = body  # fallback (already stripped above)

        if not a:
            continue  # skip if no answer

        qa_pairs.append({
            "question": q,
            "answer": a,
            "link": html_url
        })

    return qa_pairs


# extract only title
# def extract_qa_pairs(issues):
#     qa_pairs = []
#     for issue in issues:
#         if "pull_request" in issue:
#             continue  # skip PRs

#         q = issue["title"].strip()
#         html_url = issue["html_url"]
#         comments = get_comments(issue["url"])

#         if comments:
#             a = comments[0].get("body", "")
#             a = a.strip() if a else ""
#         else:
#             body = issue.get("body")
#             a = body.strip() if body else ""

#         if not a:
#             continue  # skip if no meaningful answer

#         qa_pairs.append({
#             "question": q,
#             "answer": a,
#             "link": html_url
#         })

#     return qa_pairs

def append_to_json_file(filename, new_data):
    existing = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                pass  # ignore if file is empty

    existing.extend(new_data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    start_page = 1

    while True:
        print(f"📄 Fetching page {start_page}...")
        issues = get_issues_by_page(start_page)

        if not issues:
            break

        qa_pairs = extract_qa_pairs(issues)

        if qa_pairs:
            print(f"✅ {len(qa_pairs)} Q&A pairs from page {start_page}")
            append_to_json_file(OUTPUT_FILE, qa_pairs)
        else:
            print(f"⚠️ No valid Q&A pairs on page {start_page}")

        start_page += 1
