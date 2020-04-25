import datetime
import functools
import html
from typing import Any, Dict, Iterable, Iterator, Optional, Text

from absl import flags

from web_design.compiler.backend import linker
from web_design.compiler.backend import page
from web_design.compiler.frontend import document

flags.DEFINE_string('info_file', None, 'TODO')
flags.mark_flags_as_required(['info_file'])

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
def Render(obj) -> page.Fragment:
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


def Nav() -> page.Fragment:
  nav_icon = linker.Reference('web_design/compiler/backend/swiss/x.svg')
  links = [
    ('Home', '#', nav_icon),
    ('Document index', '#', nav_icon),
    ('Contact', '#', nav_icon),
  ]
  anchors = [
    H('a', {'class': 'nav-row', 'href': href}, page.MixedContent([
      H('img', {'class': 'nav-icon', 'src': src}),
      H('li', {}, page.MixedContent([text])),
    ]))
    for text, href, src in links
  ]
  spacer = H('div', {'class': 'nav-spacer'})
  return H('nav', {}, page.MixedContent([
    H('ul', {}, page.MixedContent(list(intersperse(spacer, anchors)))),
  ]))


def FooterBlock(copyright: page.Fragment) -> page.Fragment:
  with open(FLAGS.info_file, 'rt') as f:
    info = dict(l.split(' ', 1) for l in f)
  git_ref = info["STABLE_GIT_COMMIT"].strip()
  if git_ref.endswith('-dirty'):
    git_hash = git_ref[:-6]
  else:
    git_hash = git_ref
  git_url = f'https://github.com/sjolsen/web-design/commit/{git_hash}'
  return page.MixedContent([
    H('div', {'class': 'footer-left'}, page.MixedContent([
      f'Copyright © {datetime.datetime.now().year} ',
      copyright,
    ])),
    H('div', {'class': 'footer-right'}, page.MixedContent([
      f'Built from ',
      H('a', {'class': 'footer-git', 'href': git_url}, git_ref),
    ])),
  ])


@Render.register(document.Document)
def RenderDocument(doc) -> page.Fragment:
  title = Render(doc.title)
  subtitle = Render(doc.subtitle)
  copyright = Render(doc.copyright)
  sections = page.MixedContent([Render(s) for s in doc.sections])
  style = linker.Reference('web_design/compiler/backend/swiss/style.css')

  head = H('head', {}, page.MixedContent([
    H('meta', {'charset': 'utf-8'}),
    H('title', {}, title),
    H('link', {'rel': 'stylesheet', 'href': style, 'type': 'text/css'}),
  ]))
  header = H('header', {},
    H('div', {'class': 'hcenter header-flexbox'}, page.MixedContent([
      TitleBlock(title, subtitle),
      H('div', {'class': 'header-vr title-rule'}),
      Nav(),
    ])))
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
