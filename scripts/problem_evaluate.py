#!/usr/bin/env python3
"""
AI-powered solution evaluator
"""
import json
import sys
import re

def evaluate_solution(question: str, reference_solution: str, user_solution: str, difficulty: float):
    """Evaluate the quality of a user's solution"""
    
    # Basic validation
    if not user_solution or len(user_solution.strip()) < 10:
        return {
            "isValid": False,
            "qualityScore": 0.0,
            "feedback": "Solution is too short or empty.",
            "strengths": [],
            "weaknesses": ["Insufficient detail"],
        }
    
    # Length analysis
    solution_length = len(user_solution)
    word_count = len(user_solution.split())
    
    # Initialize scores
    scores = {
        "length": 0.0,
        "structure": 0.0,
        "technical": 0.0,
        "clarity": 0.0,
    }
    
    # Length score (50-500 words optimal)
    if word_count < 20:
        scores["length"] = 0.3
    elif word_count < 50:
        scores["length"] = 0.6
    elif word_count <= 500:
        scores["length"] = 1.0
    else:
        scores["length"] = 0.8
    
    # Structure score (paragraphs, formatting)
    paragraphs = user_solution.split('\n\n')
    if len(paragraphs) > 1:
        scores["structure"] += 0.3
    if any(char in user_solution for char in ['1.', '2.', '3.', '-', '*']):
        scores["structure"] += 0.3
    if re.search(r'\b(therefore|thus|hence|consequently)\b', user_solution, re.IGNORECASE):
        scores["structure"] += 0.2
    if re.search(r'\b(first|second|finally|in conclusion)\b', user_solution, re.IGNORECASE):
        scores["structure"] += 0.2
    scores["structure"] = min(1.0, scores["structure"])
    
    # Technical score (formulas, terminology)
    technical_indicators = [
        r'[=+\-*/^]',  # Math operators
        r'\b(equation|formula|theorem|principle|law)\b',
        r'\b(calculate|derive|prove|demonstrate)\b',
        r'\d+\.?\d*',  # Numbers
        r'[α-ωΑ-Ω]',  # Greek letters
    ]
    technical_count = sum(1 for pattern in technical_indicators if re.search(pattern, user_solution, re.IGNORECASE))
    scores["technical"] = min(1.0, technical_count / len(technical_indicators))
    
    # Clarity score (readability)
    sentences = re.split(r'[.!?]+', user_solution)
    avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
    
    if 10 <= avg_sentence_length <= 25:
        scores["clarity"] = 1.0
    elif 5 <= avg_sentence_length < 10 or 25 < avg_sentence_length <= 35:
        scores["clarity"] = 0.7
    else:
        scores["clarity"] = 0.5
    
    # Adjust for difficulty
    difficulty_factor = 0.7 + (difficulty * 0.3)
    
    # Calculate overall quality
    quality_score = (
        scores["length"] * 0.2 +
        scores["structure"] * 0.3 +
        scores["technical"] * 0.3 +
        scores["clarity"] * 0.2
    ) * difficulty_factor
    
    # Add randomness for variation (±5%)
    import random
    quality_score = max(0.0, min(1.0, quality_score + random.uniform(-0.05, 0.05)))
    
    # Determine validity
    is_valid = quality_score >= 0.4
    
    # Generate feedback
    strengths = []
    weaknesses = []
    
    if scores["length"] > 0.7:
        strengths.append("Appropriate length and detail")
    elif scores["length"] < 0.5:
        weaknesses.append("Could provide more detail")
    
    if scores["structure"] > 0.7:
        strengths.append("Well-structured and organized")
    elif scores["structure"] < 0.5:
        weaknesses.append("Could improve organization")
    
    if scores["technical"] > 0.7:
        strengths.append("Strong technical content")
    elif scores["technical"] < 0.5:
        weaknesses.append("Could include more technical details")
    
    if scores["clarity"] > 0.7:
        strengths.append("Clear and readable")
    elif scores["clarity"] < 0.5:
        weaknesses.append("Could improve clarity")
    
    # Overall feedback
    if quality_score >= 0.9:
        feedback = "Excellent solution! Demonstrates deep understanding."
    elif quality_score >= 0.7:
        feedback = "Good solution with solid reasoning."
    elif quality_score >= 0.5:
        feedback = "Acceptable solution, but could be improved."
    else:
        feedback = "Solution needs significant improvement."
    
    result = {
        "isValid": is_valid,
        "qualityScore": round(quality_score, 3),
        "feedback": feedback,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "scores": {k: round(v, 2) for k, v in scores.items()},
        "metadata": {
            "wordCount": word_count,
            "sentenceCount": len([s for s in sentences if s.strip()]),
            "avgSentenceLength": round(avg_sentence_length, 1),
        }
    }
    
    return result

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No arguments provided"}))
        return 1
    
    try:
        args = json.loads(sys.argv[1])
        params = args[0] if isinstance(args, list) else args
        
        question = params.get("question", "")
        reference_solution = params.get("referenceSolution", "")
        user_solution = params.get("userSolution", "")
        difficulty = params.get("difficulty", 0.5)
        
        result = evaluate_solution(question, reference_solution, user_solution, difficulty)
        print(json.dumps(result))
        return 0
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return 1

if __name__ == "__main__":
    sys.exit(main())
