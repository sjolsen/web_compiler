package(default_visibility = ["//visibility:public"])

py_binary(
    name = "compiler",
    srcs = ["compiler.py"],
    deps = [
        "//compiler/backend:linker",
        "//compiler/backend:page",
        "//compiler/backend/swiss:document",
        "//compiler/frontend:frontend",
    ],
)
