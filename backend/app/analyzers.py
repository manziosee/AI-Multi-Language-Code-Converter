"""Code analysis utilities for complexity, performance, and security."""
import re
from typing import Dict, List, Any


def analyze_complexity(code: str, language: str) -> Dict[str, Any]:
    """Calculate cyclomatic complexity and identify complex functions."""
    lines = code.split('\n')
    complexity = 1
    complex_functions = []
    
    # Count decision points
    decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'case', 'catch', '&&', '||', '?']
    for line in lines:
        for keyword in decision_keywords:
            complexity += line.count(keyword)
    
    # Identify functions
    func_patterns = {
        'python': r'def\s+(\w+)',
        'javascript': r'function\s+(\w+)',
        'typescript': r'function\s+(\w+)',
        'java': r'(public|private|protected)?\s*\w+\s+(\w+)\s*\(',
        'golang': r'func\s+(\w+)',
        'php': r'function\s+(\w+)',
        'c': r'\w+\s+(\w+)\s*\([^)]*\)\s*\{',
        'cpp': r'\w+\s+(\w+)\s*\([^)]*\)\s*\{',
        'csharp': r'(public|private|protected)?\s*\w+\s+(\w+)\s*\(',
        'rust': r'fn\s+(\w+)',
    }
    
    pattern = func_patterns.get(language)
    if pattern:
        for match in re.finditer(pattern, code):
            func_name = match.group(1) if match.lastindex == 1 else match.group(2)
            if complexity > 10:
                complex_functions.append({
                    'name': func_name,
                    'line': code[:match.start()].count('\n') + 1,
                    'complexity': min(complexity, 50)
                })
    
    return {
        'complexity_score': min(complexity, 100),
        'rating': 'Low' if complexity < 10 else 'Medium' if complexity < 20 else 'High',
        'complex_functions': complex_functions[:5],
        'suggestions': ['Break down complex functions', 'Reduce nested conditions'] if complexity > 15 else []
    }


def analyze_performance(code: str, language: str) -> Dict[str, Any]:
    """Detect performance issues and suggest optimizations."""
    issues = []
    
    # Nested loops
    if re.search(r'for.*\n.*for', code, re.MULTILINE):
        issues.append({
            'type': 'nested_loops',
            'severity': 'medium',
            'message': 'Nested loops detected - O(n²) complexity',
            'suggestion': 'Consider using hash maps or optimizing algorithm'
        })
    
    # Repeated calculations in loops
    if re.search(r'(for|while).*\n.*(\w+\([^)]*\))', code):
        issues.append({
            'type': 'repeated_calculation',
            'severity': 'low',
            'message': 'Potential repeated calculations in loop',
            'suggestion': 'Cache results outside the loop'
        })
    
    # String concatenation in loops (Python, Java)
    if language in ['python', 'java'] and re.search(r'(for|while).*\n.*\+.*["\']', code):
        issues.append({
            'type': 'string_concat',
            'severity': 'medium',
            'message': 'String concatenation in loop',
            'suggestion': 'Use join() or StringBuilder for better performance'
        })
    
    # Large data structures
    if re.search(r'\[\s*\d+\s*\*\s*\d{4,}', code):
        issues.append({
            'type': 'memory',
            'severity': 'high',
            'message': 'Large array allocation detected',
            'suggestion': 'Consider generators or streaming for large datasets'
        })
    
    return {
        'issues': issues,
        'score': max(0, 100 - len(issues) * 20)
    }


