"""
Code Reviewer Module
Reviews code changes and provides suggestions
"""

import json
import requests
from typing import Dict, List, Any
from utils.config import Config
from utils.logger import setup_logger


class CodeReviewer:
    """Reviews code changes and provides feedback"""
    
    def __init__(self, config: Config):
        self.config = config
        self.api_key = config.iflow_api_key
        self.api_url = "https://apis.iflow.cn/v1/chat/completions"
        self.logger = setup_logger()
    
    def review_diff(self, diff: str, pr_number: int) -> Dict[str, Any]:
        """Review a PR diff"""
        self.logger.info(f"Reviewing PR #{pr_number}")
        
        # Analyze with AI
        review = self._analyze_with_ai(diff)
        
        # Calculate overall score
        overall_score = self._calculate_score(review)
        
        return {
            'pr_number': pr_number,
            'overall_score': overall_score,
            'summary': review.get('summary', ''),
            'issues': review.get('issues', []),
            'suggestions': review.get('suggestions', []),
            'comments': review.get('comments', [])
        }
    
    def _analyze_with_ai(self, diff: str) -> Dict[str, Any]:
        """Use iFlow AI to review code diff"""
        prompt = f"""Review the following code diff:

```
{diff}
```

Provide a comprehensive code review in JSON format with these fields:
- summary: brief overall assessment (2-3 sentences)
- issues: list of issues found (each with: severity [critical/medium/low], file, line, description)
- suggestions: list of improvement suggestions (each with: title, description, code_example)
- comments: list of inline comments (each with: path, line, body)

Focus on:
1. Code quality and best practices
2. Security vulnerabilities
3. Performance issues
4. Readability and maintainability
5. Potential bugs

Respond with only the JSON, no other text."""
        
        try:
            payload = {
                "model": "tstars2.0",
                "messages": [
                    {"role": "system", "content": "You are an expert code reviewer. Provide detailed, constructive feedback in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
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
            self.logger.error(f"AI review failed: {e}")
            return {
                'summary': 'Unable to perform AI review due to an error.',
                'issues': [],
                'suggestions': [],
                'comments': []
            }
    
    def _calculate_score(self, review: Dict[str, Any]) -> int:
        """Calculate overall score based on review results"""
        base_score = 10
        
        # Deduct points for issues
        critical_issues = len([i for i in review.get('issues', []) if i.get('severity') == 'critical'])
        medium_issues = len([i for i in review.get('issues', []) if i.get('severity') == 'medium'])
        low_issues = len([i for i in review.get('issues', []) if i.get('severity') == 'low'])
        
        score = base_score - (critical_issues * 2) - (medium_issues * 1) - (low_issues * 0.5)
        
        # Bonus for good practices
        if review.get('suggestions'):
            score += 1
        
        return max(1, min(10, int(score)))
    
    def check_security(self, code: str) -> List[Dict[str, Any]]:
        """Check for security issues"""
        # Common security patterns
        security_patterns = [
            ('SQL Injection', ['execute(', 'exec(', 'format(', '%s'], 'high'),
            ('XSS Vulnerability', ['innerHTML', 'document.write'], 'medium'),
            ('Hardcoded Password', ['password', 'secret', 'api_key'], 'high'),
            ('Insecure Random', ['random.random('], 'low'),
        ]
        
        issues = []
        for name, patterns, severity in security_patterns:
            for pattern in patterns:
                if pattern in code:
                    issues.append({
                        'type': name,
                        'severity': severity,
                        'pattern': pattern
                    })
        
        return issues