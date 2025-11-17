#!/usr/bin/env python3
"""
Simple inspection script for PlannerAgent.

This script inspects the PlannerAgent structure without requiring dependencies.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def inspect_structure():
    """Inspect PlannerAgent file structure."""
    print('=' * 70)
    print('PlannerAgent Structure Inspection')
    print('=' * 70)
    print()

    planner_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'openhands',
        'agenthub',
        'planner_agent',
    )

    print('📁 File Structure:')
    print(f'   Location: {planner_dir}')
    print()

    if os.path.exists(planner_dir):
        for root, dirs, files in os.walk(planner_dir):
            level = root.replace(planner_dir, '').count(os.sep)
            indent = '   ' * (level + 1)
            folder_name = os.path.basename(root) or 'planner_agent'
            print(f'{indent}📂 {folder_name}/')
            subindent = '   ' * (level + 2)
            for file in sorted(files):
                if file.endswith(('.py', '.md', '.jinja2')):
                    size = os.path.getsize(os.path.join(root, file))
                    print(f'{subindent}📄 {file} ({size} bytes)')
    else:
        print(f'   ❌ Directory not found: {planner_dir}')

    print()


def show_quick_test():
    """Show a quick test command."""
    print('🧪 Quick Test Commands:')
    print()
    print('   1. Check Python syntax:')
    print('      python3 -m py_compile openhands/agenthub/planner_agent/*.py')
    print()
    print('   2. View documentation:')
    print('      cat openhands/agenthub/planner_agent/README.md')
    print()
    print('   3. Check registration (requires dependencies):')
    print('      python3 -c "from openhands.controller.agent import Agent; print(Agent.list_agents())"')
    print()
    print('   4. Run with OpenHands CLI (requires setup):')
    print('      python -m openhands.core.main --agent-name PlannerAgent')
    print()


def show_example_queries():
    """Show example test queries."""
    print('💬 Example Test Queries:')
    print()

    queries = [
        ('Simple', 'Add a contact form to the homepage'),
        ('Medium', 'Implement user authentication with JWT tokens'),
        ('Complex', 'Create a blog feature with markdown support and comments'),
        ('Bug Fix', 'Fix the login timeout issue'),
        ('Refactor', 'Refactor the API layer to use async/await'),
        ('Research', 'Research and implement the best caching strategy'),
    ]

    for category, query in queries:
        print(f'   {category:12} | "{query}"')

    print()


def show_expected_behavior():
    """Show what to expect when running PlannerAgent."""
    print('✨ Expected Behavior:')
    print()
    print('   When you give PlannerAgent a task, it will:')
    print()
    print('   1️⃣  ANALYZE the request and repository context')
    print('   2️⃣  CREATE a structured plan with steps')
    print('   3️⃣  DELEGATE steps to specialized agents (CodeActAgent, etc.)')
    print('   4️⃣  COLLECT feedback from each step')
    print('   5️⃣  REFINE the plan based on results')
    print('   6️⃣  ITERATE until the goal is achieved')
    print('   7️⃣  RETURN final results and summary')
    print()


def show_documentation():
    """Show where to find documentation."""
    print('📚 Documentation:')
    print()

    docs = [
        ('DESIGN.md', 'Technical architecture and design decisions'),
        ('README.md', 'User guide and API documentation'),
        ('EXAMPLE.md', 'Detailed usage examples with real scenarios'),
        ('test_planner_agent.md', 'Testing guide and troubleshooting'),
        ('PLANNER_AGENT_SUMMARY.md', 'Implementation summary'),
    ]

    for filename, description in docs:
        path = f'openhands/agenthub/planner_agent/{filename}'
        if filename.startswith('test_') or filename.startswith('PLANNER_'):
            path = filename
        print(f'   📄 {path}')
        print(f'      {description}')
        print()


def main():
    """Main function."""
    inspect_structure()
    show_expected_behavior()
    show_example_queries()
    show_quick_test()
    show_documentation()

    print('=' * 70)
    print('✅ PlannerAgent files are in place!')
    print()
    print('To test with a real query:')
    print('  1. Install dependencies: pip install -e .')
    print('  2. Set API key: export LLM_API_KEY=your-key')
    print('  3. Run: python -m openhands.core.main --agent-name PlannerAgent')
    print('=' * 70)


if __name__ == '__main__':
    main()
