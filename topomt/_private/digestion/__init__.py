# molsysmt/_private/digestion/__init__.py
from .._private.optional_import import optional_import

digest, register_pipeline = optional_import(
    "argdigest",
    ["digest", "register_pipeline"],
    warn=False,
)

