#!/usr/bin/env python3
"""
Laniakea Protocol - Automated Code Analysis Tool
تحلیل خودکار کدها برای شناسایی مشکلات و نواقص
"""

import os
import ast
import json
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

class CodeAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
        
    def analyze_python_file(self, filepath: Path) -> Dict[str, Any]:
        """تحلیل یک فایل پایتون"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content, filename=str(filepath))
            
            file_issues = {
                'imports': [],
                'functions': [],
                'classes': [],
                'todos': [],
                'complexity': 0,
                'lines': len(content.split('\n'))
            }
            
            # تحلیل imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_issues['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        file_issues['imports'].append(node.module)
                        
                # تحلیل functions
                elif isinstance(node, ast.FunctionDef):
                    file_issues['functions'].append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'args': len(node.args.args),
                        'has_docstring': ast.get_docstring(node) is not None
                    })
                    
                # تحلیل classes
                elif isinstance(node, ast.ClassDef):
                    file_issues['classes'].append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        'has_docstring': ast.get_docstring(node) is not None
                    })
            
            # جستجوی TODO و FIXME
            for i, line in enumerate(content.split('\n'), 1):
                if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                    file_issues['todos'].append({
                        'line': i,
                        'content': line.strip()
                    })
                    
            return file_issues
            
        except SyntaxError as e:
            self.issues['syntax_errors'].append({
                'file': str(filepath),
                'error': str(e)
            })
            return None
        except Exception as e:
            self.issues['parse_errors'].append({
                'file': str(filepath),
                'error': str(e)
            })
            return None
    
    def check_missing_files(self):
        """بررسی فایل‌های ضروری که وجود ندارند"""
        essential_files = [
            '.env.example',
            'pytest.ini',
            '.gitignore',
            'docker-compose.yml',
            'Dockerfile'
        ]
        
        for filename in essential_files:
            filepath = self.project_root / filename
            if not filepath.exists():
                self.issues['missing_files'].append(filename)
            else:
                # بررسی اگر فایل خالی است
                if filepath.stat().st_size == 0:
                    self.issues['empty_files'].append(filename)
    
    def analyze_imports(self, all_files_data: Dict):
        """تحلیل وابستگی‌های import"""
        all_imports = defaultdict(int)
        
        for filepath, data in all_files_data.items():
            if data and 'imports' in data:
                for imp in data['imports']:
                    all_imports[imp] += 1
        
        # پیدا کردن imports استفاده نشده یا کمتر استفاده شده
        rarely_used = {k: v for k, v in all_imports.items() if v == 1}
        
        return {
            'total_unique_imports': len(all_imports),
            'rarely_used_imports': rarely_used,
            'most_used_imports': dict(sorted(all_imports.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def check_documentation(self, all_files_data: Dict):
        """بررسی کیفیت مستندات"""
        undocumented_functions = []
        undocumented_classes = []
        
        for filepath, data in all_files_data.items():
            if not data:
                continue
                
            for func in data.get('functions', []):
                if not func['has_docstring']:
                    undocumented_functions.append({
                        'file': filepath,
                        'function': func['name'],
                        'line': func['lineno']
                    })
            
            for cls in data.get('classes', []):
                if not cls['has_docstring']:
                    undocumented_classes.append({
                        'file': filepath,
                        'class': cls['name'],
                        'line': cls['lineno']
                    })
        
        return {
            'undocumented_functions': undocumented_functions[:20],  # فقط 20 مورد اول
            'undocumented_classes': undocumented_classes,
            'total_undocumented_functions': len(undocumented_functions),
            'total_undocumented_classes': len(undocumented_classes)
        }
    
    def analyze_project(self):
        """تحلیل کل پروژه"""
        print("🔍 شروع تحلیل پروژه Laniakea Protocol...")
        
        # پیدا کردن تمام فایل‌های پایتون
        python_files = list(self.project_root.rglob('*.py'))
        python_files = [f for f in python_files if '.git' not in str(f) and 'venv' not in str(f)]
        
        print(f"📁 تعداد فایل‌های پایتون یافت شده: {len(python_files)}")
        
        # تحلیل هر فایل
        all_files_data = {}
        for filepath in python_files:
            rel_path = filepath.relative_to(self.project_root)
            data = self.analyze_python_file(filepath)
            if data:
                all_files_data[str(rel_path)] = data
                self.stats['total_lines'] += data['lines']
                self.stats['total_functions'] += len(data['functions'])
                self.stats['total_classes'] += len(data['classes'])
        
        print(f"✅ تحلیل {len(all_files_data)} فایل کامل شد")
        
        # بررسی‌های اضافی
        self.check_missing_files()
        
        # تحلیل imports
        import_analysis = self.analyze_imports(all_files_data)
        
        # بررسی مستندات
        doc_analysis = self.check_documentation(all_files_data)
        
        # جمع‌آوری نتایج
        results = {
            'summary': {
                'total_python_files': len(python_files),
                'successfully_analyzed': len(all_files_data),
                'total_lines_of_code': self.stats['total_lines'],
                'total_functions': self.stats['total_functions'],
                'total_classes': self.stats['total_classes']
            },
            'issues': dict(self.issues),
            'import_analysis': import_analysis,
            'documentation_analysis': doc_analysis,
            'files_data': all_files_data
        }
        
        return results

def main():
    analyzer = CodeAnalyzer('/home/ubuntu/laniakea-protocol')
    results = analyzer.analyze_project()
    
    # ذخیره نتایج
    output_file = '/home/ubuntu/laniakea-protocol/code_analysis_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 گزارش کامل در فایل ذخیره شد: {output_file}")
    
    # نمایش خلاصه
    print("\n" + "="*60)
    print("📈 خلاصه تحلیل:")
    print("="*60)
    print(f"✓ تعداد فایل‌های پایتون: {results['summary']['total_python_files']}")
    print(f"✓ خطوط کد: {results['summary']['total_lines_of_code']:,}")
    print(f"✓ تعداد توابع: {results['summary']['total_functions']}")
    print(f"✓ تعداد کلاس‌ها: {results['summary']['total_classes']}")
    
    print(f"\n⚠️  مشکلات یافت شده:")
    print(f"  - خطاهای Syntax: {len(results['issues'].get('syntax_errors', []))}")
    print(f"  - خطاهای Parse: {len(results['issues'].get('parse_errors', []))}")
    print(f"  - فایل‌های گمشده: {len(results['issues'].get('missing_files', []))}")
    print(f"  - فایل‌های خالی: {len(results['issues'].get('empty_files', []))}")
    
    print(f"\n📚 وضعیت مستندات:")
    print(f"  - توابع بدون docstring: {results['documentation_analysis']['total_undocumented_functions']}")
    print(f"  - کلاس‌های بدون docstring: {results['documentation_analysis']['total_undocumented_classes']}")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
