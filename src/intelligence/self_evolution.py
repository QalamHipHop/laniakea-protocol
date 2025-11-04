"""
Self-Evolution System - سیستم خودتکاملی
یک سیستم هوشمند که کد خود را تحلیل، بهبود و آپدیت می‌کند
"""

import ast
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import hashlib

from openai import OpenAI


class CodeAnalyzer:
    """تحلیلگر کد برای شناسایی الگوها و بهبودها"""
    
    def __init__(self):
        self.patterns = {
            'complexity': [],
            'duplicates': [],
            'optimizations': [],
            'security': []
        }
    
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """تحلیل یک فایل پایتون"""
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
                'imports': self._extract_imports(tree),
                'docstring_coverage': self._check_docstrings(tree),
                'hash': hashlib.sha256(code.encode()).hexdigest()
            }
            
            return analysis
        except Exception as e:
            return {'error': str(e), 'filepath': filepath}
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """محاسبه پیچیدگی کد (McCabe Complexity)"""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """استخراج import ها"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        return imports
    
    def _check_docstrings(self, tree: ast.AST) -> float:
        """بررسی پوشش docstring"""
        total_functions = 0
        documented = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                total_functions += 1
                if ast.get_docstring(node):
                    documented += 1
        
        return documented / total_functions if total_functions > 0 else 0.0


class SelfEvolutionEngine:
    """موتور خودتکاملی که کد را بهبود می‌دهد"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analyzer = CodeAnalyzer()
        self.client = OpenAI()  # از متغیر محیطی استفاده می‌کند
        self.evolution_log = []
        self.version = "0.0.1"
        
    async def scan_project(self) -> Dict[str, Any]:
        """اسکن کامل پروژه"""
        print("🔍 Scanning project structure...")
        
        python_files = list(self.project_root.rglob("*.py"))
        analyses = []
        
        for filepath in python_files:
            if '__pycache__' not in str(filepath) and 'venv' not in str(filepath):
                analysis = self.analyzer.analyze_file(str(filepath))
                analyses.append(analysis)
        
        project_stats = {
            'total_files': len(analyses),
            'total_lines': sum(a.get('lines', 0) for a in analyses),
            'total_functions': sum(a.get('functions', 0) for a in analyses),
            'total_classes': sum(a.get('classes', 0) for a in analyses),
            'avg_complexity': sum(a.get('complexity_score', 0) for a in analyses) / len(analyses) if analyses else 0,
            'files': analyses,
            'timestamp': datetime.now().isoformat()
        }
        
        return project_stats
    
    async def suggest_improvements(self, project_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """پیشنهاد بهبودها با استفاده از AI"""
        print("🧠 Analyzing code patterns with AI...")
        
        # انتخاب فایل‌های پیچیده برای بهبود
        complex_files = sorted(
            [f for f in project_stats['files'] if 'error' not in f],
            key=lambda x: x.get('complexity_score', 0),
            reverse=True
        )[:5]
        
        suggestions = []
        
        for file_info in complex_files:
            try:
                with open(file_info['filepath'], 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # درخواست از AI برای تحلیل
                response = self.client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert code reviewer specializing in Python optimization, security, and best practices."
                        },
                        {
                            "role": "user",
                            "content": f"""Analyze this Python code and suggest specific improvements:

File: {file_info['filepath']}
Complexity Score: {file_info['complexity_score']}
Lines: {file_info['lines']}

Code:
```python
{code[:3000]}  # محدود کردن برای جلوگیری از token زیاد
```

Provide 3-5 specific, actionable improvements focusing on:
1. Performance optimization
2. Code readability
3. Security enhancements
4. Modern Python patterns
5. Error handling

Format as JSON array of objects with: {{"type": "...", "description": "...", "priority": "high/medium/low"}}"""
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                ai_suggestions = response.choices[0].message.content
                
                # تلاش برای parse کردن JSON
                try:
                    parsed_suggestions = json.loads(ai_suggestions)
                    suggestions.append({
                        'file': file_info['filepath'],
                        'suggestions': parsed_suggestions
                    })
                except json.JSONDecodeError:
                    suggestions.append({
                        'file': file_info['filepath'],
                        'suggestions': [{'type': 'general', 'description': ai_suggestions, 'priority': 'medium'}]
                    })
                
                await asyncio.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"⚠️ Error analyzing {file_info['filepath']}: {e}")
        
        return suggestions
    
    async def auto_improve_code(self, filepath: str, suggestion: Dict[str, Any]) -> bool:
        """بهبود خودکار کد بر اساس پیشنهاد"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # درخواست بهبود کد از AI
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code refactoring expert. Improve the code while maintaining functionality."
                    },
                    {
                        "role": "user",
                        "content": f"""Improve this code based on the suggestion:

Suggestion: {suggestion['description']}

Original Code:
```python
{original_code}
```

Return ONLY the improved code, no explanations."""
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            improved_code = response.choices[0].message.content
            
            # حذف markdown code blocks اگر وجود داشت
            if improved_code.startswith('```python'):
                improved_code = improved_code.split('```python')[1].split('```')[0].strip()
            elif improved_code.startswith('```'):
                improved_code = improved_code.split('```')[1].split('```')[0].strip()
            
            # ذخیره نسخه بهبود یافته
            backup_path = filepath + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_code)
            
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
        """فرآیند کامل تکامل"""
        print("🌱 Starting self-evolution process...")
        
        # 1. اسکن پروژه
        stats = await self.scan_project()
        
        # 2. دریافت پیشنهادات
        suggestions = await self.suggest_improvements(stats)
        
        # 3. اعمال بهبودها (اگر درخواست شده)
        applied = []
        if auto_apply:
            for item in suggestions:
                for suggestion in item['suggestions']:
                    if suggestion.get('priority') == 'high':
                        success = await self.auto_improve_code(item['file'], suggestion)
                        if success:
                            applied.append(item['file'])
        
        evolution_report = {
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'project_stats': stats,
            'suggestions': suggestions,
            'applied_improvements': applied,
            'evolution_log': self.evolution_log
        }
        
        # ذخیره گزارش
        report_path = self.project_root / 'EVOLUTION_REPORT.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(evolution_report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Evolution complete! Report saved to {report_path}")
        
        return evolution_report


class ContinuousEvolution:
    """تکامل مداوم در پس‌زمینه"""
    
    def __init__(self, project_root: str, interval_hours: int = 24):
        self.engine = SelfEvolutionEngine(project_root)
        self.interval = interval_hours * 3600
        self.running = False
    
    async def start(self):
        """شروع تکامل مداوم"""
        self.running = True
        print(f"🔄 Continuous evolution started (interval: {self.interval/3600}h)")
        
        while self.running:
            try:
                await self.engine.evolve(auto_apply=False)
                await asyncio.sleep(self.interval)
            except Exception as e:
                print(f"❌ Evolution cycle failed: {e}")
                await asyncio.sleep(3600)  # تلاش مجدد بعد از 1 ساعت
    
    def stop(self):
        """توقف تکامل مداوم"""
        self.running = False
        print("⏸️ Continuous evolution stopped")


# تابع کمکی برای استفاده آسان
async def run_evolution(project_root: str = ".", auto_apply: bool = False):
    """اجرای یک چرخه تکامل"""
    engine = SelfEvolutionEngine(project_root)
    return await engine.evolve(auto_apply=auto_apply)


if __name__ == "__main__":
    # تست سیستم
    import sys
    
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    auto_apply = "--apply" in sys.argv
    
    result = asyncio.run(run_evolution(project_path, auto_apply))
    print(f"\n📊 Evolution Summary:")
    print(f"  Files analyzed: {result['project_stats']['total_files']}")
    print(f"  Total lines: {result['project_stats']['total_lines']}")
    print(f"  Suggestions: {len(result['suggestions'])}")
    print(f"  Applied: {len(result['applied_improvements'])}")
