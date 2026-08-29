import os
import re
import math
from collections import Counter

def tokenize(text):
    """Lowercase and split into words — strip punctuation"""
    return re.findall(r'[a-z0-9]+', text.lower())

def build_corpus(directory):
    """Load all files and return list of (path, tokens) pairs"""
    corpus = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.py') or file.endswith('.txt') or file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    content = open(path).read()
                    corpus.append((path, content, tokenize(content)))
                except:
                    pass
    return corpus

def bm25_scores(query, corpus, k1=1.5, b=0.75):
    """
    BM25 ranking — scores each file by relevance to query.
    k1: term frequency saturation (higher = more weight to repeated terms)
    b:  length normalisation (1.0 = full normalisation, 0 = none)
    """
    query_tokens = tokenize(query)
    N = len(corpus)                                          # total number of files
    avgdl = sum(len(doc[2]) for doc in corpus) / N          # avg file length in tokens

    # document frequency: how many files contain each word
    df = Counter()
    for _, _, tokens in corpus:
        for word in set(tokens):
            df[word] += 1

    scores = []
    for path, content, tokens in corpus:
        tf = Counter(tokens)                                 # term frequency in this file
        dl = len(tokens)                                     # this file's length
        score = 0.0

        for word in query_tokens:
            if df[word] == 0:
                continue
            # IDF: rare words across files score higher
            idf = math.log((N - df[word] + 0.5) / (df[word] + 0.5) + 1)
            # TF with saturation and length normalisation
            tf_norm = (tf[word] * (k1 + 1)) / (tf[word] + k1 * (1 - b + b * dl / avgdl))
            score += idf * tf_norm

        scores.append((score, path, content))

    scores.sort(reverse=True)
    return scores


def get_relevant_files(directory, task, max_tokens=3000):
    """Return the most relevant files that fit within token budget, ranked by BM25"""
    corpus = build_corpus(directory)
    if not corpus:
        return []

    ranked = bm25_scores(task, corpus)

    selected = []
    total_chars = 0
    char_budget = max_tokens * 4  # rough: 1 token ≈ 4 chars

    for score, path, content in ranked:
        if score <= 0:                              # skip files with zero relevance
            continue
        if total_chars + len(content) < char_budget:
            selected.append((path, content))
            total_chars += len(content)

    return selected
