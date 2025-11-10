
"""Tiny registry for tools."""

TOOLS = {}

def register(tool):
    TOOLS[tool.name] = tool

def get(name):
    return TOOLS.get(name)

# Import built-ins so they self-register.
from tools.detectors.face import TOOL as _face   # noqa: F401
from tools.transforms.blur import TOOL as _blur  # noqa: F401
# from tools.composites.blur_faces import TOOL as _bf  # noqa: F401

from tools.detectors.detect_keywords import TOOL as _dk   # noqa: F401
from tools.transforms.mute_segments import TOOL as _ms    # noqa: F401
from tools.composites.mute_keywords import TOOL as _mk  # noqa: F401