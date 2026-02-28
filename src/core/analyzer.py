"""
Code Analyzer Module
Analyzes code structure, complexity, and patterns
"""

import ast
import json
import requests
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

from utils.config import Config
from utils.logger import setup_logger


@dataclass
class AnalysisResult:
    """Result of code analysis"""
    file_path: str
    complexity_score: float
    lines_of_code: int
    issues_found: List[Dict[str, Any]]
    patterns_detected: List[Dict[str, Any]]
    dependencies: List[str]


class CodeAnalyzer:
    """Analyzes code files and directories"""
    
    def __init__(self, config: Config):
        self.config = config
        self.api_key = config.iflow_api_key
        self.api_url = "https://apis.iflow.cn/v1/chat/completions"
        self.logger = setup_logger()
    
    def analyze_directory(self, directory: str) -> Dict[str, Any]:
        """Analyze all files in a directory"""
        self.logger.info(f"Analyzing directory: {directory}")
        
        dir_path = Path(directory)
        results = []
        
        # Find all Python files
        python_files = list(dir_path.rglob("*.py"))
        
        # Filter out excluded paths
        excluded_patterns = self.config.get('analysis.exclude', [])
        python_files = [
            f for f in python_files 
            if not any(pattern in str(f) for pattern in excluded_patterns)
        ]
        
        for file_path in python_files:
            try:
                result = self.analyze_file(str(file_path))
                results.append(asdict(result))
            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {e}")
        
        # Generate summary with AI
        summary = self._generate_summary(results)
        
        return {
            'files_analyzed': len(results),
            'issues_found': sum(len(r['issues_found']) for r in results),
            'complexity_score': summary['avg_complexity'],
            'details': results,
            'summary': summary
        }
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze a single file"""
        self.logger.info(f"Analyzing file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Calculate basic metrics
        lines_of_code = len([line for line in code.split('\n') if line.strip()])
        
        # Parse AST
        try:
            tree = ast.parse(code)
            complexity = self._calculate_complexity(tree)
        except SyntaxError:
            complexity = 0
        
        # Analyze with AI
        ai_analysis = self._analyze_with_ai(code, file_path)
        
        return AnalysisResult(
            file_path=file_path,
            complexity_score=complexity,
            lines_of_code=lines_of_code,
            issues_found=ai_analysis.get('issues', []),
            patterns_detected=ai_analysis.get('patterns', []),
            dependencies=ai_analysis.get('dependencies', [])
        )
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return float(complexity)
    
    def _analyze_with_ai(self, code: str, file_path: str) -> Dict[str, Any]:
        """Use iFlow AI to analyze code"""
        prompt = f"""Analyze the following Python code file: {file_path}

Code:
```python
{code}
```

Provide analysis in JSON format with these fields:
- issues: list of potential issues (each with: severity, message, line_number)
- patterns: list of design patterns detected (each with: pattern_name, description)
- dependencies: list of external dependencies identified

Respond with only the JSON, no other text."""
        
        try:
            payload = {
                "model": "tstars2.0",
                "messages": [
                    {"role": "system", "content": "You are a code analysis expert. Analyze code and return results in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1500,
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
            self.logger.error(f"AI analysis failed: {e}")
            return {'issues': [], 'patterns': [], 'dependencies': []}
    
    def _generate_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate summary of all analysis results"""
        if not results:
            return {'avg_complexity': 0, 'total_lines': 0, 'issue_types': {}}
        
        avg_complexity = sum(r['complexity_score'] for r in results) / len(results)
        total_lines = sum(r['lines_of_code'] for r in results)
        
        # Count issue types
        issue_types = {}
        for result in results:
            for issue in result['issues_found']:
                severity = issue.get('severity', 'unknown')
                issue_types[severity] = issue_types.get(severity, 0) + 1
        
        return {
            'avg_complexity': round(avg_complexity, 2),
            'total_lines': total_lines,
            'issue_types': issue_types
        }