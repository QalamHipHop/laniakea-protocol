"""
LaniakeA Protocol - Knowledge Extractor Agent (KEA)
Extracts hard problems from scientific sources (NASA, Wikipedia, Universities, etc.)
"""

import os
import json
import logging
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import random

logger = logging.getLogger("KEA")


class Problem:
    """Represents a hard problem extracted from scientific sources"""
    
    def __init__(self, 
                 title: str,
                 description: str,
                 difficulty: float,
                 source: str,
                 category: str,
                 keywords: List[str],
                 metadata: Dict[str, Any] = None):
        """
        Initialize a Problem
        
        Args:
            title: Problem title
            description: Detailed problem description
            difficulty: Difficulty level (0.0 to 1.0)
            source: Source URL or reference
            category: Problem category (physics, mathematics, biology, etc.)
            keywords: List of relevant keywords
            metadata: Additional metadata
        """
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.source = source
        self.category = category
        self.keywords = keywords
        self.metadata = metadata or {}
        self.problem_id = self._generate_id()
        self.created_at = datetime.utcnow().isoformat()
    
    def _generate_id(self) -> str:
        """Generate unique problem ID"""
        content = f"{self.title}{self.description}{self.source}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'problem_id': self.problem_id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'source': self.source,
            'category': self.category,
            'keywords': self.keywords,
            'metadata': self.metadata,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Problem':
        """Create Problem from dictionary"""
        return cls(
            title=data['title'],
            description=data['description'],
            difficulty=data['difficulty'],
            source=data['source'],
            category=data['category'],
            keywords=data['keywords'],
            metadata=data.get('metadata', {})
        )


