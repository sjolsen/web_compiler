import sys
import re
import typing
from typing import List
from xml.etree import ElementTree as ET

import more_itertools

from web_compiler.backend import linker
from web_compiler.frontend import document
from web_compiler.frontend import nav


def MapOptional(f, x):
  if x is None:
    return None
  return f(x)


class ParseError(Exception):
  pass


class Parser(object):

  def match(self, part):
    pass

  def parse(self, part):
    return part

  def __call__(self, part):
    self.match(part)
    return self.parse(part)


class SimpleParser(Parser):

  @classmethod
  def Matching(cls, match):
    def decorate(parse):
      return cls(match, parse)
    return decorate

  def __init__(self, match, parse):
    super().__init__()
    self._match = match
    self._parse = parse

  def match(self, part):
    self._match(part)

  def parse(self, part):
    return self._parse(part)


class OneOf(Parser):

  def __init__(self, *parsers):
    super().__init__()
    self._parsers = parsers
    self._matches = {}

  def _show_errors(self, errors):
    return ''.join('\n  ' + str(e) for e in errors)

  def match(self, part):
    errors = []
    for p in self._parsers:
      try:
        p.match(part)
        self._matches[part] = p
        return
      except ParseError as e:
        errors.append((p, e))
        continue
    raise ParseError(f'No parsers matched on {part}: {self._show_errors(errors)}')

  def parse(self, part):
    return self._matches[part].parse(part)


class XmlContentIterator(object):

  @classmethod
  def _text_and_children(cls, node):
    result = []
    if node.text is not None:
      result.append(node.text)
    for child in node:
      result.append(child)
      if child.tail is not None:
        result.append(child.tail)
    return result

  def __init__(self, node, preserve_whitespace):
    self._iter = iter(self._text_and_children(node))
    self._preserve_whitespace = preserve_whitespace

  def __iter__(self):
    return self

  def __next__(self):
    while True:
      part = next(self._iter)
      if isinstance(part, typing.Text):
        if not self._preserve_whitespace:
          part = part.strip()
        if part:
          return part
        else:
          continue
      elif isinstance(part, ET.Element):
        return part
      else:
        raise ParseError(f'Unrecognized part: {part} of type {type(part)}')


class ParseContext(object):

  def __init__(self, node, preserve_whitespace=False):
    self._node = node
    self._iter = more_itertools.peekable(
      XmlContentIterator(node, preserve_whitespace))

  def __enter__(self):
    return self

  def __exit__(self, *args):
    try:
      part = self._iter.peek()
      raise ParseError(f'Incomplete iteration over node {self._node} at "{part}"')
    except StopIteration:
      pass

  def Expect(self, parser):
    try:
      part = next(self._iter)
    except StopIteration:
      raise ParseError('Unexpected end of content')
    return parser(part)

  def ExpectRest(self, parser):
    result = []
    for part in self._iter:
      result.append(parser(part))
    return result

  def Optional(self, parser):
    try:
      result = parser(self._iter.peek())
      next(self._iter)
      return result
    except (ParseError, StopIteration):
      return None


Any = Parser()


class Node(Parser):

  def __init__(self, match_tag):
    super().__init__()
    self._match_tag = match_tag

  def match(self, part):
    if not isinstance(part, ET.Element):
      raise ParseError(f'Expected node but got {part} of type {type(part)}')
    if not self._match_tag(part.tag):
      raise ParseError(f'Got node {part} with unexpected tag {part.tag}')


class TextParser(Parser):

  def match(self, part):
    if not isinstance(part, typing.Text):
      raise ParseError(f'Expected text but got {part} of type {type(part)}')

Text = TextParser()


def BlogTag(name):
  def match_tag(tag):
    return tag == '{http://sj-olsen.com/blog}' + name
  return match_tag


def HTMLTag(tag):
  return tag.startswith('{http://www.w3.org/1999/xhtml}')


@SimpleParser.Matching(Node(BlogTag('document')))
def ParseDocument(node):
  with ParseContext(node) as i:
    title = i.Expect(Node(BlogTag('title')))
    subtitle = i.Expect(Node(BlogTag('subtitle')))
    copyright = i.Expect(Node(BlogTag('copyright')))
    sections = i.ExpectRest(Node(BlogTag('section')))
  return document.Document(
    title=ParseMixedContent(title),
    subtitle=ParseMixedContent(subtitle),
    copyright=ParseMixedContent(copyright),
    sections=list(map(ParseDocumentSection, sections)))


@SimpleParser.Matching(Node(BlogTag('section')))
def ParseDocumentSection(node):
  with ParseContext(node) as i:
    title = i.Expect(Node(BlogTag('title')))
    body = i.Expect(Node(BlogTag('body')))
  return document.Section(
    title=ParseMixedContent(title),
    body=ParseMixedContent(body))


@SimpleParser.Matching(Any)
def ParseMixedContent(node):
  with ParseContext(node, preserve_whitespace=True) as i:
    return document.MixedContent(
      parts=i.ExpectRest(OneOf(Text, ParseHTML, ParseCode, ParseCodeBlock)))


@SimpleParser.Matching(Node(HTMLTag))
def ParseHTML(node):
  return document.HTMLNode(
    tag=re.match(r'{.*}(.*)', node.tag).group(1),
    attrs=node.attrib,
    content=ParseMixedContent(node))


@SimpleParser.Matching(Node(BlogTag('code')))
def ParseCode(node):
  return document.Code(
    content=ParseMixedContent(node))


@SimpleParser.Matching(Node(BlogTag('code-block')))
def ParseCodeBlock(node):
  with ParseContext(node) as i:
    header = i.Optional(Node(BlogTag('header')))
    body = i.Expect(Node(BlogTag('body')))
  return document.CodeBlock(
    header=MapOptional(ParseMixedContent, header),
    body=ParseMixedContent(body))


@SimpleParser.Matching(Node(BlogTag('nav')))
def ParseNav(node) -> List[nav.NavItem]:
  with ParseContext(node) as i:
    items = i.ExpectRest(Node(BlogTag('nav-item')))
  return [ParseNavItem(item) for item in items]


@SimpleParser.Matching(Node(BlogTag('nav-item')))
def ParseNavItem(node) -> nav.NavItem:
  with ParseContext(node) as i:
    ref = linker.Reference(node.attrib['href'])
    icon = linker.Reference(node.attrib['icon'])
    text = ''.join(i.ExpectRest(Text))
  return nav.NavItem(text=text, ref=ref, icon=icon)
