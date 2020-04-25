import functools
import os
import subprocess
import tempfile
from typing import NamedTuple, Sequence, Union

from absl import app
from absl import flags
from rules_python.python.runfiles import runfiles

from web_design.compiler.backend import linker
from web_design.compiler.backend import page
from web_design.compiler.backend.swiss import document as swissdoc
from web_design.compiler.frontend import frontend

flags.DEFINE_string('manifest', None, 'TODO')
flags.DEFINE_string('output', None, 'TODO')
flags.mark_flags_as_required(['manifest', 'output'])

FLAGS = flags.FLAGS


class Asset(NamedTuple):
    src_url: str


class Document(NamedTuple):
    src_url: str


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
    print(manifest)
    assert isinstance(manifest, Manifest)
    r = runfiles.Create()
    link = linker.Linker()
    documents = set()
    for i in manifest.inputs:
        basename = os.path.basename(i.src_url)
        if isinstance(i, Asset):
            link.add_resource(
                ref=linker.Reference(i.src_url),
                out=os.path.join(manifest.output_root, 'assets', basename),
                resource=linker.StaticResource(r.Rlocation(i.src_url)))
        elif isinstance(i, Document):
            base, _ = os.path.splitext(basename)
            ref = linker.Reference(i.src_url)
            doc = frontend.LoadDocument(r.Rlocation(i.src_url))
            link.add_resource(
                ref=ref,
                out=os.path.join(manifest.output_root, base + '.html'),
                resource=page.PageResource(swissdoc.RenderDocument(doc)))
            documents.add(ref)
        else:
            raise TypeError(i)
    link.add_resource(
        ref='_index',
        out=os.path.join(manifest.output_root, 'index.html'),
        resource=linker.LinkResource(linker.Reference(manifest.index)))
    with tempfile.TemporaryDirectory() as d:
        link.link(d, documents)
        subprocess.check_call(['tar', '-czf', FLAGS.output, '-C', d, '.'])


if __name__ == '__main__':
    app.run(main)
