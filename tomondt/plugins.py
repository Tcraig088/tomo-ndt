import sys

from .domain import procedures


print("Loading plugins...")

parent_pkg = sys.modules[__package__]
parent_pkg.procedures = procedures
sys.modules[f"{__package__}.procedures"] = procedures

