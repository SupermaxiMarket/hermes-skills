#!/usr/bin/env python3
"""
Hermes Astros script - Perform competitor research and generate content ideas.
This script is designed to be run via the Hermes agent's execute_code tool.
"""
import json
import sys
from datetime import datetime, timedelta
import os

def main():
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Hermes Astros: Competitor research and content idea generation')
    parser.add_argument('--scan', action='store_true', help='Run a scan for trending topics')
    parser.add_argument('--view', action='store_true', help='View last results from memory')
    parser.add_argument('--keywords', nargs='+', default=['AI SEO', 'Claude Code', 'NotebookLM'], help='Keywords to monitor')
    parser.add_argument('--hours', type=int, default=24, help='Look back hours for recent content')
    args = parser.parse_args()

    # Import hermes_tools
    try:
        from hermes_tools import web_search, web_extract, memory
    except ImportError:
        print(json.dumps({"error": "hermes_tools not available. This script must run within Hermes agent."}))
        return 1

    if args.scan:
        all_results = []
        for keyword in args.keywords:
            try:
                # Search for recent content
                query = f"{keyword} latest trends 2024"
                search_results = web_search(query=query, limit=5)
                if search_results.get("status") == "success":
                    data = search_results.get("data", {})
                    web_results = data.get("web", [])
                    for result in web_results[:3]:  # Top 3 per keyword
                        all_results.append({
                            "keyword": keyword,
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "snippet": result.get("description", ""),
                            "timestamp": datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"Error searching for {keyword}: {e}", file=sys.stderr)

        # Store results in memory for later use
        memory_data = {
            "timestamp": datetime.now().isoformat(),
            "keywords": args.keywords,
            "results": all_results
        }
        # Save to a memory file
        memory_path = os.path.expanduser("~/.hermes/astros_last_scan.json")
        try:
            with open(memory_path, 'w') as f:
                json.dump(memory_data, f, indent=2)
            # Also store in Hermes memory for persistence across sessions
            memory(
                action="add",
                target="memory",
                content=f"Hermes Astros scan results: {json.dumps(memory_data, indent=2)}"
            )
        except Exception as e:
            print(f"Error saving memory: {e}", file=sys.stderr)

        # Output results
        print(json.dumps({
            "status": "scan_complete",
            "timestamp": datetime.now().isoformat(),
            "keywords": args.keywords,
            "results_count": len(all_results),
            "results": all_results
        }, indent=2))

    elif args.view:
        memory_path = os.path.expanduser("~/.hermes/astros_last_scan.json")
        if os.path.exists(memory_path):
            try:
                with open(memory_path, 'r') as f:
                    data = json.load(f)
                print(json.dumps({
                    "status": "success",
                    "data": data
                }, indent=2))
            except Exception as e:
                print(json.dumps({"error": f"Failed to read memory: {e}"}))
        else:
            print(json.dumps({"status": "no_data", "message": "No previous scan results found. Run --scan first."}))

    else:
        parser.print_help()

if __name__ == '__main__':
    sys.exit(main())