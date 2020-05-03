load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_binary")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "compiler",
    srcs = ["compiler.py"],
    deps = [
        "//backend:linker",
        "//backend:page",
        "//backend/swiss:document",
        "//frontend",
        requirement("absl-py"),
    ],
)
