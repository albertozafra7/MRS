# -*- mode: python -*-
# vi: set ft=python :

#
# src/BUILD
# HRVO Library
#
# Copyright 2009 University of North Carolina at Chapel Hill
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Please send all bug reports to <geom@cs.unc.edu>.
#
# The authors may be contacted via:
#
# Jamie Snape, Jur van den Berg, Stephen J. Guy, and Dinesh Manocha
# Dept. of Computer Science
# 201 S. Columbia St.
# Frederick P. Brooks, Jr. Computer Science Bldg.
# Chapel Hill, N.C. 27599-3175
# United States of America
#
# <https://gamma.cs.unc.edu/HRVO/>
#

load("@rules_cc//cc:defs.bzl", "cc_library")
load("@rules_pkg//:pkg.bzl", "pkg_tar")

licenses(["notice"])

genrule(
    name = "export",
    outs = ["Export.h"],
    cmd = """
cat << 'EOF' > $@
/*
 * Export.h
 * HRVO Library
 *
 * Copyright 2009 University of North Carolina at Chapel Hill
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Please send all bug reports to <geom@cs.unc.edu>.
 *
 * The authors may be contacted via:
 *
 * Jamie Snape, Jur van den Berg, Stephen J. Guy, and Dinesh Manocha
 * Dept. of Computer Science
 * 201 S. Columbia St.
 * Frederick P. Brooks, Jr. Computer Science Bldg.
 * Chapel Hill, N.C. 27599-3175
 * United States of America
 *
 * <https://gamma.cs.unc.edu/HRVO/>
 */

#ifndef HRVO_EXPORT_H_
#define HRVO_EXPORT_H_

#ifdef HRVO_STATIC_DEFINE
#define HRVO_EXPORT
#else
#ifdef _WIN32
#ifdef HRVO_EXPORTS
#define HRVO_EXPORT __declspec(dllexport)
#else
#define HRVO_EXPORT __declspec(dllimport)
#endif
#else
#define HRVO_EXPORT __attribute__((visibility("default")))
#endif
#endif

#endif  // HRVO_EXPORT_H_
EOF
""",
    visibility = ["//visibility:private"],
)

filegroup(
    name = "hdrs",
    srcs = [
        "Export.h",
        "HRVO.h",
        "Simulator.h",
        "Vector2.h",
    ],
    visibility = ["//visibility:private"],
)

cc_library(
    name = "HRVO",
    srcs = [
        "Agent.cpp",
        "Agent.h",
        "Definitions.h",
        "Goal.cpp",
        "Goal.h",
        "KdTree.cpp",
        "KdTree.h",
        "Simulator.cpp",
        "Vector2.cpp",
    ],
    hdrs = [":hdrs"],
    copts = [
        "-fvisibility-inlines-hidden",
        "-fvisibility=hidden",
    ],
    includes = ["."],
    visibility = ["//visibility:public"],
)

pkg_tar(
    name = "include",
    srcs = [":hdrs"],
    mode = "0644",
    package_dir = "/usr/include/HRVO",
    visibility = ["//:__pkg__"],
)

pkg_tar(
    name = "lib",
    srcs = ["//src:HRVO"],
    mode = "0644",
    package_dir = "/usr/lib",
    visibility = ["//:__pkg__"],
)
