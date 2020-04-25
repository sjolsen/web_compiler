load("//compiler:compiler.bzl", "assets")

package(default_visibility = ["//compiler:__subpackages__"])

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
        "//compiler/backend:linker",
        "//compiler/backend:page",
        "//compiler/frontend:document",
    ],
)
