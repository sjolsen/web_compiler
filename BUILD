package(default_visibility = ["//visibility:public"])

py_binary(
    name = "compiler",
    srcs = ["compiler.py"],
    deps = [
        "//backend:linker",
        "//backend:page",
        "//backend/swiss:document",
        "//frontend",
    ],
)
