load("@bazel_skylib//lib:paths.bzl", "paths")

BuildInfo = provider(fields = ["info_file", "version_file"])

def _build_info(ctx):
    return [BuildInfo(info_file = ctx.info_file, version_file = ctx.version_file)]

build_info = rule(
    implementation = _build_info,
)

InputInfo = provider(fields = ["assets", "documents"])

def _assets(ctx):
    return [InputInfo(
        assets = depset(ctx.files.srcs),
        documents = depset(),
    )]

assets = rule(
    implementation = _assets,
    attrs = {
        "srcs": attr.label_list(allow_files = True),
    },
)

def _document(ctx):
    srcs = []
    transitive_srcs = []
    for src in ctx.attr.srcs:
        if InputInfo in src:
            transitive_srcs.append(src[InputInfo].assets)
        else:
            srcs.extend(src.files)
    return [InputInfo(
        assets = depset(srcs, transitive = transitive_srcs),
        documents = depset([ctx.file.main]),
    )]

document = rule(
    implementation = _document,
    attrs = {
        "main": attr.label(
            mandatory = True,
            allow_single_file = True,
        ),
        "srcs": attr.label_list(
            allow_files = True,
        ),
    },
)

def _workspace(ctx, label):
    """Get the workspace name associated with a Label.

    Labels do have a workspace_name field, but annoyingly it returns an empty
    string for the default workspace. When the name of the default workspace is
    needed, we get it from ctx.

    Args:
        ctx: The rule context.
        label: The label to inspect.
    """
    if label.workspace_name:
        return label.workspace_name
    else:
        return ctx.workspace_name

def _runfiles_path(ctx, file):
    return paths.normalize(_workspace(ctx, file.owner) + "/" + file.short_path)

def _make_manifest(ctx, assets, documents, index, output_root):
    m_assets = ["Asset(%s, %s)" % (repr(_runfiles_path(ctx, f)), repr(f.path)) for f in assets.to_list()]
    m_docs = ["Document(%s, %s)" % (repr(_runfiles_path(ctx, f)), repr(f.path)) for f in documents.to_list()]
    m_inputs = '\n'.join(
        ["["] + ["        " + x + "," for x in m_assets + m_docs] + ["    ]"])
    m_contents = """Manifest(
    inputs={m_inputs},
    index={m_index},
    output_root={m_output_root})
""".format(
        m_inputs = m_inputs,
        m_index = repr(_runfiles_path(ctx, index)),
        m_output_root = repr(output_root))
    manifest = ctx.actions.declare_file(ctx.label.name + '_manifest')
    ctx.actions.write(
        content = m_contents,
        output = manifest,
    )
    return manifest

SiteInfo = provider(fields = ["tarball"])

def _site(ctx):
    assets = depset(transitive = [src[InputInfo].assets for src in ctx.attr.srcs])
    documents = depset(transitive = [src[InputInfo].documents for src in ctx.attr.srcs])
    indices = ctx.attr.index[InputInfo].documents.to_list()
    if len(indices) != 1:
        fail("Must provide one index document", ctx.attr.index)
    index = indices[0]
    manifest = _make_manifest(ctx, assets, documents, index, ctx.attr.output_root)
    info_file = ctx.attr.build_info[BuildInfo].info_file
    version_file = ctx.attr.build_info[BuildInfo].version_file
    args = ctx.actions.args()
    inputs = [manifest, info_file, version_file]
    args.add("--manifest", manifest)
    if ctx.attr.nav:
        inputs.append(ctx.file.nav)
        args.add("--nav", ctx.file.nav)
    args.add("--output", ctx.outputs.out)
    args.add("--info_file", info_file)
    args.add("--version_file", version_file)
    ctx.actions.run(
        executable = ctx.executable._compiler,
        arguments = [args],
        inputs = depset(
            inputs,
            transitive = [assets, documents]),
        outputs = [ctx.outputs.out],
    )
    return [SiteInfo(tarball = ctx.outputs.out)]

site = rule(
    implementation = _site,
    attrs = {
        "srcs": attr.label_list(
            mandatory = True,
            providers = [InputInfo],
        ),
        "index": attr.label(
            mandatory = True,
            providers = [InputInfo],
        ),
        "nav": attr.label(
            allow_single_file = True,
        ),
        "output_root": attr.string(
            mandatory = True,
        ),
        "build_info": attr.label(
            mandatory = True,
            providers = [BuildInfo],
        ),
        "_compiler": attr.label(
            executable = True,
            cfg = "exec",
            default = "//:compiler",
        ),
    },
    outputs = {
        "out": "%{name}.tar.gz",
    },
)
