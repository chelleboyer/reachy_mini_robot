#!/usr/bin/env python3
"""Hardware validation test for Phase 1B - Brain loop integration.

Tests the complete perception-cognition-action pipeline on actual hardware.
"""
import time
from reachy_mini import ReachyMini
from reachy_mini_ranger.brain.graph import compile_graph
from reachy_mini_ranger.brain.models.state import create_initial_state

def main():
    print("=== Phase 1B Hardware Validation ===\n")
    
    # Connect to robot
    print("1. Connecting to ReachyMini...")
    reachy_mini = ReachyMini()
    print(f"   ✓ Connected to robot at {reachy_mini._host}")
    
    # Initialize brain
    print("\n2. Initializing brain...")
    graph = compile_graph()
    state = create_initial_state()
    print("   ✓ Brain graph compiled")
    
    # Test camera
    print("\n3. Testing camera...")
    frame = reachy_mini.media.get_frame()
    if frame is not None:
        print(f"   ✓ Camera working: {frame.shape} frame captured")
    else:
        print("   ✗ Camera not available")
        return
    
    # Run brain cycles
    print("\n4. Running brain cycles...")
    cycle_times = []
    
    for i in range(10):
        start = time.time()
        state = graph.invoke(state)
        elapsed = time.time() - start
        cycle_times.append(elapsed)
        
        # Print status every cycle
        num_faces = len(state.sensors.vision.faces)
        num_humans = len(state.world_model.humans)
        fps = state.sensors.vision.fps
        head_cmd = state.actuator_commands.head
        
        print(f"   Cycle {i+1}: "
              f"{num_faces} faces, "
              f"{num_humans} humans, "
              f"vision FPS: {fps:.1f}, "
              f"head: ({head_cmd.yaw:.1f}°, {head_cmd.pitch:.1f}°, {head_cmd.roll:.1f}°), "
              f"cycle time: {elapsed*1000:.1f}ms")
    
    # Calculate stats
    avg_cycle_time = sum(cycle_times) / len(cycle_times)
    max_cycle_time = max(cycle_times)
    min_cycle_time = min(cycle_times)
    target_fps = 1.0 / avg_cycle_time
    
    print(f"\n5. Performance Summary:")
    print(f"   Average cycle time: {avg_cycle_time*1000:.1f}ms")
    print(f"   Min cycle time: {min_cycle_time*1000:.1f}ms")
    print(f"   Max cycle time: {max_cycle_time*1000:.1f}ms")
    print(f"   Target FPS: {target_fps:.1f} Hz")
    print(f"   Target met: {'✓ YES' if target_fps >= 10.0 else '✗ NO'} (target: 10 Hz)")
    
    # Check logs for any safety violations
    print(f"\n6. Safety Check:")
    safety_logs = [log for log in state.metadata.logs if "Safety" in log]
    if safety_logs:
        print(f"   Found {len(safety_logs)} safety events:")
        for log in safety_logs[-5:]:  # Last 5
            print(f"   - {log}")
    else:
        print("   ✓ No safety violations")
    
    print("\n=== Hardware Validation Complete ===")
    print(f"Status: {'✓ PASS' if target_fps >= 8.0 else '✗ FAIL'}")
    print(f"Camera: {'✓ Working' if frame is not None else '✗ Failed'}")
    print(f"Brain Loop: {'✓ Stable' if max_cycle_time < 0.150 else '⚠ Slow'}")

if __name__ == "__main__":
    main()
