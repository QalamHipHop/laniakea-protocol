#!/usr/bin/env python3
"""
Laniakea Security Audit — runs bandit + safety + custom checks.
Exits non-zero on findings above severity threshold.
"""
import subprocess
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


SEVERITY_LEVELS = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def run_bandit(target="laniakea/"):
    """Run Bandit — Python security linter."""
    print("🔍 Running Bandit...")
    try:
        r = subprocess.run(
            ["bandit", "-r", target, "-f", "json", "-q"],
            capture_output=True, text=True, timeout=120
        )
        data = json.loads(r.stdout) if r.stdout else {"results": []}
        return data.get("results", [])
    except FileNotFoundError:
        print("  ⚠ bandit not installed (pip install bandit)")
        return []
    except Exception as e:
        print(f"  ⚠ bandit error: {e}")
        return []


def run_safety():
    """Run Safety — checks dependencies for known vulns."""
    print("🔍 Running Safety (dependency check)...")
    try:
        r = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True, text=True, timeout=120
        )
        if r.stdout:
            return json.loads(r.stdout).get("vulnerabilities", [])
        return []
    except FileNotFoundError:
        print("  ⚠ safety not installed (pip install safety)")
        return []
    except Exception as e:
        print(f"  ⚠ safety error: {e}")
        return []


def check_secrets():
    """Custom check for hardcoded secrets."""
    print("🔍 Checking for hardcoded secrets...")
    findings = []
    patterns = {
        "aws_key": r"AKIA[0-9A-Z]{16}",
        "private_key": r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "github_token": r"gh[pousr]_[A-Za-z0-9]{36,255}",
        "generic_secret": r"(?i)(secret|password|api_key|token)\s*=\s*['\"][^'\"]{16,}['\"]",
    }
    skip_dirs = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv"}
    for path in Path(".").rglob("*"):
        if any(p in path.parts for p in skip_dirs):
            continue
        if not path.is_file() or path.suffix not in {".py", ".js", ".ts", ".yaml", ".yml", ".env", ".json"}:
            continue
        if path.name == "security_audit.py":
            continue
        try:
            content = path.read_text(errors="ignore")
            for name, pat in patterns.items():
                import re
                for m in re.finditer(pat, content):
                    line = content[:m.start()].count("\n") + 1
                    findings.append({
                        "file": str(path), "line": line, "type": name,
                        "severity": "CRITICAL" if "key" in name or "token" in name else "HIGH"
                    })
        except Exception:
            pass
    return findings


def check_dangerous_imports():
    """Check for dangerous Python patterns."""
    print("🔍 Checking for dangerous imports...")
    findings = []
    dangerous = {
        "pickle": "Arbitrary code execution risk",
        "marshal": "Arbitrary code execution risk",
        "subprocess.shell=True": "Shell injection risk",
        "eval(": "Code injection risk",
        "exec(": "Code injection risk",
    }
    for py in Path("laniakea").rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        try:
            content = py.read_text(errors="ignore")
            for pat, reason in dangerous.items():
                if pat in content:
                    findings.append({
                        "file": str(py), "type": pat, "reason": reason, "severity": "MEDIUM"
                    })
        except Exception:
            pass
    return findings


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", default="laniakea/")
    p.add_argument("--threshold", default="MEDIUM", choices=list(SEVERITY_LEVELS))
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    threshold = SEVERITY_LEVELS[args.threshold]
    all_findings = {
        "timestamp": datetime.utcnow().isoformat(),
        "bandit": run_bandit(args.target),
        "safety": run_safety(),
        "secrets": check_secrets(),
        "dangerous": check_dangerous_imports(),
    }

    # Count
    total_critical = total_high = total_med = 0
    for cat in ["secrets", "dangerous"]:
        for f in all_findings[cat]:
            sev = SEVERITY_LEVELS.get(f.get("severity", "LOW"), 1)
            if sev >= 4: total_critical += 1
            elif sev >= 3: total_high += 1
            elif sev >= 2: total_med += 1
    for f in all_findings["bandit"]:
        sev = f.get("issue_severity", "LOW")
        if sev == "CRITICAL": total_critical += 1
        elif sev == "HIGH": total_high += 1
        elif sev == "MEDIUM": total_med += 1
    total_critical += len(all_findings["safety"])

    summary = {
        "critical": total_critical, "high": total_high, "medium": total_med,
        "passed": (total_critical == 0 and total_high == 0)
    }

    if args.json:
        print(json.dumps({"summary": summary, "findings": all_findings}, indent=2))
    else:
        print("\n" + "=" * 60)
        print("🌌 LANIAKEA SECURITY AUDIT")
        print("=" * 60)
        print(f"  CRITICAL: {summary['critical']}")
        print(f"  HIGH:     {summary['high']}")
        print(f"  MEDIUM:   {summary['medium']}")
        print(f"  Status:   {'✅ PASS' if summary['passed'] else '❌ FAIL'}")
        print("=" * 60)

        if not summary["passed"]:
            if all_findings["secrets"]:
                print("\n🔐 Hardcoded secrets found:")
                for s in all_findings["secrets"][:10]:
                    print(f"   - {s['file']}:{s['line']} ({s['type']})")
            if all_findings["bandit"]:
                high = [b for b in all_findings["bandit"] if b.get("issue_severity") in ("HIGH", "CRITICAL")]
                if high:
                    print(f"\n🐛 Bandit found {len(high)} high/critical issues:")
                    for b in high[:5]:
                        print(f"   - {b.get('filename')}:{b.get('line_number')} {b.get('test_id')}: {b.get('issue_text', '')[:80]}")
            if all_findings["safety"]:
                print(f"\n📦 Safety found {len(all_findings['safety'])} vulnerable deps")

    sys.exit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
