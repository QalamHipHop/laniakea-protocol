#!/usr/bin/env python3
"""
AI-powered scientific problem generator
"""
import json
import sys
import random

# Problem templates by category
PROBLEM_TEMPLATES = {
    "physics": [
        {
            "template": "Calculate the {quantity} of a {object} with {property} = {value}.",
            "quantities": ["momentum", "kinetic energy", "potential energy", "force", "acceleration"],
            "objects": ["particle", "projectile", "satellite", "pendulum", "spring"],
            "properties": ["mass", "velocity", "height", "displacement", "frequency"],
        },
        {
            "template": "A {system} has {initial_state}. After {time}, what is the {final_quantity}?",
            "systems": ["harmonic oscillator", "rotating disk", "falling object", "electromagnetic field"],
            "initial_states": ["zero velocity", "maximum amplitude", "rest position"],
            "final_quantities": ["position", "velocity", "energy", "angular momentum"],
        },
    ],
    "mathematics": [
        {
            "template": "Solve the {equation_type} equation: {equation}",
            "equation_types": ["differential", "integral", "algebraic", "transcendental"],
        },
        {
            "template": "Find the {operation} of the function f(x) = {function}",
            "operations": ["derivative", "integral", "limit", "maximum", "minimum"],
            "functions": ["x^2 + 3x + 2", "sin(x) * e^x", "ln(x^2 + 1)", "sqrt(x^3 - x)"],
        },
    ],
    "biology": [
        {
            "template": "Explain the process of {process} in {organism} and its {aspect}.",
            "processes": ["cellular respiration", "photosynthesis", "DNA replication", "protein synthesis"],
            "organisms": ["prokaryotes", "eukaryotes", "plants", "animals"],
            "aspects": ["energy efficiency", "evolutionary advantage", "molecular mechanism"],
        },
    ],
    "chemistry": [
        {
            "template": "Calculate the {quantity} for the reaction: {reaction}",
            "quantities": ["equilibrium constant", "reaction rate", "enthalpy change", "entropy change"],
        },
        {
            "template": "Determine the {property} of {compound} given {conditions}.",
            "properties": ["molecular structure", "oxidation state", "pH", "solubility"],
            "compounds": ["organic compound", "ionic compound", "coordination complex"],
            "conditions": ["standard conditions", "elevated temperature", "acidic medium"],
        },
    ],
    "computer_science": [
        {
            "template": "Design an algorithm to {task} with time complexity {complexity}.",
            "tasks": ["sort an array", "search a graph", "find shortest path", "compress data"],
            "complexities": ["O(n log n)", "O(n)", "O(log n)", "O(n^2)"],
        },
        {
            "template": "Implement a {structure} that supports {operations} efficiently.",
            "structures": ["binary search tree", "hash table", "priority queue", "trie"],
            "operations": ["insertion and deletion", "range queries", "nearest neighbor search"],
        },
    ],
    "philosophy": [
        {
            "template": "Analyze {philosopher}'s argument about {topic} and discuss its {aspect}.",
            "philosophers": ["Kant", "Aristotle", "Descartes", "Nietzsche", "Plato"],
            "topics": ["consciousness", "free will", "ethics", "epistemology", "metaphysics"],
            "aspects": ["logical validity", "practical implications", "historical context"],
        },
    ],
    "engineering": [
        {
            "template": "Design a {system} that can {function} under {constraints}.",
            "systems": ["bridge", "circuit", "control system", "mechanical linkage"],
            "functions": ["withstand load", "regulate temperature", "minimize vibration"],
            "constraints": ["limited budget", "space restrictions", "environmental conditions"],
        },
    ],
    "cosmology": [
        {
            "template": "Calculate the {quantity} of a {object} at redshift z = {redshift}.",
            "quantities": ["luminosity distance", "age", "angular diameter", "comoving volume"],
            "objects": ["galaxy", "quasar", "galaxy cluster", "cosmic structure"],
        },
        {
            "template": "Explain how {phenomenon} affects {observation} in {context}.",
            "phenomena": ["dark energy", "cosmic inflation", "gravitational lensing", "CMB anisotropies"],
            "observations": ["galaxy distribution", "expansion rate", "structure formation"],
            "contexts": ["early universe", "late-time universe", "large-scale structure"],
        },
    ],
}