class KnowledgeExtractorAgent:
    """
    Knowledge Extractor Agent (KEA)
    Discovers and extracts hard problems from scientific sources
    """
    
    # Problem categories
    CATEGORIES = [
        'physics', 'mathematics', 'astronomy', 'biology', 
        'chemistry', 'computer_science', 'engineering',
        'cosmology', 'quantum_mechanics', 'artificial_intelligence'
    ]
    
    # Difficulty levels
    DIFFICULTY_LEVELS = {
        'beginner': (0.1, 0.3),
        'intermediate': (0.3, 0.6),
        'advanced': (0.6, 0.8),
        'expert': (0.8, 1.0)
    }
    
    def __init__(self, use_openai: bool = False):
        """
        Initialize KEA
        
        Args:
            use_openai: Whether to use OpenAI API for problem generation
        """
        self.use_openai = use_openai
        self.openai_client = None
        
        if use_openai:
            self._init_openai()
        
        self.problem_cache: List[Problem] = []
        self.sources = self._init_sources()
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            self.openai_client = OpenAI()  # Uses OPENAI_API_KEY from environment
            logger.info("✅ OpenAI client initialized")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI initialization failed: {e}")
            self.use_openai = False
    
    def _init_sources(self) -> Dict[str, str]:
        """Initialize scientific sources"""
        return {
            'nasa': 'https://www.nasa.gov',
            'wikipedia': 'https://en.wikipedia.org',
            'arxiv': 'https://arxiv.org',
            'nature': 'https://www.nature.com',
            'science': 'https://www.science.org',
            'mit': 'https://www.mit.edu',
            'stanford': 'https://www.stanford.edu',
            'caltech': 'https://www.caltech.edu'
        }
    
    def extract_problems(self, 
                        category: Optional[str] = None,
                        difficulty_level: Optional[str] = None,
                        count: int = 10) -> List[Problem]:
        """
        Extract problems from scientific sources
        
        Args:
            category: Specific category to extract from
            difficulty_level: Difficulty level (beginner, intermediate, advanced, expert)
            count: Number of problems to extract
            
        Returns:
            List of Problem objects
        """
        if self.use_openai and self.openai_client:
            return self._extract_with_openai(category, difficulty_level, count)
        else:
            return self._extract_predefined(category, difficulty_level, count)
    
    def _extract_with_openai(self, 
                            category: Optional[str],
                            difficulty_level: Optional[str],
                            count: int) -> List[Problem]:
        """Extract problems using OpenAI API"""
        problems = []
        
        try:
            # Determine difficulty range
            if difficulty_level and difficulty_level in self.DIFFICULTY_LEVELS:
                diff_min, diff_max = self.DIFFICULTY_LEVELS[difficulty_level]
            else:
                diff_min, diff_max = 0.1, 1.0
            
            # Select category
            selected_category = category if category in self.CATEGORIES else random.choice(self.CATEGORIES)
            
            # Create prompt for OpenAI
            prompt = f"""Generate {count} challenging scientific problems in the field of {selected_category}.
            
Each problem should be:
- Scientifically accurate and based on real research questions
- Challenging enough for difficulty level: {difficulty_level or 'mixed'}
- Include a clear title and detailed description
- Reference real scientific concepts or ongoing research

Format each problem as JSON with fields: title, description, keywords (list of 3-5 keywords)

Return a JSON array of problems."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a scientific knowledge extraction system for the LaniakeA Protocol. Generate challenging, scientifically accurate problems."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            problem_data = json.loads(content.strip())
            
            # Create Problem objects
            for i, data in enumerate(problem_data[:count]):
                difficulty = diff_min + (diff_max - diff_min) * (i / max(count - 1, 1))
                
                problem = Problem(
                    title=data.get('title', 'Untitled Problem'),
                    description=data.get('description', ''),
                    difficulty=round(difficulty, 2),
                    source=random.choice(list(self.sources.values())),
                    category=selected_category,
                    keywords=data.get('keywords', []),
                    metadata={'generated_by': 'openai', 'model': 'gpt-4.1-mini'}
                )
                problems.append(problem)
            
            logger.info(f"✅ Generated {len(problems)} problems using OpenAI")
            
        except Exception as e:
            logger.error(f"❌ OpenAI problem extraction failed: {e}")
            # Fallback to predefined problems
            return self._extract_predefined(category, difficulty_level, count)
        
        return problems
    
    def _extract_predefined(self,
                           category: Optional[str],
                           difficulty_level: Optional[str],
                           count: int) -> List[Problem]:
        """Extract problems from predefined database"""
        
        # Predefined problem templates
        problem_templates = {
            'physics': [
                {
                    'title': 'Dark Matter Distribution in Galaxy Clusters',
                    'description': 'Analyze the gravitational lensing data to map the distribution of dark matter in the Coma Cluster. Calculate the mass-to-light ratio and compare with theoretical predictions.',
                    'keywords': ['dark matter', 'gravitational lensing', 'galaxy clusters', 'cosmology']
                },
                {
                    'title': 'Quantum Entanglement in Macroscopic Systems',
                    'description': 'Design an experiment to demonstrate quantum entanglement in a system with more than 1000 particles. Propose methods to maintain coherence and measure entanglement entropy.',
                    'keywords': ['quantum entanglement', 'macroscopic quantum', 'coherence', 'entropy']
                }
            ],
            'mathematics': [
                {
                    'title': 'Riemann Hypothesis Verification for Large Zeros',
                    'description': 'Develop an algorithm to verify the Riemann Hypothesis for the first 10^15 non-trivial zeros of the zeta function. Optimize for computational efficiency.',
                    'keywords': ['Riemann hypothesis', 'zeta function', 'number theory', 'algorithm']
                },
                {
                    'title': 'Topological Data Analysis of High-Dimensional Manifolds',
                    'description': 'Apply persistent homology to analyze the topology of a 12-dimensional manifold representing cosmic microwave background data.',
                    'keywords': ['topology', 'persistent homology', 'manifolds', 'data analysis']
                }
            ],
            'astronomy': [
                {
                    'title': 'Exoplanet Atmosphere Composition Analysis',
                    'description': 'Using James Webb Space Telescope data, determine the atmospheric composition of TRAPPIST-1e. Identify biosignature gases and estimate their abundances.',
                    'keywords': ['exoplanets', 'atmospheres', 'biosignatures', 'spectroscopy']
                },
                {
                    'title': 'Supermassive Black Hole Merger Dynamics',
                    'description': 'Simulate the merger of two supermassive black holes with masses 10^9 and 10^8 solar masses. Calculate gravitational wave signatures and electromagnetic counterparts.',
                    'keywords': ['black holes', 'mergers', 'gravitational waves', 'simulation']
                }
            ],
            'biology': [
                {
                    'title': 'Protein Folding Prediction for Novel Enzymes',
                    'description': 'Predict the 3D structure of a newly discovered enzyme from extremophile bacteria. Identify active sites and propose catalytic mechanisms.',
                    'keywords': ['protein folding', 'enzymes', 'structure prediction', 'extremophiles']
                },
                {
                    'title': 'Neural Network Connectivity in C. elegans',
                    'description': 'Map the complete connectome of C. elegans and identify key neural circuits responsible for chemotaxis behavior.',
                    'keywords': ['connectome', 'neural networks', 'C. elegans', 'behavior']
                }
            ],
            'computer_science': [
                {
                    'title': 'Quantum Algorithm for Graph Isomorphism',
                    'description': 'Develop a quantum algorithm to solve the graph isomorphism problem with polynomial speedup over classical algorithms.',
                    'keywords': ['quantum computing', 'graph theory', 'algorithms', 'complexity']
                },
                {
                    'title': 'AI Safety in Multi-Agent Systems',
                    'description': 'Design a verification framework to ensure safety properties in a system of 1000+ autonomous AI agents with conflicting objectives.',
                    'keywords': ['AI safety', 'multi-agent systems', 'verification', 'game theory']
                }
            ]
        }
        
        # Select category
        selected_category = category if category in problem_templates else random.choice(list(problem_templates.keys()))
        
        # Determine difficulty range
        if difficulty_level and difficulty_level in self.DIFFICULTY_LEVELS:
            diff_min, diff_max = self.DIFFICULTY_LEVELS[difficulty_level]
        else:
            diff_min, diff_max = 0.1, 1.0
        
        # Generate problems
        problems = []
        templates = problem_templates[selected_category]
        
        for i in range(count):
            template = templates[i % len(templates)]
            difficulty = diff_min + (diff_max - diff_min) * random.random()
            
            problem = Problem(
                title=template['title'],
                description=template['description'],
                difficulty=round(difficulty, 2),
                source=random.choice(list(self.sources.values())),
                category=selected_category,
                keywords=template['keywords'],
                metadata={'generated_by': 'predefined', 'template_id': i % len(templates)}
            )
            problems.append(problem)
        
        logger.info(f"✅ Generated {len(problems)} predefined problems")
        return problems
    
    def save_problems(self, problems: List[Problem], filepath: str):
        """Save problems to JSON file"""
        try:
            data = [p.to_dict() for p in problems]
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"✅ Saved {len(problems)} problems to {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save problems: {e}")
    
    def load_problems(self, filepath: str) -> List[Problem]:
        """Load problems from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            problems = [Problem.from_dict(p) for p in data]
            logger.info(f"✅ Loaded {len(problems)} problems from {filepath}")
            return problems
        except Exception as e:
            logger.error(f"❌ Failed to load problems: {e}")
            return []


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Initialize KEA
    kea = KnowledgeExtractorAgent(use_openai=True)
    
    # Extract problems
    problems = kea.extract_problems(
        category='physics',
        difficulty_level='advanced',
        count=5
    )
    
    # Display problems
    print("\n" + "="*60)
    print("EXTRACTED PROBLEMS")
    print("="*60)
    
    for i, problem in enumerate(problems, 1):
        print(f"\n{i}. {problem.title}")
        print(f"   Category: {problem.category}")
        print(f"   Difficulty: {problem.difficulty:.2f}")
        print(f"   Keywords: {', '.join(problem.keywords)}")
        print(f"   Description: {problem.description[:100]}...")
    
    # Save problems
    kea.save_problems(problems, '/tmp/laniakea_problems.json')
