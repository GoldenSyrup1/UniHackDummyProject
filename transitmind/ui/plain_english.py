def gap_to_label(gap_score):
    if gap_score < 0.3:
        return "🟢", "Well served", "Your area has good access to public transit."
    elif gap_score < 0.6:
        return "🟡", "Moderate gaps", "Your area has some transit coverage but key gaps exist."
    else:
        return "🔴", "Critically underserved", "Your area is significantly lacking in public transit access."

def format_commuter_card(result):
    emoji, label, description = gap_to_label(result["gap_score"])
    return emoji, label, description, round(result["gap_score"] * 100)

def get_top_gaps(df, n=10):
    return df.nlargest(n, "gap_score")[["hex", "gap_score", "deprivation", "accessibility"]].reset_index(drop=True)