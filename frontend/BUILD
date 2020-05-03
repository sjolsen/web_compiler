load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_library")

package(default_visibility = ["//:__subpackages__"])

py_library(
    name = "document",
    srcs = ["document.py"],
)

py_library(
    name = "frontend",
    srcs = ["frontend.py"],
    deps = [
        ":document",
        ":parser",
        ":nav",
    ],
)

py_library(
    name = "parser",
    srcs = ["parser.py"],
    deps = [
        ":document",
        ":nav",
        requirement("more_itertools"),
    ],
)

py_library(
    name = "nav",
    srcs = ["nav.py"],
    deps = ["//backend:linker"],
)
