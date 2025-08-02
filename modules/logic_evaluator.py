def categorize_question(question: str) -> str:
    if "experience" in question.lower():
        return "experience"
    elif "skill" in question.lower():
        return "skills"
    elif "qualification" in question.lower() or "education" in question.lower():
        return "education"
    else:
        return "general"