def generate_problem(difficulty: float, category: str, knowledge_domains: list, user_level: int):
    """Generate a scientific problem based on parameters"""
    
    # Select template
    if category not in PROBLEM_TEMPLATES:
        category = random.choice(list(PROBLEM_TEMPLATES.keys()))
    
    templates = PROBLEM_TEMPLATES[category]
    template_data = random.choice(templates)
    
    # Generate question
    question = template_data["template"]
    for key, values in template_data.items():
        if key != "template" and isinstance(values, list):
            placeholder = "{" + key + "}"
            if placeholder in question:
                question = question.replace(placeholder, random.choice(values))
    
    # Add numerical values based on difficulty
    if "{value}" in question:
        if difficulty < 0.3:
            value = random.randint(1, 10)
        elif difficulty < 0.6:
            value = random.randint(10, 100)
        else:
            value = random.randint(100, 1000)
        question = question.replace("{value}", str(value))
    
    if "{time}" in question:
        time = round(random.uniform(1, 10) * difficulty, 2)
        question = question.replace("{time}", f"{time}s")
    
    if "{redshift}" in question:
        redshift = round(random.uniform(0.1, 5.0) * difficulty, 2)
        question = question.replace("{redshift}", str(redshift))
    
    if "{equation}" in question:
        if difficulty < 0.3:
            equation = "y' + y = 0"
        elif difficulty < 0.6:
            equation = "y'' + 2y' + y = e^x"
        else:
            equation = "y''' - 3y'' + 3y' - y = sin(x)"
        question = question.replace("{equation}", equation)
    
    if "{reaction}" in question:
        reactions = [
            "2H2 + O2 → 2H2O",
            "N2 + 3H2 ⇌ 2NH3",
            "CH4 + 2O2 → CO2 + 2H2O",
        ]
        question = question.replace("{reaction}", random.choice(reactions))
    
    # Generate reference solution (simplified)
    reference_solution = f"This problem requires understanding of {', '.join(knowledge_domains)}. "
    reference_solution += f"The solution involves applying fundamental principles and mathematical reasoning. "
    reference_solution += f"Expected approach: analyze the given information, apply relevant formulas or concepts, "
    reference_solution += f"perform calculations, and interpret the results in the context of the problem."
    
    # Determine knowledge required
    if not knowledge_domains:
        knowledge_domains = [category]
    
    # Add related domains based on difficulty
    if difficulty > 0.5 and len(knowledge_domains) < 3:
        related = {
            "physics": ["mathematics", "engineering"],
            "mathematics": ["physics", "computer_science"],
            "biology": ["chemistry", "physics"],
            "chemistry": ["physics", "mathematics"],
            "computer_science": ["mathematics", "engineering"],
            "philosophy": ["mathematics", "cosmology"],
            "engineering": ["physics", "mathematics"],
            "cosmology": ["physics", "mathematics"],
        }
        if category in related:
            knowledge_domains.extend(random.sample(related[category], min(1, 3 - len(knowledge_domains))))
    
    result = {
        "question": question,
        "difficulty": difficulty,
        "category": category,
        "knowledgeRequired": list(set(knowledge_domains)),
        "referenceSolution": reference_solution,
        "sources": [
            f"Generated for user level {user_level}",
            f"Difficulty: {difficulty:.2f}",
        ],
        "metadata": {
            "generatedBy": "LaniakeA AI Problem Generator",
            "version": "0.0.03",
            "userLevel": user_level,
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
        
        difficulty = params.get("difficulty", 0.5)
        category = params.get("category", "physics")
        knowledge_domains = params.get("knowledgeDomains", [])
        user_level = params.get("userLevel", 1)
        
        result = generate_problem(difficulty, category, knowledge_domains, user_level)
        print(json.dumps(result))
        return 0
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return 1

if __name__ == "__main__":
    sys.exit(main())
