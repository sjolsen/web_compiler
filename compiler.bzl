load("//server:server.bzl", "ResourceInfo", "TransitiveResources")

InputInfo = provider(fields = ["assets", "documents"])

def _assets(ctx):
    return [InputInfo(assets = depset(ctx.files.srcs))]

assets = rule(
    implementation = _assets,
    attrs = {
        "srcs": attr.label_list(allow_files = True),
    },
)

def _document(ctx):
    return [InputInfo(documents = depset([ctx.file.src]))]

document = rule(
    implementation = _document,
    attrs = {
        "src": attr.label(
            mandatory = True,
            allow_files = True,
        ),
    },
)

def _make_manifest(ctx, assets, documents, index, output_root):
    m_assets = ["Asset(%s)" % f.short_path for f in assets.to_list()]
    m_docs = ["Document(%s)" % f.short_path for f in documents.to_list()]
    m_contents = """Manifest(
    inputs={m_inputs},
    index={m_index},
    output_root={m_output_root})
""".format(
        m_inputs = repr(m_assets + m_docs),
        m_index = repr(index.short_path),
        m_output_root = repr(output_root))
    manifest = ctx.actions.declare_file(ctx.label.name + '_manifest')
    ctx.actions.write(
        contents = m_contents,
        output = manfest,
    )
    return manifest

def _site(ctx):
    assets = depset(transitive = [src[InputInfo].assets for src in ctx.attr.src])
    documents = depset(transitive = [src[InputInfo].documents for src in ctx.attr.src])
    indices = ctx.attr.index[InputInfo].documents.to_list()
    if len(indices) != 1:
        fail("Must provide one index document", ctx.attr.index)
    index = indices[0]
    manifest = _make_manifest(ctx, assets, documents, index, ctx.attr.output_root)
    args = ctx.actions.args()
    args.add("--manifest", manifest)
    args.add("--output", ctx.outputs.out)
    ctx.actions.run(
        executable = ctx.executable._compiler,
        args = args,
        inputs = depset([manifest], transitive = [assets, documents]),
        outputs = ctx.outputs.out,
    )

site = rule(
    implementation = _site,
    atrs = {
        "srcs": attr.label_list(
            mandatory = True,
            providers = [InputInfo],
        ),
        "index": attr.label(
            mandatory = True,
            providers = [InputInfo],
        ),
        "output_root": attr.string(
            mandatory = True,
        ),
        "_compiler": attr.label(
            executable = True,
            cfg = "exec",
            default = "//compiler",
        ),
    },
    outputs = {
        "out": "%{name}.tar.gz",
    },
)
