import arxiv, json, sys, time

queries = [
    "Bayesian model selection Bayes factor null hypothesis machine learning",
    "interpreting null results non-significant findings statistical equivalence testing",
    "neurosymbolic reasoning hybrid symbolic Bayesian inference",
    "AI alignment evaluation robustness safety experiments",
    "statistical power analysis deep learning experiments reproducibility",
    "equivalence testing TOST Bayesian evidence absence of effect",
    "probabilistic program induction symbolic regression Bayesian",
    "diagnosing experimental design flaws causal inference interventions",
    "red teaming language model robustness adversarial evaluation alignment",
    "Bayesian workflow model criticism posterior predictive checks",
]

client = arxiv.Client(page_size=20, delay_seconds=3, num_retries=3)
seen = {}
for q in queries:
    try:
        search = arxiv.Search(query=q, max_results=12, sort_by=arxiv.SortCriterion.Relevance)
        for r in client.results(search):
            aid = r.get_short_id().split('v')[0]
            if aid in seen:
                seen[aid]['queries'].append(q)
                continue
            seen[aid] = {
                'id': aid,
                'title': r.title.replace('\n',' ').strip(),
                'authors': [a.name for a in r.authors][:6],
                'year': r.published.year,
                'pdf': r.pdf_url,
                'summary': r.summary.replace('\n',' ').strip(),
                'cats': r.categories,
                'queries': [q],
            }
    except Exception as e:
        print(f"ERR query '{q}': {e}", file=sys.stderr)
    time.sleep(1)

with open('/tmp/arxiv_results.json','w') as f:
    json.dump(list(seen.values()), f, indent=2)
print(f"TOTAL unique: {len(seen)}")
for v in seen.values():
    print(f"\n[{v['id']}] ({v['year']}) {v['title']}")
    print(f"  cats={v['cats'][:3]} nq={len(v['queries'])}")
    print(f"  {v['summary'][:300]}")
