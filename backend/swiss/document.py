import datetime
import functools
import html
from typing import Any, Dict, Iterable, Iterator, NamedTuple, Optional, Sequence, Text

from absl import flags

from web_compiler.backend import linker
from web_compiler.backend import page
from web_compiler.frontend import document
from web_compiler.frontend import nav

flags.DEFINE_string('info_file', None, 'TODO')
flags.DEFINE_string('version_file', None, 'TODO')
flags.mark_flags_as_required(['info_file', 'version_file'])

FLAGS = flags.FLAGS


def intersperse(sep: Any, l: Iterable[Any]) -> Iterator[Any]:
  try:
    i = iter(l)
    yield next(i)
    for item in i:
      yield sep
      yield item
  except StopIteration:
    return


@functools.singledispatch
def Render(obj, **kwargs) -> page.Fragment:
  raise TypeError(f'No Render instance found for {type(obj)}')


@Render.register(Text)
def RenderText(text) -> page.Fragment:
  return page.MixedContent([html.escape(text, quote=False)])


@Render.register(document.MixedContent)
def RenderMixedContent(mc) -> page.Fragment:
  return page.MixedContent([Render(p) for p in mc.parts])


def H(tag: Text, attrs: Optional[Dict[Text, Text]] = None,
      content: Optional[page.MixedContent] = None) -> page.HTMLNode:
  return page.HTMLNode(tag=tag, attrs=attrs or {},
                       content=content or page.MixedContent([]))


def TitleBlock(title: page.Fragment, subtitle: page.Fragment) -> page.Fragment:
  return H('div', {'class': 'title-block'}, page.MixedContent([
    H('h1', {'class': 'title'}, title),
    H('hr', {'class': 'title-rule'}),
    H('h2', {'class': 'subtitle'}, subtitle),
  ]))


def Nav(items: Iterable[nav.NavItem]) -> page.Fragment:
  anchors = [
    H('a', {'class': 'nav-row', 'href': i.ref}, page.MixedContent([
      H('img', {'class': 'nav-icon', 'src': i.icon}),
      H('li', {}, page.MixedContent([i.text])),
    ]))
    for i in items
  ]
  spacer = H('div', {'class': 'nav-spacer'})
  return H('nav', {}, page.MixedContent([
    H('ul', {}, page.MixedContent(list(intersperse(spacer, anchors)))),
  ]))


def _ParseBazelInfo(filename: str) -> Dict[str, str]:
  result = dict()
  with open(filename, 'rt') as f:
    for line in f:
      line = line.strip()
      parts = line.split(' ', 1)
      if len(parts) == 2:
        result[parts[0]] = parts[1]
      else:
        result[parts[0]] = ''
  return result


def FooterBlock(copyright: page.Fragment) -> page.Fragment:
  # Get the build timestamp to embed in the footer
  version = _ParseBazelInfo(FLAGS.version_file)
  ts = datetime.datetime.utcfromtimestamp(int(version['BUILD_TIMESTAMP']))
  date = ts.strftime('%Y-%m-%d')
  # Get the git hash to embed in the footer
  info = _ParseBazelInfo(FLAGS.info_file)
  git_ref = info['STABLE_GIT_COMMIT']
  if git_ref.endswith('-dirty'):
    git_hash = git_ref[:-6]
  else:
    git_hash = git_ref
  # TODO: Use the same mechanism to get the git remote URL
  git_url = info['STABLE_GIT_URL'].format(git_hash=git_hash)
  return page.MixedContent([
    H('div', {'class': 'footer-left'}, page.MixedContent([
      f'Copyright © {datetime.datetime.now().year} ',
      copyright,
    ])),
    H('div', {'class': 'footer-right'}, page.MixedContent([
      f'Built {date} from ',
      H('a', {'class': 'footer-git', 'href': git_url}, git_ref),
    ])),
  ])


@Render.register(document.Document)
def RenderDocument(doc, *, nav_items: Sequence[nav.NavItem] = ()) -> page.Fragment:
  title = Render(doc.title)
  subtitle = Render(doc.subtitle)
  copyright = Render(doc.copyright)
  sections = page.MixedContent([Render(s) for s in doc.sections])
  style = linker.Reference('web_compiler/backend/swiss/style.css')

  head = H('head', {}, page.MixedContent([
    H('meta', {'charset': 'utf-8'}),
    H('title', {}, title),
    H('link', {'rel': 'stylesheet', 'href': style, 'type': 'text/css'}),
  ]))
  if nav_items:
    header = H('header', {},
      H('div', {'class': 'hcenter header-flexbox'}, page.MixedContent([
        TitleBlock(title, subtitle),
        H('div', {'class': 'header-vr title-rule'}),
        Nav(nav_items),
      ])))
  else:
    header = H('header', {},
      H('div', {'class': 'hcenter'}, TitleBlock(title, subtitle)))
  main_content = H('div', {'class': 'main-content'},
    H('div', {'class': 'hcenter'},
      H('div', {'class': 'body-copy'}, sections)))
  footer = H('footer', {},
    H('div', {'class': 'hcenter footer-flexbox'},
      FooterBlock(copyright)))

  return page.MixedContent([
    '<!DOCTYPE html>',
    H('html', {'lang': 'en'}, page.MixedContent([
      head,
      H('body', {}, page.MixedContent([
        header,
        main_content,
        footer,
      ])),
    ])),
  ])


@Render.register(document.Section)
def RenderDocumentSection(section) -> page.Fragment:
  title = Render(section.title)
  body = Render(section.body)
  return page.MixedContent([
    H('h2', {'class': 'section'}, title),
    body,
  ])


@Render.register(document.HTMLNode)
def RenderHTMLNode(node) -> page.Fragment:
  content = Render(node.content)
  return page.HTMLNode(tag=node.tag, attrs=node.attrs, content=content)


@Render.register(document.Code)
def RenderCode(code) -> page.Fragment:
  content = Render(code.content)
  return H('span', {'class': 'code'}, content)


@Render.register(document.CodeBlock)
def RenderCodeBlock(block) -> page.Fragment:
  if block.header is not None:
    header = Render(block.header)
    body = Render(block.body)
    return H('div', {'class': 'code'}, page.MixedContent([
      H('div', {'class': 'code-header'}, header),
      H('div', {'class': 'code-body'},
        H('pre', {}, body)),
    ]))
  else:
    body = Render(block.body)
    return H('div', {'class': 'code'},
      H('div', {'class': 'code-body'},
        H('pre', {}, body)))
