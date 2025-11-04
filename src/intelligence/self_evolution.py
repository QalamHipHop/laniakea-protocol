'''
Self-Evolution System - سیستم خودتکاملی
یک سیستم هوشمند که کد خود را تحلیل، بهبود و آپدیت می‌کند
'''

import ast
import os
import json
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import hashlib

from src.intelligence.ai_api import get_ai_api

class CodeAnalyzer:
    '''تحلیلگر کد برای شناسایی الگوها و بهبودها'''

    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        '''تحلیل یک فایل پایتون'''
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()

            tree = ast.parse(code)

            analysis = {
                'filepath': filepath,
                'lines': len(code.split('\n')),
                'functions': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                'classes': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                'complexity_score': self._calculate_complexity(tree),
                'hash': hashlib.sha256(code.encode()).hexdigest()
            }
            return analysis
        except Exception as e:
            return {'error': str(e), 'filepath': filepath}

    def _calculate_complexity(self, tree: ast.AST) -> int:
        '''محاسبه پیچیدگی کد (McCabe Complexity)'''
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity

class SelfEvolutionEngine:
    '''موتور خودتکاملی که کد را بهبود می‌دهد'''

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analyzer = CodeAnalyzer()
        self.ai_api = get_ai_api()
        self.evolution_log = []
        self.version = "0.0.1"

    async def scan_project(self) -> Dict[str, Any]:
        '''اسکن کامل پروژه'''
        print("🔍 Scanning project structure...")
        python_files = list(self.project_root.rglob("*.py"))
        analyses = [self.analyzer.analyze_file(str(fp)) for fp in python_files if '__pycache__' not in str(fp) and 'venv' not in str(fp)]

        valid_analyses = [a for a in analyses if 'error' not in a]
        project_stats = {
            'total_files': len(valid_analyses),
            'total_lines': sum(a.get('lines', 0) for a in valid_analyses),
            'avg_complexity': sum(a.get('complexity_score', 0) for a in valid_analyses) / len(valid_analyses) if valid_analyses else 0,
            'files': valid_analyses,
            'timestamp': datetime.now().isoformat()
        }
        return project_stats

    async def suggest_improvements(self, project_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        '''پیشنهاد بهبودها با استفاده از AI'''
        print("🧠 Analyzing code patterns with AI...")
        complex_files = sorted(project_stats['files'], key=lambda x: x.get('complexity_score', 0), reverse=True)[:3]
        suggestions = []

        for file_info in complex_files:
            try:
                with open(file_info['filepath'], 'r', encoding='utf-8') as f:
                    code = f.read()

                prompt = f'''Analyze this Python code and suggest specific improvements:
File: {file_info['filepath']}
Complexity Score: {file_info['complexity_score']}

Code:
```python
{code[:3500]}
```

Provide 3 specific, actionable improvements (performance, readability, security). Format as a JSON array of objects with keys: "type", "description", "priority".'''

                response_text = self.ai_api.generate_text_sync(
                    model="gemini-2.5-flash",
                    system_prompt="You are an expert Python code reviewer.",
                    prompt=prompt,
                    max_tokens=1000
                )

                parsed_suggestions = json.loads(response_text)
                suggestions.append({'file': file_info['filepath'], 'suggestions': parsed_suggestions})
                await asyncio.sleep(1)
            except Exception as e:
                print(f"⚠️ Error analyzing {file_info['filepath']}: {e}")
        return suggestions

    async def auto_improve_code(self, filepath: str, suggestion: Dict[str, Any]) -> bool:
        '''بهبود خودکار کد بر اساس پیشنهاد'''
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_code = f.read()

            prompt = f'''Improve this code based on the suggestion:
Suggestion: {suggestion['description']}

Original Code:
```python
{original_code}
```

Return ONLY the fully improved, complete Python code. Do not add any explanations or markdown.'''

            improved_code = self.ai_api.generate_text_sync(
                model="gemini-2.5-flash",
                system_prompt="You are a code refactoring expert.",
                prompt=prompt,
                max_tokens=4000
            )

            if improved_code.startswith('```python'):
                improved_code = improved_code.split('\n', 1)[1].rsplit('```', 1)[0].strip()

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(improved_code)

            self.evolution_log.append({
                'timestamp': datetime.now().isoformat(),
                'file': filepath,
                'suggestion': suggestion,
                'status': 'applied'
            })
            return True
        except Exception as e:
            print(f"❌ Failed to improve {filepath}: {e}")
            return False

    async def evolve(self, auto_apply: bool = False) -> Dict[str, Any]:
        '''فرآیند کامل تکامل'''
        print("🌱 Starting self-evolution process...")
        stats = await self.scan_project()
        suggestions = await self.suggest_improvements(stats)
        applied = []

        if auto_apply:
            for item in suggestions:
                for suggestion in item.get('suggestions', []):
                    if suggestion.get('priority') == 'high':
                        if await self.auto_improve_code(item['file'], suggestion):
                            applied.append(item['file'])

        report = {
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'project_stats': stats,
            'suggestions': suggestions,
            'applied_improvements': list(set(applied))
        }

        report_path = self.project_root / 'evolution_log.json'
        with open(report_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(report, indent=2, ensure_ascii=False) + '\n')

        print(f"✅ Evolution complete! Report updated in {report_path}")
        return report

async def run_evolution(project_root: str = '.', auto_apply: bool = False):
    '''اجرای یک چرخه تکامل'''
    engine = SelfEvolutionEngine(project_root)
    return await engine.evolve(auto_apply=auto_apply)

if __name__ == "__main__":
    import sys
    project_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    auto_apply = "--apply" in sys.argv
    result = asyncio.run(run_evolution(project_path, auto_apply))
    print("\n📊 Evolution Summary:")
    print(f"  Files analyzed: {result['project_stats']['total_files']}")
    print(f"  Suggestions: {len(result['suggestions'])}")
