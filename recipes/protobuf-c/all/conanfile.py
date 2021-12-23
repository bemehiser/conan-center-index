from conans import ConanFile, CMake, tools
import os


class ProtobufcConan(ConanFile):
    name = "protobuf-c"
    license = "https://github.com/protobuf-c/protobuf-c/blob/master/LICENSE"
    url = "https://github.com/protobuf-c/protobuf-c"
    settings = "cppstd", "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    description = "conan package for protobuf-c"
    exports_sources = ["patches/**"]
    _source_subfolder = "source_subfolder"
    requires = [
        "protobuf/3.19.2",
    ]
    options = {
        "build_proto3": [True, False],
        "build_protoc": [True, False],
        "shared": [True, False],
        "verbose_makefile": [True, False],
    }
    default_options = {
        "build_proto3": True,
        "build_protoc": True,
        "shared": False,
        "verbose_makefile": False,
    }

    def config_options(self):
        if self.settings.compiler == 'gcc' and float(self.settings.compiler.version.value) >= 5.1:
            if self.settings.compiler.cppstd:
                tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(f"{self.name}-{self.version}", self._source_subfolder)

        if "patches" in self.conan_data and self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_PROTO3"] = self.options.build_proto3
        cmake.definitions["BUILD_PROTOC"] = self.options.build_protoc
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["HAS_SYSTEM_PROTOBUF"] = False
        cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = self.options.verbose_makefile
        cmake.verbose = True
        cmake.configure(source_folder=f"{self._source_subfolder}/build-cmake")
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "ProtobufC"
        self.cpp_info.filenames["cmake_find_package_multi"] = "protobuf-c"
        self.cpp_info.names["cmake"] = "protobuf-c"
        self.cpp_info.names["cmake_paths"] = "protobuf-c"
        self.cpp_info.names["cmake_find_package"] = "protobuf-c"
        self.cpp_info.names["cmake_find_package_multi"] = "protobuf-c"
        self.cpp_info.libs = ["protobuf-c"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]

        bin_dir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_dir}")
        self.env_info.PATH.append(bin_dir)
