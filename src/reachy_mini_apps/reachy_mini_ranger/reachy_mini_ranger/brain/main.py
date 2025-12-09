"""Brain entry point for Reachy Mini.

This module provides the main entry point for the LangGraph brain.
Can be run standalone for testing or imported as a module.

Usage:
    # Standalone test
    $ python -m reachy_mini_ranger.brain.main
    
    # Programmatic
    >>> from reachy_mini_ranger.brain.main import run_brain_demo
    >>> run_brain_demo()
"""

import sys
from datetime import datetime

from brain.graph import compile_graph, run_brain_cycle
from brain.models.state import create_initial_state


def run_brain_demo():
    """Run a demo brain cycle and print results.
    
    This is useful for testing the graph compilation and basic execution flow.
    """
    print("=" * 70)
    print("Reachy Mini LangGraph Brain - Demo")
    print("=" * 70)
    print()
    
    # Create initial state
    print("📊 Creating initial state...")
    initial_state = create_initial_state()
    print(f"   Mode: {initial_state.metadata.mode.value}")
    print(f"   Emotion: valence={initial_state.emotion.valence}, arousal={initial_state.emotion.arousal}")
    print(f"   Logs: {len(initial_state.metadata.logs)} entries")
    print()
    
    # Compile graph
    print("🔧 Compiling LangGraph...")
    try:
        app = compile_graph()
        print("   ✓ Graph compiled successfully")
    except Exception as e:
        print(f"   ✗ Compilation failed: {e}")
        return False
    print()
    
    # Run brain cycle
    print("🧠 Running brain cycle...")
    print("   START → Perception → Cognition → Skills → Execution → END")
    try:
        result_state = app.invoke(initial_state)
        print("   ✓ Cycle completed successfully")
    except Exception as e:
        print(f"   ✗ Execution failed: {e}")
        return False
    print()
    
    # Display results
    print("📈 Results:")
    print(f"   Logs: {len(result_state.metadata.logs)} entries")
    print("   Log entries:")
    for log in result_state.metadata.logs:
        print(f"     - {log}")
    print()
    
    print(f"   Timestamp: {result_state.metadata.timestamp.isoformat()}")
    print(f"   Mode: {result_state.metadata.mode.value}")
    print()
    
    # Validate execution
    expected_logs = ["Perception node executed", "Cognition node executed", 
                     "Skill node executed", "Execution node executed"]
    success = all(any(expected in log for log in result_state.metadata.logs) 
                  for expected in expected_logs)
    
    if success:
        print("✅ All nodes executed successfully!")
        print("   Graph orchestration is working correctly.")
    else:
        print("⚠️  Some nodes may not have executed")
        print(f"   Expected: {expected_logs}")
        print(f"   Got: {[log.split(': ')[1] if ': ' in log else log for log in result_state.metadata.logs]}")
    
    print()
    print("=" * 70)
    
    return success


def main():
    """Main entry point for standalone execution."""
    try:
        success = run_brain_demo()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
