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
    srcs = [":example_page"],
    build_info = "//bazel:build_info",
    index = ":example_page",
    nav = "nav.xml",
    output_root = "example",
)
