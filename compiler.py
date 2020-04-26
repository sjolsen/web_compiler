import functools
import os
import subprocess
import tempfile
from typing import NamedTuple, Sequence, Union

from absl import app
from absl import flags

from web_compiler.backend import linker
from web_compiler.backend import page
from web_compiler.backend.swiss import document as swissdoc
from web_compiler.frontend import frontend

flags.DEFINE_string('manifest', None, 'TODO')
flags.DEFINE_string('output', None, 'TODO')
flags.mark_flags_as_required(['manifest', 'output'])

FLAGS = flags.FLAGS


class Asset(NamedTuple):
    src_url: str
    path: str


class Document(NamedTuple):
    src_url: str
    path: str


LinkerInput = Union[Asset, Document]


class Manifest(NamedTuple):
    inputs: Sequence[LinkerInput]
    index: str
    output_root: str


def main(argv):
    if len(argv) > 1:
        raise app.UsageError('TODO')
    with open(FLAGS.manifest, 'rt') as f:
        manifest = eval(f.read(), globals())
    assert isinstance(manifest, Manifest)
    with tempfile.TemporaryDirectory() as d:
        load = frontend.Loader({i.src_url: i.path for i in manifest.inputs})
        link = linker.Linker(d)
        documents = set()
        for i in manifest.inputs:
            basename = os.path.basename(i.src_url)
            if isinstance(i, Asset):
                link.add_resource(
                    ref=linker.Reference(i.src_url),
                    out=os.path.join(manifest.output_root, 'assets', basename),
                    resource=linker.StaticResource(i.path))
            elif isinstance(i, Document):
                base, _ = os.path.splitext(basename)
                ref = linker.Reference(i.src_url)
                doc = load.LoadDocument(i.path)
                link.add_resource(
                    ref=ref,
                    out=os.path.join(manifest.output_root, base + '.html'),
                    resource=page.PageResource(swissdoc.RenderDocument(doc)))
                documents.add(ref)
            else:
                raise TypeError(i)
        index = linker.Reference('_index')
        link.add_resource(
            ref=index,
            out=os.path.join(manifest.output_root, 'index.html'),
            resource=linker.LinkResource(linker.Reference(manifest.index)))
        link.link(documents | {index})
        subprocess.check_call(['tar', '-czf', FLAGS.output, '-C', d, manifest.output_root])


if __name__ == '__main__':
    app.run(main)
