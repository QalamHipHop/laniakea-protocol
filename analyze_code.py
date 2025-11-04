"""
اسکریپت تحلیل خودکار کدهای پروژه
"""
import os
import ast
import json
from pathlib import Path
from collections import defaultdict

def analyze_python_file(filepath):
    """تحلیل یک فایل پایتون"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return {"status": "empty", "lines": 0}
        
        tree = ast.parse(content)
        
        classes = []
        functions = []
        imports = []
        todos = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append({
                    "name": node.name,
                    "methods": methods,
                    "line": node.lineno
                })
            elif isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
                if node.col_offset == 0:  # تابع سطح بالا
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": len(node.args.args)
                    })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node.lineno)
        
        # جستجوی TODO/FIXME
        for i, line in enumerate(content.split('\n'), 1):
            if 'TODO' in line or 'FIXME' in line or 'NotImplemented' in line:
                todos.append({"line": i, "text": line.strip()})
        
        return {
            "status": "implemented",
            "lines": len(content.split('\n')),
            "classes": classes,
            "functions": functions,
            "imports": len(imports),
            "todos": todos
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}

def analyze_project(root_dir):
    """تحلیل کل پروژه"""
    results = {}
    
    for filepath in Path(root_dir).rglob("*.py"):
        if '.venv' in str(filepath) or 'venv' in str(filepath):
            continue
        
        rel_path = str(filepath.relative_to(root_dir))
        results[rel_path] = analyze_python_file(filepath)
    
    return results

if __name__ == "__main__":
    project_root = "/home/ubuntu/laniakea-protocol"
    results = analyze_project(project_root)
    
    # خلاصه
    total_files = len(results)
    empty_files = sum(1 for r in results.values() if r.get("status") == "empty")
    implemented_files = sum(1 for r in results.values() if r.get("status") == "implemented")
    error_files = sum(1 for r in results.values() if r.get("status") == "error")
    total_lines = sum(r.get("lines", 0) for r in results.values())
    total_classes = sum(len(r.get("classes", [])) for r in results.values())
    total_functions = sum(len(r.get("functions", [])) for r in results.values())
    total_todos = sum(len(r.get("todos", [])) for r in results.values())
    
    print("=" * 60)
    print("📊 تحلیل کد پروژه Laniakea Protocol")
    print("=" * 60)
    print(f"تعداد کل فایل‌ها: {total_files}")
    print(f"فایل‌های خالی: {empty_files}")
    print(f"فایل‌های پیاده‌سازی شده: {implemented_files}")
    print(f"فایل‌های با خطا: {error_files}")
    print(f"تعداد کل خطوط: {total_lines}")
    print(f"تعداد کلاس‌ها: {total_classes}")
    print(f"تعداد توابع: {total_functions}")
    print(f"تعداد TODO/FIXME: {total_todos}")
    print("=" * 60)
    
    # فایل‌های خالی
    print("\n🔍 فایل‌های خالی:")
    for path, data in results.items():
        if data.get("status") == "empty":
            print(f"  - {path}")
    
    # فایل‌های با TODO
    print("\n📝 فایل‌های با TODO/FIXME:")
    for path, data in results.items():
        if data.get("todos"):
            print(f"  - {path}: {len(data['todos'])} TODO")
    
    # ماژول‌های اصلی
    print("\n📦 ماژول‌های اصلی:")
    modules = defaultdict(lambda: {"files": 0, "lines": 0, "classes": 0})
    for path, data in results.items():
        if path.startswith("src/"):
            module = path.split("/")[1]
            modules[module]["files"] += 1
            modules[module]["lines"] += data.get("lines", 0)
            modules[module]["classes"] += len(data.get("classes", []))
    
    for module, stats in sorted(modules.items()):
        print(f"  - {module}: {stats['files']} files, {stats['lines']} lines, {stats['classes']} classes")
    
    # ذخیره نتایج
    with open("/home/ubuntu/laniakea-protocol/code_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ نتایج کامل در code_analysis.json ذخیره شد")
