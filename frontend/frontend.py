from typing import Dict
from xml.etree import ElementInclude
from xml.etree import ElementTree as ET

from web_compiler.frontend import document
from web_compiler.frontend import parser


class Loader(object):

  def __init__(self, path_map: Dict[str, str]):
    super().__init__()
    self._path_map = path_map

  def _loader(self, href, parse, encoding=None):
    return ElementInclude.default_loader(self._path_map[href], parse, encoding)

  def LoadDocument(self, path: str) -> document.Document:
    tree = ET.parse(path)
    root = tree.getroot()
    ElementInclude.include(root, self._loader)
    return parser.ParseDocument(root)
