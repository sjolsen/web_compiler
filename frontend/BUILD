load("@pip_deps//:requirements.bzl", "requirement")

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
    ],
)

py_library(
    name = "parser",
    srcs = ["parser.py"],
    deps = [
        ":document",
        requirement("more_itertools"),
    ],
)
