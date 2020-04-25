from typing import Dict, List, NamedTuple, Optional, Text, Union


class MixedContent(NamedTuple):
  parts: List[Union[Text, 'MixedContent', 'HTMLNode', 'Code', 'CodeBlock']]


class Document(NamedTuple):
  title: MixedContent
  subtitle: MixedContent
  copyright: MixedContent
  sections: List['Section']


class Section(NamedTuple):
  title: MixedContent
  body: MixedContent


class HTMLNode(NamedTuple):
  tag: Text
  attrs: Dict[Text, Text]
  content: MixedContent


class Code(NamedTuple):
  content: MixedContent


class CodeBlock(NamedTuple):
  header: Optional[MixedContent]
  body: MixedContent
