#!/usr/bin/env python3
"""
AI Coding Assistant - Main Entry Point
GitHub Actions Workflow for automated code analysis, review, and optimization
"""

import argparse
import sys
import json
from pathlib import Path

from core.analyzer import CodeAnalyzer
from core.reviewer import CodeReviewer
from core.optimizer import CodeOptimizer
from core.documentor import Documentor
from utils.config import Config
from utils.logger import setup_logger


def main():
    """Main entry point for the AI Coding Assistant"""
    parser = argparse.ArgumentParser(
        description='AI Coding Assistant - Automated code analysis and review'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze code quality')
    analyze_parser.add_argument('--path', required=True, help='Path to analyze')
    analyze_parser.add_argument('--output', default='analysis-report.json', help='Output file')
    
    # Review command
    review_parser = subparsers.add_parser('review', help='Review code changes')
    review_parser.add_argument('--diff', required=True, help='PR diff file')
    review_parser.add_argument('--pr-number', type=int, required=True, help='PR number')
    review_parser.add_argument('--output', default='review-results.json', help='Output file')
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Optimize code')
    optimize_parser.add_argument('--path', required=True, help='Path to optimize')
    optimize_parser.add_argument('--output', default='optimization-report.json', help='Output file')
    optimize_parser.add_argument('--max-suggestions', type=int, default=5, help='Max suggestions')
    
    # Docs command
    docs_parser = subparsers.add_parser('docs', help='Generate documentation')
    docs_parser.add_argument('--path', default='src', help='Source path')
    docs_parser.add_argument('--output', default='docs/generated', help='Output directory')
    docs_parser.add_argument('--format', default='markdown', help='Output format')
    docs_parser.add_argument('--readme-only', action='store_true', help='Only update README')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Setup logger
    logger = setup_logger()
    logger.info(f"Starting AI Coding Assistant: {args.command}")
    
    # Load configuration
    config = Config()
    
    try:
        if args.command == 'analyze':
            analyzer = CodeAnalyzer(config)
            result = analyzer.analyze_directory(args.path)
            
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Analysis complete. Results saved to {output_path}")
            
        elif args.command == 'review':
            reviewer = CodeReviewer(config)
            
            with open(args.diff, 'r', encoding='utf-8') as f:
                diff_content = f.read()
            
            result = reviewer.review_diff(diff_content, args.pr_number)
            
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Review complete. Results saved to {output_path}")
            
        elif args.command == 'optimize':
            optimizer = CodeOptimizer(config)
            result = optimizer.optimize_code(args.path, args.max_suggestions)
            
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Optimization complete. Results saved to {output_path}")
            
        elif args.command == 'docs':
            documentor = Documentor(config)
            
            if args.readme_only:
                documentor.create_readme('.')
                logger.info("README updated")
            else:
                output_dir = Path(args.output)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                documentor.generate_docs(args.path, str(output_dir), args.format)
                logger.info(f"Documentation generated in {output_dir}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error executing command: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())