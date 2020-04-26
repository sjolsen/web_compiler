#!/bin/sh

echo STABLE_GIT_URL "https://github.com/sjolsen/web_compiler/commit/{git_hash}"
# TODO: Provide this functionality in web_compiler
echo STABLE_GIT_COMMIT "$(git describe --no-match --always --dirty)"
