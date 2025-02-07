#!/usr/bin/env python3
import pytest
import sys
import os
from pathlib import Path
import argparse

def run_test_stage(stage_config):
    """Run a single test stage and return its result."""
    print(f"\n{'='*20}")
    print(f"Running {stage_config['name']}")
    print(f"{'='*20}\n")
    
    # Build pytest arguments
    pytest_args = [
        stage_config["path"],
        "-v",
        "--tb=short"
    ]
    
    # Add specific configuration for E2E tests
    if stage_config["name"] == "e2e":
        pytest_args.extend([
            "-c", "tests/test_e2e/pytest.ini",  # Use E2E specific config
            "--base-url=http://localhost:8000"
        ])
    
    result = pytest.main(pytest_args)
    
    if result != 0:
        print(f"\n❌ {stage_config['name']} failed!")
        return False
    else:
        print(f"\n✅ {stage_config['name']} passed!")
        return True

def run_tests(stage=None):
    """
    Run tests with optional stage selection.
    
    Args:
        stage: Optional stage to run ('unit', 'integration', 'e2e', or None for all)
    """
    # Get the project root directory
    root_dir = Path(__file__).parent.parent
    
    # Ensure we're in the project root
    os.chdir(root_dir)
    
    # Create necessary directories
    os.makedirs("data/sample_images", exist_ok=True)
    os.makedirs("data/audio", exist_ok=True)
    
    # Define test stages and their configurations
    test_stages = {
        "unit": {
            "name": "Unit Tests",
            "path": "tests/test_services",
        },
        "integration": {
            "name": "API Integration Tests",
            "path": "tests/test_api",
        },
        "e2e": {
            "name": "End-to-End Tests",
            "path": "tests/test_e2e",
        }
    }
    
    if stage:
        if stage not in test_stages:
            print(f"Error: Unknown test stage '{stage}'")
            print(f"Available stages: {', '.join(test_stages.keys())}")
            sys.exit(1)
        
        # Run single stage
        success = run_test_stage(test_stages[stage])
        sys.exit(0 if success else 1)
    
    # Run all stages in order
    failed = False
    for stage_name in ["unit", "integration", "e2e"]:
        stage_success = run_test_stage(test_stages[stage_name])
        if not stage_success:
            failed = True
            break  # Stop on first failure
    
    # Exit with appropriate status code
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Visual Storyteller tests")
    parser.add_argument("--stage", choices=["unit", "integration", "e2e"],
                      help="Run specific test stage (unit, integration, or e2e)")
    args = parser.parse_args()
    
    run_tests(args.stage)