import sys

from .domain import io


print("Loading plugins...")

parent_pkg = sys.modules[__package__]
parent_pkg.procedures = io
sys.modules[f"{__package__}.io"] = io   

