#!/bin/sh

# TODO: Provide this functionality in web_compiler
echo STABLE_GIT_COMMIT "$(git describe --no-match --always --dirty)"
