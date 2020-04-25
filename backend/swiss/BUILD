load("//compiler:compiler.bzl", "assets")

package(default_visibility = ["//compiler:__subpackages__"])

assets(
    name = "style",
    srcs = ["style.css"],
)

assets(
    name = "nav_buttons",
    srcs = ["x.svg"],
)

py_library(
    name = "document",
    srcs = ["document.py"],
    # data = [
    #     ":style",
    #     ":nav_buttons",
    # ],
    deps = [
        "//compiler/backend:linker",
        "//compiler/backend:page",
        "//compiler/frontend:document",
    ],
)
