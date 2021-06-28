from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os

required_conan_version = ">=1.28.0"


class Twemproxy(ConanFile):
    name = "twemproxy"
    description = "a fast and lightweight proxy for memcached and redis protocol"
    topics = ("conan", "proxy")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/twitter/twemproxy"
    license = "Apache-2.0",
    exports_sources = "patches/**"
    generators = "pkg_config"
    settings = "os", "arch", "compiler", "build_type", "cppstd"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    build_requires = (
        "automake/1.16.3",
        "libtool/2.4.6",
    )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "twemproxy-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        autotools = AutoToolsBuildEnvironment(self)

        with tools.chdir(os.path.join(self._source_subfolder, "contrib")):
            tools.untargz("yaml-0.1.4.tar.gz")
        self.run("make distclean", cwd=os.path.join(self._source_subfolder, "contrib", "yaml-0.1.4"))
            # autotools.make(args=["distclean"])

        vars = autotools.vars
        vars["CFLAGS"] = "-O3 -fno-strict-aliasing"
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fvi")
        autotools.configure(configure_dir=self._source_subfolder, vars=vars)
        autotools.make(args=["install"], vars=vars)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("libevent.a", dst="lib", src="src/event")
        self.copy("libproto.a", dst="lib", src="src/proto")
        self.copy("libhashkit.a", dst="lib", src="src/hashkit")
        self.copy("libyaml.a", dst="lib", src="src/.libs")

    def package_info(self):
        self.cpp_info.names = "twemproxy"
        self.cpp_info.names["cmake"] = "Nutcracker"
        self.cpp_info.names["cmake_paths"] = "Nutcracker"
        self.cpp_info.names["cmake_find_package"] = "Nutcracker"
        self.cpp_info.names["cmake_find_package_multi"] = "Nutcracker"

        self.cpp_info.components["event"].libs = ["event"]
        self.cpp_info.components["hashkit"].libs = ["hashkit"]
        self.cpp_info.components["proto"].libs = ["proto"]
        self.cpp_info.components["yaml"].libs = ["yaml"]
