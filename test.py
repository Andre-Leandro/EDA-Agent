from main import ask_agent

tests = [
    ("Which columns have missing values?", ["age", "embarked", "deck", "embark_town"]),
    ("Show me the first 3 columns with their data types.", ["survived", "pclass", "sex"]),
    ("Give me a statistical summary of the 'age' column.", ["mean", "min", "max"]),
]

def passed(q, out, must_include):
    text = out.lower()
    return all(any(tok in text for tok in (m.lower(), str(m).lower())) for m in must_include)

if __name__ == "__main__":
    ok = 0
    for q, must in tests:
        out = ask_agent(q)
        result = passed(q, out, must)
        print(f"[{'OK' if result else 'FAIL'}] {q}\n{out}\n")
        ok += int(result)
    print(f"Passed {ok}/{len(tests)}")