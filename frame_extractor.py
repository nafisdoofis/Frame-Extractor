import cv2
import os
import csv

def time_to_seconds(t):
    """Convert 'MM:SS' or 'HH:MM:SS' string to seconds. Also accepts a plain number."""
    if isinstance(t, (int, float)):
        return float(t)
    parts = [float(p) for p in t.split(":")]
    if len(parts) == 2:
        m, s = parts
        return m * 60 + s
    elif len(parts) == 3:
        h, m, s = parts
        return h * 3600 + m * 60 + s
    else:
        raise ValueError(f"Unrecognized time format: {t}")


def seconds_to_mmss(seconds):
    """Convert seconds (float) to 'MM:SS.ss' string."""
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m:02d}:{s:05.2f}"


def extract_frames(video_path, output_dir, image_format="png", start_index=1,
                    zero_pad=None, grayscale=True, frame_interval=1,
                    png_compression=3, start_time=None, end_time=None,
                    export_csv=True, csv_path=None):
    """
    Extract frames from a video within an optional time range, saving 1 out of
    every `frame_interval` frames read. Also exports a CSV mapping each saved
    frame number to its exact video timestamp.

    Parameters:
        video_path (str): Path to the input video file.
        output_dir (str): Directory where extracted frames (and CSV) are saved.
        image_format (str): 'png' (lossless, recommended for DIC) or 'jpg'.
        start_index (int): Number to start labeling saved frames from (default 1).
        zero_pad (int or None): Zero-pad filenames to this width, e.g. 5 -> 00001.png.
        grayscale (bool): Convert frames to grayscale before saving.
        frame_interval (int): Save 1 out of every N frames read within the range.
        png_compression (int): 0 (none) - 9 (max). Lossless regardless of level.
        start_time / end_time: 'MM:SS', 'HH:MM:SS', or seconds. None = full video.
        export_csv (bool): If True, writes a CSV with frame_number, timestamp_seconds,
                            timestamp_mm_ss for every frame actually saved.
        csv_path (str or None): Path for the CSV. Defaults to
                                 '<output_dir>/frame_timestamp_mapping.csv' if None.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps else 0

    start_sec = time_to_seconds(start_time) if start_time is not None else 0.0
    end_sec = time_to_seconds(end_time) if end_time is not None else duration

    start_frame = int(round(start_sec * fps))
    end_frame = int(round(end_sec * fps))

    print(f"Video: {video_path}")
    print(f"Resolution: {width}x{height}, FPS: {fps:.2f}, Total frames (reported): {total_frames}, Duration: {duration:.1f}s")
    print(f"Extracting time range: {start_sec:.2f}s -> {end_sec:.2f}s  (frame {start_frame} -> {end_frame})")
    print(f"Saving 1 out of every {frame_interval} frames within that range")
    print(f"Grayscale: {grayscale}, Compression: {png_compression}")
    print(f"Saving frames to: {output_dir}\n")

    # Jump straight to the start frame instead of reading through everything before it
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    read_count = start_frame
    saved_count = start_index
    saved_total = 0

    # Collects (frame_number, timestamp_seconds, filename) for every frame actually written
    csv_rows = []

    while True:
        if read_count > end_frame:
            break

        ret, frame = cap.read()
        if not ret:
            break  # end of video reached early

        if (read_count - start_frame) % frame_interval == 0:
            if grayscale:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if zero_pad:
                filename = f"{saved_count:0{zero_pad}d}.{image_format}"
            else:
                filename = f"{saved_count}.{image_format}"

            filepath = os.path.join(output_dir, filename)

            if image_format.lower() == "png":
                success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_PNG_COMPRESSION, png_compression])
            elif image_format.lower() in ("jpg", "jpeg"):
                success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
            else:
                success = cv2.imwrite(filepath, frame)

            if not success:
                print(f"  WARNING: failed to write {filepath}")
            else:
                saved_total += 1
                actual_time = read_count / fps
                csv_rows.append((saved_count, actual_time, filename))

                if saved_total % 100 == 0:
                    print(f"  ...saved {saved_total} frames")

            saved_count += 1

        read_count += 1

    cap.release()
    print(f"\nDone. Saved {saved_total} frames to '{output_dir}'.")

    # ---- Export the frame -> timestamp CSV ----
    if export_csv:
        if csv_path is None:
            csv_path = os.path.join(output_dir, "frame_timestamp_mapping.csv")

        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["frame_number", "timestamp_seconds", "timestamp_mm_ss", "filename"])
            for frame_number, t_sec, filename in csv_rows:
                writer.writerow([frame_number, f"{t_sec:.3f}", seconds_to_mmss(t_sec), filename])

        print(f"Saved frame-timestamp mapping CSV to: {csv_path}")

    return csv_rows


if __name__ == "__main__":
    # ---- EDIT THESE ----
    video_path = r"F:\DIC paper\0.25N (2).mp4"
    output_dir = r"F:\DIC paper\Tensile-S6\frames"
    image_format = "png"
    start_index = 1
    zero_pad = 5
    grayscale = True
    frame_interval = 30          # 1 out of every 30 frames -> 1 fps at 30fps video
    png_compression = 3
    start_time = "00:02"         # MM:SS, HH:MM:SS, or seconds
    end_time = "02:48"
    export_csv = True            # writes frame_timestamp_mapping.csv into output_dir
    csv_path = None              # or set a custom path, e.g. r"F:\DIC paper\mapping.csv"
    # --------------------

    extract_frames(video_path, output_dir, image_format, start_index,
                    zero_pad, grayscale, frame_interval, png_compression,
                    start_time, end_time, export_csv, csv_path)
