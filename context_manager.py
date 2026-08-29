import os
import re

def score_file(path, task):
    """Score a file's relevance to the task — higher = more relevant"""
    try:
        with open(path, 'r') as f:
            content = f.read()
    except:
        return 0

    score = 0

    # keyword overlap between task and file content
    task_words = set(task.lower().split())
    file_words = set(content.lower().split())
    overlap = task_words & file_words
    score += len(overlap) * 10

    # shorter files are cheaper — prefer them
    lines = content.count('\n')
    if lines < 50:
        score += 20
    elif lines < 100:
        score += 10

    # penalize files that are too large to fit in context
    if len(content) > 4000:
        score -= 30

    return score


def get_relevant_files(directory, task, max_tokens=3000):
    """Return the most relevant files that fit within token budget"""
    candidates = []

    for root, dirs, files in os.walk(directory):
        # skip hidden folders like .git
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.py') or file.endswith('.txt') or file.endswith('.md'):
                path = os.path.join(root, file)
                s = score_file(path, task)
                candidates.append((s, path))

    # sort by score descending
    candidates.sort(reverse=True)

    selected = []
    total_chars = 0
    char_budget = max_tokens * 4  # rough: 1 token ≈ 4 chars

    for score, path in candidates:
        with open(path, 'r') as f:
            content = f.read()
        if total_chars + len(content) < char_budget:
            selected.append((path, content))
            total_chars += len(content)

    return selected
