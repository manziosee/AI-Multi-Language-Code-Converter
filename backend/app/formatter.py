"""Code formatting utilities."""
import re


def format_code(code: str, language: str) -> str:
    """Auto-format code based on language conventions."""
    
    if language == 'python':
        return format_python(code)
    elif language in ['javascript', 'typescript', 'nodejs']:
        return format_javascript(code)
    elif language == 'java':
        return format_java(code)
    elif language == 'golang':
        return format_go(code)
    
    return code


def format_python(code: str) -> str:
    """Format Python code."""
    lines = code.split('\n')
    formatted = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted.append('')
            continue
        
        # Decrease indent for closing statements
        if stripped.startswith(('return', 'break', 'continue', 'pass')) or \
           (stripped and not stripped.endswith(':') and indent_level > 0 and 
            not stripped.startswith((' ', '\t'))):
            pass
        
        # Add proper indentation
        formatted.append('    ' * indent_level + stripped)
        
        # Increase indent after colons
        if stripped.endswith(':'):
            indent_level += 1
        
        # Decrease indent for dedent
        if stripped.startswith(('return', 'break', 'continue', 'pass')):
            indent_level = max(0, indent_level - 1)
    
    return '\n'.join(formatted)


def format_javascript(code: str) -> str:
    """Format JavaScript/TypeScript code."""
    lines = code.split('\n')
    formatted = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted.append('')
            continue
        
        # Decrease indent for closing braces
        if stripped.startswith('}'):
            indent_level = max(0, indent_level - 1)
        
        # Add proper indentation
        formatted.append('  ' * indent_level + stripped)
        
        # Increase indent after opening braces
        if stripped.endswith('{'):
            indent_level += 1
        
        # Handle single-line closing
        if stripped.startswith('}') and stripped.endswith('{'):
            indent_level += 1
    
    return '\n'.join(formatted)


def format_java(code: str) -> str:
    """Format Java code."""
    return format_javascript(code)  # Similar formatting rules


def format_go(code: str) -> str:
    """Format Go code."""
    lines = code.split('\n')
    formatted = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted.append('')
            continue
        
        # Decrease indent for closing braces
        if stripped.startswith('}'):
            indent_level = max(0, indent_level - 1)
        
        # Add proper indentation (tabs for Go)
        formatted.append('\t' * indent_level + stripped)
        
        # Increase indent after opening braces
        if stripped.endswith('{'):
            indent_level += 1
    
    return '\n'.join(formatted)
