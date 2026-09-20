# Frame-Extractor
Here's a clean description you can use as a README section or as a module docstring for this script:

---

## Frame Extractor for DIC Video Analysis

A Python utility for extracting still frames from high-resolution video (e.g. 4K tensile/compression test footage) for use in Digital Image Correlation (DIC) software such as Ncorr.

### What it does

Given a video file, this script:
- Extracts frames within an optional time range (`start_time` to `end_time`), rather than requiring the full video.
- Samples at a configurable interval (`frame_interval`) instead of saving every frame — e.g. saving 1 out of every 30 frames from a 30fps video yields 1 frame per second, keeping DIC datasets manageable in size.
- Converts frames to grayscale by default (standard input format for most DIC software) and saves them as lossless PNGs with adjustable compression.
- Saves frames with sequential, zero-padded numeric filenames (e.g. `00001.png`, `00002.png`) so they sort correctly in any file browser or analysis pipeline.
- Automatically exports a companion CSV (`frame_timestamp_mapping.csv`) mapping every saved frame to its exact source-video timestamp — critical for later synchronizing DIC displacement/strain data against external time-series data (e.g. load-cell force readings) from a testing machine.

### Why

Digital Image Correlation software correlates the speckle pattern across a sequence of images to compute displacement and strain fields over the course of a mechanical test. This script bridges the gap between raw video footage from a test camera and the individual, correctly formatted image sequence that DIC tools expect, while preserving the precise timing information needed to later cross-reference results against force/load data collected by separate equipment.

### Requirements

```
pip install opencv-python
```

### Usage

Edit the parameters in the `if __name__ == "__main__":` block at the bottom of the script:

```python
video_path = r"path\to\your\video.mp4"
output_dir = r"path\to\output\folder"
frame_interval = 30      # save 1 out of every 30 frames
start_time = "00:02"     # MM:SS, HH:MM:SS, or seconds
end_time = "02:48"
```

Then run:
```
python frame_extractor.py
```

Frames and `frame_timestamp_mapping.csv` will be written to `output_dir`.

### Output

| File | Description |
|---|---|
| `00001.png`, `00002.png`, ... | Extracted, grayscale, sequentially numbered frames |
| `frame_timestamp_mapping.csv` | Columns: `frame_number`, `timestamp_seconds`, `timestamp_mm_ss`, `filename` |

---

If you're also uploading `sync_force_to_frames.py` and `align_force_to_frames.py` as part of the same repo/pipeline, let me know and I can write matching descriptions for those too (and possibly a top-level README tying all three together as one workflow) — but I'll need to see their final, working contents first since they've gone through several edits.
