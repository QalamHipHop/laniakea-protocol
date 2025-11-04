'''
Self-Evolution System - سیستم خودتکاملی (Enhanced)
یک سیستم هوشمند که کد خود را تحلیل، بهبود و آپدیت می‌کند، با استفاده از منطق ValueVector و PoV.
'''

import ast
import os
import json
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import hashlib
import random # برای شبیه‌سازی ValueVector

from src.intelligence.ai_api import get_ai_api
from src.core.models import ValueVector, ValueDimension, Task, ProblemCategory, Solution
from src.core.hash_modernity import HashModernityEngine # برای استفاده از منطق مدرنیته

class CodeAnalyzer:
    '''تحلیلگر کد برای شناسایی الگوها و بهبودها'''

    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        '''تحلیل یک فایل پایتون'''
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()

            tree = ast.parse(code)

            # محاسبه پیچیدگی (McCabe)
            complexity = self._calculate_complexity(tree)
            
            # شبیه‌سازی ValueVector برای کد
            code_value_vector = self._simulate_value_vector(code, complexity)

            analysis = {
                'filepath': filepath,
                'lines': len(code.split('\n')),
                'functions': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                'classes': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                'complexity_score': complexity,
                'value_vector': code_value_vector.to_dict(),
                'hash': hashlib.sha256(code.encode()).hexdigest()
            }
            return analysis
        except Exception as e:
            return {'error': str(e), 'filepath': filepath}

    def _calculate_complexity(self, tree: ast.AST) -> int:
        '''محاسبه پیچیدگی کد (McCabe Complexity)'''
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                complexity += 1
        return complexity
    
    def _simulate_value_vector(self, code: str, complexity: int) -> ValueVector:
        """
        شبیه‌سازی ValueVector برای یک قطعه کد
        این بخش باید در آینده توسط یک LLM/AI پیشرفته‌تر انجام شود.
        """
        lines = len(code.split('\n'))
        
        # دانش (Knowledge): بر اساس تعداد خطوط و پیچیدگی
        knowledge = min(10.0, (lines / 50.0) + (complexity / 10.0))
        
        # محاسبات (Computation): بر اساس پیچیدگی و تعداد حلقه‌ها
        computation = min(10.0, complexity / 5.0)
        
        # خلاقیت (Originality): تصادفی برای شبیه‌سازی نوآوری
        originality = random.uniform(0.0, 5.0)
        
        # آگاهی (Consciousness): بر اساس وجود کلمات کلیدی مرتبط با خودتکاملی
        consciousness = 1.0 if "SelfEvolutionEngine" in code else 0.0
        
        # محیطی و سلامتی (Environmental/Health): فعلاً صفر
        environmental = 0.0
        health = 0.0
        
        # مقیاس‌پذیری (Scalability): بر اساس وجود کلاس‌ها و توابع
        scalability = min(10.0, (lines / 100.0) + (complexity / 20.0))
        
        # اخلاقی (Ethical Alignment): فعلاً تصادفی
        ethical_alignment = random.uniform(0.0, 5.0)
        
        return ValueVector(
            knowledge=knowledge,
            computation=computation,
            originality=originality,
            consciousness=consciousness,
            environmental=environmental,
            health=health,
            scalability=scalability,
            ethical_alignment=ethical_alignment
        )


