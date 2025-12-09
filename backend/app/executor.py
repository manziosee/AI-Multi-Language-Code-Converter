"""Code execution utilities for playground feature."""
import subprocess
import tempfile
import os
from typing import Dict, Any


def execute_code(code: str, language: str, timeout: int = 5) -> Dict[str, Any]:
    """Execute code safely and return output."""
    
    try:
        if language == 'python':
            return execute_python(code, timeout)
        elif language in ['javascript', 'nodejs']:
            return execute_javascript(code, timeout)
        else:
            return {
                'success': False,
                'output': '',
                'error': f'Execution not supported for {language}'
            }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e)
        }


def execute_python(code: str, timeout: int) -> Dict[str, Any]:
    """Execute Python code."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['python3', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Execution timeout (5 seconds)'
        }
    finally:
        os.unlink(temp_file)


def execute_javascript(code: str, timeout: int) -> Dict[str, Any]:
    """Execute JavaScript code using Node.js."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['node', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Execution timeout (5 seconds)'
        }
    except FileNotFoundError:
        return {
            'success': False,
            'output': '',
            'error': 'Node.js not installed on server'
        }
    finally:
        os.unlink(temp_file)
