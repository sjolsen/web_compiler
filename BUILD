load("@pip_deps//:requirements.bzl", "requirement")
load("//server:server.bzl", "simple_resource")

py_library(
  name = "document",
  srcs = ["document.py"],
)

py_library(
  name = "parser",
  srcs = ["parser.py"],
  deps = [":document"],
)

py_binary(
  name = "render",
  srcs = ["render.py"],
  deps = [
      ":parser",
      requirement("more_itertools"),
  ],
  visibility = ["//visibility:public"],
)

simple_resource(
    name = "style",
    src = "style.css",
    path = "style.css",
    visibility = ["//visibility:public"],
)

simple_resource(
    name = "bullet",
    src = "x.svg",
    path = "x.svg",
    visibility = ["//visibility:public"],
)