class SelfEvolutionEngine:
    '''موتور خودتکاملی که کد را بهبود می‌دهد'''

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analyzer = CodeAnalyzer()
        self.ai_api = get_ai_api()
        self.evolution_log = []
        self.version = "0.0.2" # افزایش نسخه
        self.modernity_engine = HashModernityEngine() # استفاده از موتور مدرنیته

    async def scan_project(self) -> Dict[str, Any]:
        '''اسکن کامل پروژه'''
        print("🔍 Scanning project structure...")
        python_files = list(self.project_root.rglob("*.py"))
        analyses = [self.analyzer.analyze_file(str(fp)) for fp in python_files if '__pycache__' not in str(fp) and 'venv' not in str(fp)]

        valid_analyses = [a for a in analyses if 'error' not in a]
        
        total_value_vectors = [ValueVector(**a['value_vector']) for a in valid_analyses]
        total_value = sum(v.total_value() for v in total_value_vectors)

        project_stats = {
            'total_files': len(valid_analyses),
            'total_lines': sum(a.get('lines', 0) for a in valid_analyses),
            'avg_complexity': sum(a.get('complexity_score', 0) for a in valid_analyses) / len(valid_analyses) if valid_analyses else 0,
            'total_value_created': total_value,
            'files': valid_analyses,
            'timestamp': datetime.now().isoformat()
        }
        return project_stats

    async def suggest_improvements(self, project_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        '''پیشنهاد بهبودها با استفاده از AI'''
        print("🧠 Analyzing code patterns with AI...")
        
        # تمرکز بر فایل‌هایی با پیچیدگی بالا و ارزش پایین (نشان‌دهنده ناکارآمدی)
        def efficiency_score(analysis):
            value = ValueVector(**analysis.get('value_vector', {})).total_value()
            complexity = analysis.get('complexity_score', 1)
            return value / complexity if complexity > 0 else 0
            
        inefficient_files = sorted(project_stats['files'], key=efficiency_score)[:3]
        suggestions = []

        for file_info in inefficient_files:
            try:
                with open(file_info['filepath'], 'r', encoding='utf-8') as f:
                    code = f.read()

                # ایجاد یک تسک شبیه‌سازی شده برای ارزیابی مدرنیته
                simulated_task = Task(
                    id="evolution_task",
                    title=f"Improvement for {file_info['filepath']}",
                    description="Refactor code for higher efficiency and value density.",
                    category=ProblemCategory.SYSTEMIC_EVOLUTION,
                    author_id="SelfEvolutionEngine",
                    timestamp=datetime.now().timestamp(),
                    difficulty=file_info['complexity_score'] / 10.0
                )
                
                # محاسبه نرخ مدرنیته فعلی
                current_modernity = self.modernity_engine.assess_modernity_rate(
                    Solution(
                        id="current_solution",
                        task_id="evolution_task",
                        solver_id="current_code",
                        content=code,
                        value_vector=ValueVector(**file_info['value_vector']),
                        timestamp=datetime.now().timestamp()
                    ),
                    simulated_task,
                    [] # در اینجا راه‌حل‌های موجود را نداریم، اما در آینده می‌توان از تاریخچه استفاده کرد
                )

                prompt = f'''Analyze this Python code and suggest specific improvements to increase its Value Vector (especially Knowledge, Scalability, and Originality) and Modernity Rate ({current_modernity:.4f}).
File: {file_info['filepath']}
Current Value Vector: {file_info['value_vector']}
Current Complexity: {file_info['complexity_score']}

Code:
```python
{code[:3500]}
```

Provide 3 specific, actionable improvements (refactoring, pattern application, new features). Format as a JSON array of objects with keys: "type", "description", "priority", "target_value_dimension".'''

                response_text = self.ai_api.generate_text_sync(
                    model="gemini-2.5-flash",
                    system_prompt="You are an expert Python code reviewer focused on maximizing Value Vector and Modernity Rate.",
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

            prompt = f'''Improve this code based on the suggestion to maximize the {suggestion.get('target_value_dimension', 'Value Vector')}:
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
                    # فقط بهبودهای با اولویت بالا و مرتبط با ابعاد جدید را اعمال می‌کنیم
                    if suggestion.get('priority') == 'high' and suggestion.get('target_value_dimension') in [d.value for d in ValueDimension]:
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
        # خواندن محتوای قبلی و اضافه کردن گزارش جدید
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
        except FileNotFoundError:
            log_content = ""
            
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(log_content + json.dumps(report, indent=2, ensure_ascii=False) + ',\n') # اضافه کردن کاما برای JSON آرایه

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
    print(f"  Total Value Created: {result['project_stats']['total_value_created']:.2f}")
    print(f"  Suggestions: {sum(len(s['suggestions']) for s in result['suggestions'])}")
    print(f"  Improvements Applied: {len(result['applied_improvements'])}")
