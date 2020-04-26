from typing import Dict, List, NamedTuple, Set, Text, Union

from web_compiler.backend import linker


class MixedContent(NamedTuple):
  parts: List['Fragment']


class HTMLNode(NamedTuple):
  tag: Text
  attrs: Dict[Text, Union[Text, linker.Reference]]
  content: MixedContent


Fragment = Union[Text, MixedContent, HTMLNode, linker.Reference]


class PageResource(linker.Resource):

  def __init__(self, fragment: Fragment):
    super().__init__()
    self._fragment = fragment

  def get_references(self) -> Set[linker.Reference]:
    refs = set()
    frontier = [self._fragment]
    while frontier:
      new_frontier = []
      for item in frontier:
        if isinstance(item, str):
          pass
        elif isinstance(item, MixedContent):
          new_frontier.extend(item.parts)
        elif isinstance(item, HTMLNode):
          new_frontier.extend(item.attrs.values())
          new_frontier.append(item.content)
        elif isinstance(item, linker.Reference):
          refs.add(item)
        else:
          raise TypeError(item)
      frontier = new_frontier
    return refs

  def _render_fragment(self, item: Fragment,
                       link: linker.Linker) -> Text:
    if isinstance(item, str):
      return item
    elif isinstance(item, MixedContent):
      # TODO: Indent HTML tags excluding pre?
      return ''.join(self._render_fragment(p, link) for p in item.parts)
    elif isinstance(item, HTMLNode):
      parts = [item.tag]
      for key, value in item.attrs.items():
        value = self._render_fragment(value, link)
        parts.append(f'{key}="{value}"')
      opentag = ' '.join(parts)
      content = self._render_fragment(item.content, link)
      return f'<{opentag}>{content}</{item.tag}>'
    elif isinstance(item, linker.Reference):
      return f'/{link.resolve(item)}'
    else:
      raise TypeError(item)

  def populate_fs(self, path: str, link: linker.Linker):
    with open(path, 'wt') as f:
      f.write(self._render_fragment(self._fragment, link))
