#!/usr/bin/env python3
"""
Script to analyze lines of code and create a cumulative progress chart
over the last 30 days.
"""

import os
import subprocess
import re
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple

# Directories and files to exclude from line count
EXCLUDE_DIRS = {
    'node_modules', 'venv', '__pycache__', '.git', 'target', 
    'dist', 'build', '.next', '.venv', 'env', '.env',
    'billions.db', 'billions.db.backup', '.idea', '.vscode'
}

EXCLUDE_FILES = {
    '.gitignore', '.env', '.DS_Store', 'package-lock.json',
    'yarn.lock', '.log', '.db', '.backup'
}

# File extensions to include (code files)
CODE_EXTENSIONS = {
    '.py', '.ts', '.tsx', '.js', '.jsx', '.rs', '.kt', '.java',
    '.sol', '.json', '.toml', '.yaml', '.yml', '.md', '.css',
    '.html', '.scss', '.sass', '.vue', '.go', '.c', '.cpp',
    '.h', '.hpp', '.sql', '.sh', '.bash', '.zsh'
}


def should_exclude_file(file_path: str) -> bool:
    """Check if a file should be excluded from line count."""
    path = Path(file_path)
    
    # Check if in exclude directory
    for part in path.parts:
        if part in EXCLUDE_DIRS or part.startswith('.'):
            # Allow some dot files like .gitignore in root
            if len(path.parts) > 1 and part.startswith('.'):
                return True
    
    # Check file extension
    if path.suffix not in CODE_EXTENSIONS and not path.suffix:
        return True
    
    # Check exclude files
    if path.name in EXCLUDE_FILES:
        return True
    
    # Exclude files in node_modules, venv, etc.
    if any(exclude in str(path) for exclude in EXCLUDE_DIRS):
        return True
    
    return False


