import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3252: LEGAL DISCOVERY BCP
# -----------------------------------------------------------------------------
# Domain: Legal
# Goal: Find relevant documents in a corpus (Discovery).
# Hypothesis: BCP (Active Learning / Relevance Feedback) finds documents faster
#             than Static Keyword Search.
# -----------------------------------------------------------------------------

class Document:
    def __init__(self, id, is_relevant):
        self.id = id
        self.is_relevant = is_relevant
        # Feature vector (topics)
        if is_relevant:
            self.vector = [random.gauss(1.0, 0.5) for _ in range(5)]
        else:
            self.vector = [random.gauss(0.0, 0.5) for _ in range(5)]
            
    def match(self, query):
        # Dot product
        score = sum(q*v for q,v in zip(query, self.vector))
        return score

class Searcher:
    def search(self, docs):
        raise NotImplementedError

class StaticSearcher(Searcher):
    def search(self, docs):
        # Static query
        query = [1.0, 1.0, 1.0, 1.0, 1.0]
        scores = [(d.match(query), d) for d in docs]
        scores.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scores]

class BCPSearcher(Searcher):
    def search(self, docs):
        # Active Learning
        # Start with broad query
        query = [0.5, 0.5, 0.5, 0.5, 0.5]
        
        # 1. Initial Rank
        scores = [(d.match(query), d) for d in docs]
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # 2. Feedback Loop (Simulated Review)
        # Review top 10
        reviewed = scores[:10]
        relevant_found = [s[1] for s in reviewed if s[1].is_relevant]
        
        # Update Query (Rocchio Algorithm style)
        if relevant_found:
            # Move query towards relevant centroid
            for i in range(5):
                centroid = sum(d.vector[i] for d in relevant_found) / len(relevant_found)
                query[i] = 0.5 * query[i] + 0.5 * centroid
                
        # 3. Re-Rank
        scores = [(d.match(query), d) for d in docs]
        scores.sort(key=lambda x: x[0], reverse=True)
        
        return [s[1] for s in scores]

def run_simulation(searcher_cls, steps=100):
    total_precision_at_100 = 0
    
    for _ in range(steps):
        # 1000 docs, 50 relevant (5%)
        docs = [Document(i, i < 50) for i in range(1000)]
        random.shuffle(docs)
        
        searcher = searcher_cls()
        results = searcher.search(docs)
        
        # Precision @ 100
        top_100 = results[:100]
        relevant = sum(1 for d in top_100 if d.is_relevant)
        total_precision_at_100 += relevant
        
    return total_precision_at_100 / steps

def main():
    print("======================================================================")
    print("CYCLE 3252: LEGAL DISCOVERY BCP")
    print("======================================================================")
    
    steps = 200
    
    static_p = run_simulation(StaticSearcher, steps)
    print(f"Static Precision@100: {static_p:.2f}")
    
    bcp_p = run_simulation(BCPSearcher, steps)
    print(f"BCP Precision@100:    {bcp_p:.2f}")
    
    improvement = ((bcp_p - static_p) / static_p) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_p > static_p:
        print("RESULT: SUCCESS. Relevance feedback honed in on the signal.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3252_legal_discovery.json", "w") as f:
        json.dump({"static": static_p, "bcp": bcp_p, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
