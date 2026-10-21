"""Stitch viewport screenshots of a scroll-driven page into one tall image.

Usage:
    python3 stitch_frames.py <output.jpeg> <frame1> <frame2> ...

Frames are stacked in the given order with a 4px dark divider, so it stays
visible that the result is a sequence of screens rather than one full-page
screenshot. Requires Pillow.
"""
import sys

try:
    from PIL import Image
except ImportError:
    print("Pillow is required: python3 -m pip install Pillow", file=sys.stderr)
    sys.exit(1)

DIVIDER = 4
DIVIDER_COLOR = (30, 41, 59)


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    out_path, frame_paths = argv[1], argv[2:]
    frames = [Image.open(path).convert("RGB") for path in frame_paths]
    width = max(frame.width for frame in frames)
    height = sum(frame.height for frame in frames) + DIVIDER * (len(frames) - 1)
    canvas = Image.new("RGB", (width, height), DIVIDER_COLOR)
    y = 0
    for frame in frames:
        canvas.paste(frame, (0, y))
        y += frame.height + DIVIDER
    canvas.save(out_path, quality=72)
    print(f"{out_path} {width}x{height} from {len(frames)} frames")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
