"""
Code Optimizer Module
Identifies and suggests code optimizations
"""

import json
import ast
import requests
from pathlib import Path
from typing import Dict, List, Any
from utils.config import Config
from utils.logger import setup_logger


class CodeOptimizer:
    """Optimizes code and provides suggestions"""
    
    def __init__(self, config: Config):
        self.config = config
        self.api_key = config.iflow_api_key
        self.api_url = "https://apis.iflow.cn/v1/chat/completions"
        self.logger = setup_logger()
    
    def optimize_code(self, path: str, max_suggestions: int = 5) -> Dict[str, Any]:
        """Optimize code in given path"""
        self.logger.info(f"Optimizing code in: {path}")
        
        path_obj = Path(path)
        suggestions = []
        
        if path_obj.is_file():
            suggestions = self._optimize_file(path_obj)
        else:
            # Optimize all Python files
            for file_path in path_obj.rglob("*.py"):
                file_suggestions = self._optimize_file(file_path)
                suggestions.extend(file_suggestions)
        
        # Limit suggestions
        suggestions = suggestions[:max_suggestions]
        
        return {
            'path': path,
            'total_suggestions': len(suggestions),
            'suggestions': suggestions
        }
    
    def _optimize_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Optimize a single file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Get AI suggestions
        ai_suggestions = self._analyze_with_ai(code, str(file_path))
        
        # Add static analysis suggestions
        static_suggestions = self._static_analysis(code, str(file_path))
        
        return ai_suggestions + static_suggestions
    
    def _analyze_with_ai(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Use iFlow AI to suggest optimizations"""
        prompt = f"""Analyze the following Python code for optimization opportunities: {file_path}

```python
{code}
```

Provide optimization suggestions in JSON format as a list, where each suggestion has:
- title: brief title of the optimization
- priority: high/medium/low
- description: what should be improved
- current_code: the code that needs optimization
- suggested_code: optimized version
- impact: expected performance improvement

Focus on:
1. Algorithm efficiency
2. Memory usage
3. Code duplication
4. Python best practices
5. Performance bottlenecks

Respond with only the JSON array, no other text."""
        
        try:
            payload = {
                "model": "tstars2.0",
                "messages": [
                    {"role": "system", "content": "You are a code optimization expert. Provide performance-focused suggestions in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            result_text = result['choices'][0]['message']['content'].strip()
            return json.loads(result_text)
            
        except Exception as e:
            self.logger.error(f"AI optimization analysis failed: {e}")
            return []
    
    def _static_analysis(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Perform static analysis for common issues"""
        suggestions = []
        
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return suggestions
        
        # Check for common patterns
        for node in ast.walk(tree):
            # Check for nested loops (potential O(n²) complexity)
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.For) and child != node:
                        suggestions.append({
                            'title': 'Nested loop detected',
                            'priority': 'medium',
                            'description': 'Nested loops can lead to O(n²) complexity. Consider using sets or dictionaries for lookups.',
                            'file': file_path,
                            'line': node.lineno,
                            'impact': 'May improve performance significantly'
                        })
                        break
        
        # Check for repeated string concatenation
        if code.count('+=') > 10 and 'str' in code:
            suggestions.append({
                'title': 'Repeated string concatenation',
                'priority': 'low',
                'description': 'Multiple string concatenations can be inefficient. Consider using join() or StringIO.',
                'file': file_path,
                'impact': 'Moderate performance improvement'
            })
        
        return suggestions