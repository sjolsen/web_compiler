from typing import NamedTuple

from web_compiler.backend import linker
from web_compiler.frontend import document


class NavItem(NamedTuple):
  text: document.MixedContent
  ref: linker.Reference
  icon: linker.Reference