def count_lines_in_file(file_path: str) -> int:
    """Count non-empty lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # Count non-empty lines (lines with at least one non-whitespace character)
            return sum(1 for line in lines if line.strip())
    except Exception:
        return 0


def count_lines_in_repo(repo_path: str) -> int:
    """Count total lines of code in repository."""
    total_lines = 0
    file_count = 0
    
    for root, dirs, files in os.walk(repo_path):
        # Filter out exclude directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_path)
            
            if should_exclude_file(rel_path):
                continue
            
            lines = count_lines_in_file(file_path)
            total_lines += lines
            file_count += 1
    
    return total_lines, file_count


def count_lines_at_commit(repo_path: str, commit_hash: str) -> int:
    """Count lines of code at a specific commit without checking it out."""
    total_lines = 0
    
    # Get list of all files in the commit
    cmd = ['git', 'ls-tree', '-r', '--name-only', commit_hash]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        files = result.stdout.strip().split('\n')
        files = [f for f in files if f.strip()]
        
        for file_path in files:
            # Filter files
            if should_exclude_file(file_path):
                continue
            
            # Get file content at this commit
            try:
                show_cmd = ['git', 'show', f'{commit_hash}:{file_path}']
                file_result = subprocess.run(
                    show_cmd,
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    errors='ignore',  # Skip binary files gracefully
                    check=True
                )
                
                # Count non-empty lines
                lines = file_result.stdout.split('\n')
                non_empty = sum(1 for line in lines if line.strip())
                total_lines += non_empty
            except (subprocess.CalledProcessError, UnicodeDecodeError):
                # File might be binary, deleted, or have encoding issues, skip
                continue
        
        return total_lines
    except subprocess.CalledProcessError:
        return 0


def get_first_commit_hash(repo_path: str) -> str:
    """Get the hash of the first commit in the repository (by date)."""
    # Get all commits with dates and find the one with the earliest date
    cmd = ['git', 'log', '--all', '--pretty=format:%H|%ad', '--date=short']
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        earliest_date = None
        earliest_commit = None
        
        for line in result.stdout.strip().split('\n'):
            if not line.strip() or '|' not in line:
                continue
            
            parts = line.split('|')
            if len(parts) >= 2:
                commit_hash = parts[0].strip()
                date_str = parts[1].strip()
                
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    if earliest_date is None or date < earliest_date:
                        earliest_date = date
                        earliest_commit = commit_hash
                except ValueError:
                    continue
        
        return earliest_commit
    except (subprocess.CalledProcessError, ValueError):
        pass
    
    return None


def get_first_commit_date(repo_path: str) -> datetime:
    """Get the date of the first commit in the repository."""
    # Get all commits and find the earliest date
    cmd = ['git', 'log', '--all', '--pretty=format:%ad', '--date=short']
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        dates = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    date = datetime.strptime(line.strip(), '%Y-%m-%d')
                    dates.append(date)
                except ValueError:
                    continue
        
        if dates:
            return min(dates)
    except (subprocess.CalledProcessError, ValueError) as e:
        pass
    
    # Fallback: use current date minus 1 year if we can't find first commit
    return datetime.now() - timedelta(days=365)


def get_all_commits_from_start(repo_path: str, start_date: datetime) -> List[Tuple[str, datetime]]:
    """Get all commits from a start date to now."""
    start_str = start_date.strftime('%Y-%m-%d')
    
    cmd = [
        'git', 'log',
        '--since', f'{start_str}',
        '--pretty=format:%H|%ad',
        '--date=iso'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|')
            if len(parts) == 2:
                commit_hash = parts[0]
                date_str = parts[1]
                try:
                    date = datetime.fromisoformat(date_str.replace(' +', '+').replace(' -', '-'))
                    commits.append((commit_hash, date))
                except ValueError:
                    continue
        
        return commits
    except subprocess.CalledProcessError:
        return []


def get_git_commits_for_date_range(repo_path: str, days: int = 30) -> List[Tuple[str, datetime]]:
    """Get all commits from the last N days."""
    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d')
    
    cmd = [
        'git', 'log',
        '--since', f'{cutoff_str}',
        '--pretty=format:%H|%ad',
        '--date=iso'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|')
            if len(parts) == 2:
                commit_hash = parts[0]
                date_str = parts[1]
                try:
                    date = datetime.fromisoformat(date_str.replace(' +', '+').replace(' -', '-'))
                    commits.append((commit_hash, date))
                except ValueError:
                    continue
        
        return commits
    except subprocess.CalledProcessError:
        return []


def get_commit_line_changes(repo_path: str, commit_hash: str) -> int:
    """Get net line change (added - deleted) for a commit, filtering to relevant files only."""
    # Use --numstat for precise line counts per file
    cmd = ['git', 'show', '--numstat', '--format=', commit_hash]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        total_insertions = 0
        total_deletions = 0
        
        # Parse numstat output: "insertions\tdeletions\tfilename"
        # Example: "95\t15\tfrontend/src/components/WalletButton.tsx"
        lines = result.stdout.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            # Split by tab
            parts = line.split('\t')
            if len(parts) < 3:
                continue
            
            try:
                insertions = int(parts[0]) if parts[0] != '-' else 0
                deletions = int(parts[1]) if parts[1] != '-' else 0
                file_path = parts[2].strip()
                
                # Filter: only count files that match our criteria
                if should_exclude_file(file_path):
                    continue
                
                total_insertions += insertions
                total_deletions += deletions
            except (ValueError, IndexError):
                continue
        
        return total_insertions - total_deletions
    except (subprocess.CalledProcessError, AttributeError, ValueError) as e:
        return 0


def get_initial_line_count(repo_path: str, first_commit_hash: str) -> int:
    """Get line count at the first commit by directly counting files in that commit."""
    if not first_commit_hash:
        return 0
    
    print(f"   Counting lines at first commit ({first_commit_hash[:8]}...)...")
    return count_lines_at_commit(repo_path, first_commit_hash)


def get_daily_line_counts_from_start(repo_path: str, start_date: datetime, first_commit_hash: str) -> Dict[str, int]:
    """Get line counts for each day from start date to now using git diff stats."""
    print("   Calculating initial line count at first commit...")
    initial_lines = get_initial_line_count(repo_path, first_commit_hash)
    print(f"   ✅ First commit had {initial_lines:,} lines")
    
    # Get all commits from start date
    commits = get_all_commits_from_start(repo_path, start_date)
    
    if not commits:
        # No commits, return just current count
        current_lines, _ = count_lines_in_repo(repo_path)
        today = datetime.now().strftime('%Y-%m-%d')
        return {today: current_lines}
    
    # Group commits by date and calculate cumulative changes
    daily_changes = defaultdict(int)
    for commit_hash, date in commits:
        date_key = date.strftime('%Y-%m-%d')
        change = get_commit_line_changes(repo_path, commit_hash)
        daily_changes[date_key] += change
    
    # Build cumulative counts for each day from start to now
    date_counts = {}
    current_date = start_date.date()
    end_date = datetime.now().date()
    cumulative_lines = initial_lines
    
    # Get all unique dates with commits
    all_dates = set([start_date.date()])
    for commit_hash, date in commits:
        all_dates.add(date.date())
    all_dates.add(end_date)
    
    # Sort dates
    sorted_dates = sorted(all_dates)
    
    for date in sorted_dates:
        date_key = date.strftime('%Y-%m-%d')
        
        # Add changes for this day
        if date_key in daily_changes:
            cumulative_lines += daily_changes[date_key]
        
        date_counts[date_key] = cumulative_lines
    
    return date_counts


def create_line_chart(date_counts: Dict[str, int], output_path: str, start_date: str = None):
    """Create a cumulative line chart of code progress in dark mode."""
    # Set dark mode style
    plt.style.use('dark_background')
    
    # Sort dates
    sorted_dates = sorted(date_counts.keys())
    sorted_counts = [date_counts[date] for date in sorted_dates]
    
    # Convert to datetime objects for better plotting
    dates = [datetime.strptime(d, '%Y-%m-%d') for d in sorted_dates]
    
    # Create figure with dark background
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    
    # Plot with bright colors for dark mode
    line_color = '#60a5fa'  # Bright blue
    fill_color = '#3b82f6'  # Medium blue
    
    ax.plot(dates, sorted_counts, marker='o', linewidth=2.5, markersize=4, 
            color=line_color, markerfacecolor=line_color, markeredgecolor='white', markeredgewidth=0.5)
    ax.fill_between(dates, sorted_counts, alpha=0.25, color=fill_color)
    
    # Title and labels with light text
    title_text = 'BILLION$ Ai Lines of Code Progression'
    if start_date:
        title_text += f'\nFrom {start_date} to Present'
    ax.set_title(title_text, fontsize=16, fontweight='bold', pad=20, color='white')
    ax.set_xlabel('Date', fontsize=12, fontweight='bold', color='#d1d5db')
    ax.set_ylabel('Total Lines of Code', fontsize=12, fontweight='bold', color='#d1d5db')
    
    # Grid with subtle dark lines
    ax.grid(True, alpha=0.2, linestyle='--', color='#4b5563')
    
    # Format x-axis dates
    ax.tick_params(colors='#d1d5db')
    plt.xticks(rotation=45, ha='right')
    plt.gcf().autofmt_xdate()
    
    # Add annotation for current total with dark mode styling
    if sorted_counts:
        current_total = sorted_counts[-1]
        ax.annotate(
            f'Current: {current_total:,} lines',
            xy=(dates[-1], current_total),
            xytext=(10, 10),
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#fbbf24', edgecolor='white', linewidth=1, alpha=0.9),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='white', lw=1.5),
            fontsize=11,
            fontweight='bold',
            color='#1e1e1e'
        )
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#1e1e1e')
    print(f"Chart saved to: {output_path}")


def main():
    repo_path = Path(__file__).parent.parent
    
    print("📊 Analyzing codebase statistics...")
    print(f"Repository: {repo_path}")
    
    # Count current lines
    print("\n1. Counting current lines of code...")
    current_lines, file_count = count_lines_in_repo(str(repo_path))
    print(f"   ✅ Total lines of code: {current_lines:,}")
    
    # Get first commit date and hash
    print("\n2. Finding repository start date...")
    first_commit_date = get_first_commit_date(str(repo_path))
    first_commit_hash = get_first_commit_hash(str(repo_path))
    print(f"   ✅ Repository started: {first_commit_date.strftime('%Y-%m-%d')}")
    if first_commit_hash:
        print(f"   ✅ First commit: {first_commit_hash[:12]}...")
    
    # Get daily line counts from start
    print("\n3. Analyzing git history from beginning...")
    date_counts = get_daily_line_counts_from_start(str(repo_path), first_commit_date, first_commit_hash)
    
    print(f"   ✅ Analyzed {len(date_counts)} days with commits")
    
    # Create chart
    print("\n4. Creating cumulative progress chart (dark mode)...")
    output_path = repo_path / 'codebase_progress_chart.png'
    create_line_chart(date_counts, str(output_path), first_commit_date.strftime('%Y-%m-%d'))
    
    # Print summary
    print("\n📈 Summary:")
    if date_counts:
        sorted_dates = sorted(date_counts.keys())
        first_date = sorted_dates[0]
        last_date = sorted_dates[-1]
        first_count = date_counts[first_date]
        last_count = date_counts[last_date]
        growth = last_count - first_count
        
        print(f"   Start ({first_date}): {first_count:,} lines")
        print(f"   End ({last_date}): {last_count:,} lines")
        print(f"   Growth: {growth:+,} lines ({growth/first_count*100:.1f}%)" if first_count > 0 else f"   Growth: {growth:+,} lines")
    
    print(f"\n✅ Complete! Chart saved to: {output_path}")


if __name__ == '__main__':
    main()

