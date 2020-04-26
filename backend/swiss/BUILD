load("//:compiler.bzl", "assets")

# TODO: Decouple from the compiler framework
package(default_visibility = ["//:__subpackages__"])

assets(
    name = "nav_buttons",
    srcs = ["x.svg"],
    visibility = ["//visibility:public"],  # TODO: Make this implicit
)

assets(
    name = "style",
    srcs = ["style.css"],
    visibility = ["//visibility:public"],  # TODO: Make this implicit
)

py_library(
    name = "document",
    srcs = ["document.py"],
    # data = [
    #     ":style",
    #     ":nav_buttons",
    # ],
    deps = [
        "//backend:linker",
        "//backend:page",
        "//frontend:document",
        "//frontend:nav",
    ],
)