def analyze_security(code: str, language: str) -> Dict[str, Any]:
    """Scan for security vulnerabilities."""
    vulnerabilities = []
    
    # SQL Injection
    sql_patterns = [
        r'execute\s*\([^)]*\+',
        r'query\s*\([^)]*\+',
        r'SELECT.*\+.*FROM',
        r'INSERT.*\+.*VALUES',
        r'UPDATE.*\+.*SET',
        r'DELETE.*\+.*WHERE'
    ]
    for pattern in sql_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            vulnerabilities.append({
                'type': 'sql_injection',
                'severity': 'critical',
                'message': 'Potential SQL injection vulnerability',
                'suggestion': 'Use parameterized queries or prepared statements'
            })
            break
    
    # XSS vulnerabilities
    if language in ['javascript', 'typescript', 'php']:
        if re.search(r'innerHTML\s*=|document\.write\(|eval\(', code):
            vulnerabilities.append({
                'type': 'xss',
                'severity': 'high',
                'message': 'Potential XSS vulnerability',
                'suggestion': 'Sanitize user input and use textContent instead of innerHTML'
            })
    
    # Hardcoded credentials
    cred_patterns = [
        r'password\s*=\s*["\'][^"\']{3,}["\']',
        r'api[_-]?key\s*=\s*["\'][^"\']{10,}["\']',
        r'secret\s*=\s*["\'][^"\']{10,}["\']',
        r'token\s*=\s*["\'][^"\']{10,}["\']'
    ]
    for pattern in cred_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            vulnerabilities.append({
                'type': 'hardcoded_secret',
                'severity': 'critical',
                'message': 'Hardcoded credentials detected',
                'suggestion': 'Use environment variables or secure vaults'
            })
            break
    
    # Unsafe eval
    if re.search(r'\beval\s*\(', code):
        vulnerabilities.append({
            'type': 'unsafe_eval',
            'severity': 'high',
            'message': 'Unsafe eval() usage detected',
            'suggestion': 'Avoid eval() - use safer alternatives like JSON.parse()'
        })
    
    # Command injection
    if re.search(r'(exec|system|shell_exec|popen)\s*\([^)]*\+', code):
        vulnerabilities.append({
            'type': 'command_injection',
            'severity': 'critical',
            'message': 'Potential command injection vulnerability',
            'suggestion': 'Validate and sanitize all inputs to system commands'
        })
    
    return {
        'vulnerabilities': vulnerabilities,
        'score': max(0, 100 - len(vulnerabilities) * 25),
        'is_secure': len(vulnerabilities) == 0
    }


def get_code_review(code: str, language: str) -> Dict[str, Any]:
    """Generate AI-powered code review suggestions."""
    suggestions = []
    
    # Check for comments
    comment_ratio = len(re.findall(r'#|//|/\*', code)) / max(len(code.split('\n')), 1)
    if comment_ratio < 0.1:
        suggestions.append({
            'category': 'documentation',
            'message': 'Add more comments to explain complex logic',
            'priority': 'low'
        })
    
    # Check for error handling
    has_error_handling = bool(re.search(r'try|catch|except|error', code, re.IGNORECASE))
    if not has_error_handling and len(code) > 200:
        suggestions.append({
            'category': 'error_handling',
            'message': 'Add error handling for robustness',
            'priority': 'high'
        })
    
    # Check for magic numbers
    magic_numbers = re.findall(r'\b\d{2,}\b', code)
    if len(magic_numbers) > 3:
        suggestions.append({
            'category': 'maintainability',
            'message': 'Replace magic numbers with named constants',
            'priority': 'medium'
        })
    
    # Check function length
    lines = code.split('\n')
    if len(lines) > 50:
        suggestions.append({
            'category': 'refactoring',
            'message': 'Consider breaking down into smaller functions',
            'priority': 'medium'
        })
    
    # Check for code duplication
    line_counts = {}
    for line in lines:
        stripped = line.strip()
        if len(stripped) > 10:
            line_counts[stripped] = line_counts.get(stripped, 0) + 1
    
    duplicates = [line for line, count in line_counts.items() if count > 2]
    if duplicates:
        suggestions.append({
            'category': 'duplication',
            'message': 'Code duplication detected - consider extracting to function',
            'priority': 'medium'
        })
    
    return {
        'suggestions': suggestions,
        'score': max(0, 100 - len(suggestions) * 15)
    }


def calculate_confidence_score(code: str, language: str, target_language: str) -> int:
    """Calculate conversion confidence score."""
    score = 100
    
    # Reduce score for complex code
    complexity = analyze_complexity(code, language)
    if complexity['complexity_score'] > 20:
        score -= 20
    
    # Reduce score for language-specific features
    language_specific = {
        'python': ['lambda', 'list comprehension', 'decorator'],
        'javascript': ['async/await', 'promise', 'closure'],
        'golang': ['goroutine', 'channel', 'defer'],
        'rust': ['lifetime', 'borrow', 'trait']
    }
    
    for feature in language_specific.get(language, []):
        if feature.replace(' ', '_') in code.lower():
            score -= 10
    
    # Reduce score for very different language paradigms
    paradigm_distance = {
        ('python', 'c'): 30,
        ('javascript', 'rust'): 25,
        ('python', 'java'): 15,
    }
    
    distance = paradigm_distance.get((language, target_language), 0)
    score -= distance
    
    return max(50, min(100, score))
