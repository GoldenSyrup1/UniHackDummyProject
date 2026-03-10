import requests

def generate_brief(hex_id, gap_score, demographics):
    prompt = f"""You are an urban policy analyst. Write a 100-word council brief.

Zone gap score: {gap_score:.2f}/1.0
Elderly (65+): {demographics['elderly_pct']}%
No car: {demographics['no_car_pct']}%
Median income: ${demographics['median_income']}/week

Write: problem summary, key stat, recommended intervention."""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"]