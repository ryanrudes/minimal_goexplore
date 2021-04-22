from pympler.asizeof import asizeof
from textwrap import wrap
import cv2

units = ["B", "KB", "MB", "GB", "TB", "PB"]

def cellfn(frame):
    cell = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    cell = cv2.resize(cell, (11, 8), interpolation = cv2.INTER_AREA)
    cell = cell // 32
    return cell

def hashfn(cell):
    return hash(cell.data.tobytes())

def prettysize(obj, delimiter=' ', separator=True):
    size = asizeof(obj)
    size = str(size)
    pad = len(size) % 3
    if pad:
        size = size.rjust(len(size) + 3 - pad)
    size = wrap(size, 3)
    text = []
    for value, unit in zip(size, reversed(units[:len(size)])):
        text.append(value.lstrip() + ' ' * int(separator) + unit)
    return delimiter.join(text)
