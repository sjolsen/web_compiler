load("//:compiler.bzl", "document", "site")

package(default_visibility = ["//visibility:public"])

document(
    name = "example_page",
    srcs = [
        "fib.c",
        "fib.dis",
    ],
    main = "example.xml",
)

site(
    name = "example",
    srcs = [
        ":example_page",
        # TODO: Make this implicit
        "//backend/swiss:nav_buttons",
        "//backend/swiss:style",
    ],
    build_info = "//bazel:build_info",
    index = ":example_page",
    output_root = "example",
)
