from xml.etree import ElementInclude
from xml.etree import ElementTree as ET

from web_design.compiler.frontend import document
from web_design.compiler.frontend import parser


def LoadDocument(path: str) -> document.Document:
  tree = ET.parse(path)
  root = tree.getroot()
  ElementInclude.include(root)
  return parser.ParseDocument(root)
