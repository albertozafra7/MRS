# -*- mode: python -*-
# vi: set ft=python :

#
# BUILD
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

load("@rules_pkg//:pkg.bzl", "pkg_deb", "pkg_tar")

licenses(["notice"])

exports_files(
    ["LICENSE"],
    visibility = ["//visibility:public"],
)

pkg_tar(
    name = "doc",
    srcs = ["LICENSE"],
    mode = "0644",
    package_dir = "/usr/share/doc/HRVO",
    visibility = ["//visibility:private"],
)

genrule(
    name = "pc",
    outs = ["HRVO.pc"],
    cmd = """
cat << 'EOF' > $@
#
# HRVO.pc
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

prefix=/usr
exec_prefix=$${prefix}
libdir=$${exec_prefix}/lib
includedir=$${prefix}/include/HRVO

Name: HRVO Library
Description: Reciprocal Collision Avoidance with Acceleration-Velocity Obstacles
URL: https://gamma.cs.unc.edu/HRVO/
Version: 1.1.0
Libs: -L$${libdir} -lHRVO
Cflags: -I$${includedir}
EOF
""",
    visibility = ["//visibility:private"],
)

pkg_tar(
    name = "pkgconfig",
    srcs = ["HRVO.pc"],
    mode = "0644",
    package_dir = "/usr/lib/pkgconfig",
    visibility = ["//visibility:private"],
)

pkg_tar(
    name = "HRVO",
    extension = "tar.gz",
    visibility = ["//visibility:public"],
    deps = [
        ":doc",
        ":pkgconfig",
        "//src:include",
        "//src:lib",
    ],
)

pkg_deb(
    name = "deb",
    architecture = "amd64",
    data = ":HRVO",
    depends = [
        "libc6",
        "libgcc1",
        "libstdc++6",
    ],
    description = "The Hybrid Reciprocal Velocity Obstacle",
    homepage = "https://gamma.cs.unc.edu/HRVO/",
    maintainer = "Jamie Snape",
    package = "hrvo",
    version = "1.1.0",
    visibility = ["//visibility:public"],
)
