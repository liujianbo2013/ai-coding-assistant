"""
Documentor Module
Generates documentation from code
"""

import ast
import json
import requests
from pathlib import Path
from typing import Dict, List, Any
from utils.config import Config
from utils.logger import setup_logger


class Documentor:
    """Generates documentation from code"""
    
    def __init__(self, config: Config):
        self.config = config
        self.api_key = config.iflow_api_key
        self.api_url = "https://apis.iflow.cn/v1/chat/completions"
        self.logger = setup_logger()
    
    def generate_docs(self, path: str, output_dir: str, format: str = 'markdown'):
        """Generate documentation for code in path"""
        self.logger.info(f"Generating documentation for: {path}")
        
        path_obj = Path(path)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if path_obj.is_file():
            self._generate_file_docs(path_obj, output_path, format)
        else:
            # Generate docs for all Python files
            for file_path in path_obj.rglob("*.py"):
                rel_path = file_path.relative_to(path_obj)
                file_output_dir = output_path / rel_path.parent
                file_output_dir.mkdir(parents=True, exist_ok=True)
                self._generate_file_docs(file_path, file_output_dir, format)
    
    def _generate_file_docs(self, file_path: Path, output_dir: Path, format: str):
        """Generate documentation for a single file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError:
            self.logger.error(f"Cannot parse {file_path}")
            return
        
        # Extract module info
        module_doc = ast.get_docstring(tree)
        classes = self._extract_classes(tree)
        functions = self._extract_functions(tree)
        
        # Generate documentation with AI
        doc_content = self._generate_with_ai(
            file_path.name,
            code,
            module_doc,
            classes,
            functions
        )
        
        # Write documentation
        output_file = output_dir / f"{file_path.stem}.{format}"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        self.logger.info(f"Documentation generated: {output_file}")
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class information from AST"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            'name': item.name,
                            'docstring': ast.get_docstring(item),
                            'args': [arg.arg for arg in item.args.args]
                        })
                
                classes.append({
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'methods': methods
                })
        
        return classes
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function information from AST"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not isinstance(node.parent, ast.ClassDef):
                functions.append({
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'args': [arg.arg for arg in node.args.args]
                })
        
        return functions
    
    def _generate_with_ai(self, filename: str, code: str, module_doc: str,
                          classes: List[Dict], functions: List[Dict]) -> str:
        """Generate documentation using iFlow AI"""
        prompt = f"""Generate comprehensive Markdown documentation for this Python file: {filename}

Module Docstring: {module_doc or 'No module docstring'}

Classes: {json.dumps(classes, indent=2)}

Functions: {json.dumps(functions, indent=2)}

Code:
```python
{code[:2000]}
```

Generate documentation that includes:
1. Overview and purpose
2. Classes documentation (with methods)
3. Functions documentation
4. Usage examples
5. Notes and warnings

Use proper Markdown formatting with headers, code blocks, and tables where appropriate."""
        
        try:
            payload = {
                "model": "tstars2.0",
                "messages": [
                    {"role": "system", "content": "You are a technical documentation expert. Generate clear, comprehensive documentation in Markdown format."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 3000,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            self.logger.error(f"AI documentation generation failed: {e}")
            return f"# Documentation for {filename}\n\n*Documentation generation failed.*"
    
    def create_readme(self, project_path: str):
        """Update or create README.md"""
        self.logger.info("Updating README.md")
        
        project_path_obj = Path(project_path)
        readme_path = project_path_obj / 'README.md'
        
        # Gather project information
        python_files = list(project_path_obj.rglob("*.py"))
        
        # Generate README content
        readme_content = self._generate_readme_content(
            project_path_obj.name,
            python_files
        )
        
        # Write README
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _generate_readme_content(self, project_name: str, python_files: List[Path]) -> str:
        """Generate README content using iFlow AI"""
        prompt = f"""Generate a comprehensive README.md for a Python project named "{project_name}"

The project has {len(python_files)} Python files.

Include these sections:
1. Project title and badge
2. Brief description
3. Features
4. Installation instructions
5. Usage examples
6. Project structure
7. Contributing guidelines
8. License

Use professional README formatting with proper Markdown."""
        
        try:
            payload = {
                "model": "tstars2.0",
                "messages": [
                    {"role": "system", "content": "You are a README generation expert. Create professional, well-formatted README files in Markdown."},
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
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            self.logger.error(f"README generation failed: {e}")
            return f"# {project_name}\n\n*README generation failed.*"