#!/usr/bin/env python3
"""
Deep Architecture Analyzer for Laniakea Protocol
تحلیل عمیق معماری، وابستگی‌ها و نقاط ضعف
"""

import os
import json
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import re

class DeepArchitectureAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.module_dependencies = defaultdict(set)
        self.circular_deps = []
        self.missing_imports = []
        self.unused_imports = defaultdict(list)
        self.code_smells = defaultdict(list)
        self.security_issues = []
        self.performance_issues = []
        
    def analyze_module_dependencies(self):
        """تحلیل وابستگی‌های بین ماژول‌ها"""
        print("🔍 تحلیل وابستگی‌های ماژول‌ها...")
        
        python_files = list(self.project_root.rglob('*.py'))
        python_files = [f for f in python_files if '.git' not in str(f)]
        
        for filepath in python_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                module_name = self._get_module_name(filepath)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        imported = self._extract_import(node)
                        if imported and imported.startswith('laniakea'):
                            self.module_dependencies[module_name].add(imported)
            except:
                pass
        
        return self.module_dependencies
    
    def _get_module_name(self, filepath: Path) -> str:
        """تبدیل مسیر فایل به نام ماژول"""
        rel_path = filepath.relative_to(self.project_root)
        parts = list(rel_path.parts)
        
        if parts[-1] == '__init__.py':
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1].replace('.py', '')
        
        return '.'.join(parts)
    
    def _extract_import(self, node) -> str:
        """استخراج نام ماژول import شده"""
        if isinstance(node, ast.Import):
            return node.names[0].name if node.names else None
        elif isinstance(node, ast.ImportFrom):
            return node.module
        return None
    
    def detect_circular_dependencies(self):
        """شناسایی وابستگی‌های دایره‌ای"""
        print("🔄 شناسایی وابستگی‌های دایره‌ای...")
        
        def has_path(start, end, visited=None):
            if visited is None:
                visited = set()
            if start == end:
                return True
            if start in visited:
                return False
            visited.add(start)
            
            for neighbor in self.module_dependencies.get(start, []):
                if has_path(neighbor, end, visited):
                    return True
            return False
        
        for module in self.module_dependencies:
            for dep in self.module_dependencies[module]:
                if has_path(dep, module):
                    self.circular_deps.append((module, dep))
        
        return self.circular_deps
    
    def analyze_code_quality(self):
        """تحلیل کیفیت کد و شناسایی Code Smells"""
        print("🔬 تحلیل کیفیت کد...")
        
        python_files = list(self.project_root.rglob('*.py'))
        python_files = [f for f in python_files if '.git' not in str(f)]
        
        for filepath in python_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                rel_path = str(filepath.relative_to(self.project_root))
                
                # بررسی توابع بسیار طولانی
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_lines = node.end_lineno - node.lineno
                        if func_lines > 50:
                            self.code_smells['long_functions'].append({
                                'file': rel_path,
                                'function': node.name,
                                'lines': func_lines,
                                'line': node.lineno
                            })
                        
                        # بررسی تعداد پارامترها
                        if len(node.args.args) > 7:
                            self.code_smells['too_many_parameters'].append({
                                'file': rel_path,
                                'function': node.name,
                                'params': len(node.args.args),
                                'line': node.lineno
                            })
                    
                    # بررسی کلاس‌های بسیار بزرگ
                    elif isinstance(node, ast.ClassDef):
                        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                        if len(methods) > 20:
                            self.code_smells['god_classes'].append({
                                'file': rel_path,
                                'class': node.name,
                                'methods': len(methods),
                                'line': node.lineno
                            })
                
                # بررسی خطوط بسیار طولانی
                for i, line in enumerate(content.split('\n'), 1):
                    if len(line) > 120:
                        self.code_smells['long_lines'].append({
                            'file': rel_path,
                            'line': i,
                            'length': len(line)
                        })
                
            except:
                pass
        
        return self.code_smells
    
    def analyze_security_issues(self):
        """شناسایی مشکلات امنیتی احتمالی"""
        print("🔒 تحلیل مشکلات امنیتی...")
        
        python_files = list(self.project_root.rglob('*.py'))
        
        dangerous_patterns = {
            r'eval\(': 'استفاده از eval() - خطر اجرای کد دلخواه',
            r'exec\(': 'استفاده از exec() - خطر اجرای کد دلخواه',
            r'pickle\.loads': 'استفاده از pickle.loads - خطر deserialization',
            r'os\.system\(': 'استفاده از os.system() - خطر command injection',
            r'subprocess\.call\(.*shell=True': 'استفاده از shell=True - خطر command injection',
            r'password\s*=\s*["\']': 'احتمال hardcoded password',
            r'api_key\s*=\s*["\']': 'احتمال hardcoded API key',
            r'secret\s*=\s*["\']': 'احتمال hardcoded secret',
        }
        
        for filepath in python_files:
            if '.git' in str(filepath):
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                rel_path = str(filepath.relative_to(self.project_root))
                
                for pattern, description in dangerous_patterns.items():
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.security_issues.append({
                            'file': rel_path,
                            'line': line_num,
                            'issue': description,
                            'pattern': pattern
                        })
            except:
                pass
        
        return self.security_issues
    
    def analyze_performance_issues(self):
        """شناسایی مشکلات performance"""
        print("⚡ تحلیل مشکلات performance...")
        
        python_files = list(self.project_root.rglob('*.py'))
        
        for filepath in python_files:
            if '.git' in str(filepath):
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                rel_path = str(filepath.relative_to(self.project_root))
                
                # شناسایی حلقه‌های تو در تو
                for node in ast.walk(tree):
                    if isinstance(node, (ast.For, ast.While)):
                        nested_loops = [n for n in ast.walk(node) 
                                      if isinstance(n, (ast.For, ast.While)) and n != node]
                        if len(nested_loops) >= 2:
                            self.performance_issues.append({
                                'file': rel_path,
                                'line': node.lineno,
                                'issue': 'حلقه‌های تو در تو (3+ سطح) - احتمال O(n³) یا بدتر',
                                'severity': 'high'
                            })
                
            except:
                pass
        
        return self.performance_issues
    
    def check_missing_error_handling(self):
        """بررسی عدم وجود error handling"""
        print("⚠️  بررسی error handling...")
        
        missing_handlers = []
        python_files = list(self.project_root.rglob('*.py'))
        
        for filepath in python_files:
            if '.git' in str(filepath):
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                rel_path = str(filepath.relative_to(self.project_root))
                
                # پیدا کردن توابع بدون try-except
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        has_try = any(isinstance(n, ast.Try) for n in ast.walk(node))
                        
                        # فقط برای توابع API و critical functions
                        if not has_try and ('api' in node.name or 'process' in node.name 
                                          or 'execute' in node.name or 'handle' in node.name):
                            missing_handlers.append({
                                'file': rel_path,
                                'function': node.name,
                                'line': node.lineno
                            })
            except:
                pass
        
        return missing_handlers[:50]  # فقط 50 مورد اول
    
    def generate_report(self):
        """تولید گزارش کامل"""
        print("\n" + "="*70)
        print("📊 شروع تحلیل عمیق معماری...")
        print("="*70)
        
        # اجرای تحلیل‌ها
        dependencies = self.analyze_module_dependencies()
        circular = self.detect_circular_dependencies()
        code_smells = self.analyze_code_quality()
        security = self.analyze_security_issues()
        performance = self.analyze_performance_issues()
        error_handling = self.check_missing_error_handling()
        
        report = {
            'architecture': {
                'total_modules': len(dependencies),
                'module_dependencies': {k: list(v) for k, v in dependencies.items()},
                'circular_dependencies': circular,
                'circular_count': len(circular)
            },
            'code_quality': {
                'long_functions': code_smells.get('long_functions', [])[:20],
                'too_many_parameters': code_smells.get('too_many_parameters', [])[:20],
                'god_classes': code_smells.get('god_classes', []),
                'long_lines_count': len(code_smells.get('long_lines', [])),
                'total_smells': sum(len(v) for v in code_smells.values())
            },
            'security': {
                'issues': security[:30],
                'total_issues': len(security)
            },
            'performance': {
                'issues': performance[:20],
                'total_issues': len(performance)
            },
            'error_handling': {
                'missing_handlers': error_handling,
                'total_missing': len(error_handling)
            }
        }
        
        # ذخیره گزارش
        output_file = self.project_root / 'deep_analysis_report.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ گزارش کامل ذخیره شد: {output_file}")
        
        # نمایش خلاصه
        self._print_summary(report)
        
        return report
    
    def _print_summary(self, report):
        """نمایش خلاصه گزارش"""
        print("\n" + "="*70)
        print("📈 خلاصه تحلیل عمیق معماری")
        print("="*70)
        
        print(f"\n🏗️  معماری:")
        print(f"  - تعداد ماژول‌ها: {report['architecture']['total_modules']}")
        print(f"  - وابستگی‌های دایره‌ای: {report['architecture']['circular_count']}")
        
        print(f"\n🔬 کیفیت کد:")
        print(f"  - توابع طولانی (>50 خط): {len(report['code_quality']['long_functions'])}")
        print(f"  - توابع با پارامترهای زیاد (>7): {len(report['code_quality']['too_many_parameters'])}")
        print(f"  - کلاس‌های بزرگ (>20 متد): {len(report['code_quality']['god_classes'])}")
        print(f"  - مجموع Code Smells: {report['code_quality']['total_smells']}")
        
        print(f"\n🔒 امنیت:")
        print(f"  - مشکلات امنیتی احتمالی: {report['security']['total_issues']}")
        
        print(f"\n⚡ Performance:")
        print(f"  - مشکلات احتمالی: {report['performance']['total_issues']}")
        
        print(f"\n⚠️  Error Handling:")
        print(f"  - توابع بدون try-except: {report['error_handling']['total_missing']}")
        
        print("\n" + "="*70)

def main():
    analyzer = DeepArchitectureAnalyzer('/home/ubuntu/laniakea-protocol')
    analyzer.generate_report()

if __name__ == '__main__':
    main()
