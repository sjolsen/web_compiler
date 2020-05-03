load("@rules_python//python:defs.bzl", "py_library")

package(default_visibility = ["//:__subpackages__"])

py_library(
    name = "linker",
    srcs = ["linker.py"],
)

py_library(
    name = "page",
    srcs = ["page.py"],
    deps = [":linker"],
)
