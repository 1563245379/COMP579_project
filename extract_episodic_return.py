"""
Scale episodic_return in TensorBoard event files by 1/200 and save as
TensorBoard event files (same format as originals).
"""
import os

import numpy as np
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from torch.utils.tensorboard import SummaryWriter


def load_run(run_dir: str) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Load all scalars from a TensorBoard run directory."""
    ea = EventAccumulator(run_dir, size_guidance={"scalars": 0})
    ea.Reload()
    out: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for tag in ea.Tags().get("scalars", []):
        events = ea.Scalars(tag)
        steps = np.asarray([e.step for e in events], dtype=np.int64)
        values = np.asarray([e.value for e in events], dtype=np.float64)
        out[tag] = (steps, values)
    return out


def process_runs_folder(runs_dir: str, output_dir: str, divisor: float = 200):
    """Read all runs, divide episodic_return by divisor, write new event files."""
    os.makedirs(output_dir, exist_ok=True)

    for run_name in sorted(os.listdir(runs_dir)):
        run_path = os.path.join(runs_dir, run_name)
        if not os.path.isdir(run_path):
            continue

        print(f"=== {run_name} ===")
        scalars = load_run(run_path)

        # Check for episodic_return tag
        er_tag = None
        for tag in scalars:
            if "episodic_return" in tag:
                er_tag = tag
                break

        if er_tag is None:
            print(f"  No episodic_return tag found. Tags: {list(scalars.keys())[:10]}")
            continue

        steps, values = scalars[er_tag]
        # Sort by step to avoid spurious connecting lines in plots
        order = np.argsort(steps)
        steps = steps[order]
        values = values[order]
        scaled = values / divisor

        out_run_dir = os.path.join(output_dir, run_name)
        writer = SummaryWriter(log_dir=out_run_dir)
        for step, val in zip(steps, scaled):
            writer.add_scalar(er_tag, float(val), int(step))
        writer.close()

        print(f"  {len(steps)} entries, first: {values[0]:.2f} -> {scaled[0]:.4f}, "
              f"last: {values[-1]:.2f} -> {scaled[-1]:.4f}")
        print(f"  Saved to: {out_run_dir}")


if __name__ == "__main__":
    process_runs_folder("runs", "runs_scaled", divisor=200)
    print("\nDone!")