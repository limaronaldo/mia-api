"""
DEPRECATED: The graph is now created in the smart_system.py module.
This file is kept for backward compatibility with older imports but will be removed in a future version.
"""

from warnings import warn

from .smart_system import create_enhanced_mbras_system

warn(
    "The `chat_app` from this module is deprecated. "
    "Please use `create_enhanced_mbras_system()` from `smart_system.py` instead.",
    DeprecationWarning,
    stacklevel=2,
)

chat_app = create_enhanced_mbras_system()
