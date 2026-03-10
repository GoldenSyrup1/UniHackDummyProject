# llm/brief_gen.py
import anthropic

client = anthropic.Anthropic()

def generate_brief(hex_id, gap_score, demographics):
    prompt = f"""
You are an urban policy analyst. Generate a 150-word council brief for this transit gap zone.

Zone ID: {hex_id}
Gap severity score: {gap_score}/1.0
Demographics:
- Elderly population (65+): {demographics['elderly_pct']}%
- Households without a car: {demographics['no_car_pct']}%
- Median weekly income: ${demographics['median_income']}

Format:
- 2 sentence summary of the problem
- 1 key statistic
- 1 recommended intervention
- Estimated residents impacted
"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text