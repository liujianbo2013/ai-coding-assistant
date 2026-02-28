"""
GitHub API Wrapper
Handles GitHub API interactions
"""

import requests
from typing import Dict, List, Any, Optional
from utils.config import Config


class GitHubAPI:
    """Wrapper for GitHub API"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = 'https://api.github.com'
        self.token = config.github_token
        self.repository = config.github_repository
        
        if not self.token:
            raise ValueError("GitHub token is required")
    
    def _make_request(self, method: str, endpoint: str, 
                      data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to GitHub API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.request(
            method,
            url,
            headers=headers,
            json=data
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_pr(self, pr_number: int) -> Dict[str, Any]:
        """Get pull request details"""
        return self._make_request('GET', f'repos/{self.repository}/pulls/{pr_number}')
    
    def get_pr_files(self, pr_number: int) -> List[Dict[str, Any]]:
        """Get files changed in a pull request"""
        return self._make_request('GET', f'repos/{self.repository}/pulls/{pr_number}/files')
    
    def create_pr_comment(self, pr_number: int, body: str) -> Dict[str, Any]:
        """Create a comment on a pull request"""
        return self._make_request('POST', f'repos/{self.repository}/pulls/{pr_number}/comments', {'body': body})
    
    def create_issue_comment(self, issue_number: int, body: str) -> Dict[str, Any]:
        """Create a comment on an issue"""
        return self._make_request('POST', f'repos/{self.repository}/issues/{issue_number}/comments', {'body': body})
    
    def create_review_comment(self, pr_number: int, commit_id: str, 
                             path: str, line: int, body: str) -> Dict[str, Any]:
        """Create a review comment on a specific line"""
        data = {
            'commit_id': commit_id,
            'path': path,
            'line': line,
            'body': body
        }
        return self._make_request('POST', f'repos/{self.repository}/pulls/{pr_number}/comments', data)