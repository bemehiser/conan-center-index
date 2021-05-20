from conans import CMake, ConanFile, tools
import os

required_conan_version = ">=1.28.0"

class AwsCrtCpp(ConanFile):
    name = "aws-crt-cpp"
    description = "C++ wrapper around the aws-c-* libraries. Provides Cross-Platform Transport Protocols and SSL/TLS implementations for C++."
    topics = ("conan", "aws", "amazon", "cloud", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-crt-cpp"
    license = "Apache-2.0",
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

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

    # def requirements(self):
    #     self.requires("aws-c-common/0.5.11")

    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        git.clone(**self.conan_data["sources"][self.version], branch=("v%s" % self.version), args="--recursive")

        # tools.get(**self.conan_data["sources"][self.version])
        # extracted_folder = "aws-crt-cpp-{}".format(self.version)
        # os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_DEPS"] = True
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "aws-crt-cpp"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "aws-crt-cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-crt-cpp"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"

        self.cpp_info.components["aws-c-auth"].libs = ["aws-c-auth"]
        self.cpp_info.components["aws-c-auth"].names["cmake_find_package"] = "aws-c-auth"
        self.cpp_info.components["aws-c-auth"].names["cmake_find_package_multi"] = "aws-c-auth"
        self.cpp_info.components["aws-c-cal"].libs = ["aws-c-cal"]
        self.cpp_info.components["aws-c-cal"].names["cmake_find_package"] = "aws-c-cal"
        self.cpp_info.components["aws-c-cal"].names["cmake_find_package_multi"] = "aws-c-cal"
        self.cpp_info.components["aws-c-common"].libs = ["aws-c-common"]
        self.cpp_info.components["aws-c-common"].libs = ["aws-c-common"]
        self.cpp_info.components["aws-c-common"].names["cmake_find_package"] = "aws-c-common"
        self.cpp_info.components["aws-c-common"].names["cmake_find_package"] = "aws-c-common"
        self.cpp_info.components["aws-c-common"].names["cmake_find_package_multi"] = "aws-c-common"
        self.cpp_info.components["aws-c-common"].names["cmake_find_package_multi"] = "aws-c-common"
        self.cpp_info.components["aws-c-compression"].libs = ["aws-c-compression"]
        self.cpp_info.components["aws-c-compression"].names["cmake_find_package"] = "aws-c-compression"
        self.cpp_info.components["aws-c-compression"].names["cmake_find_package_multi"] = "aws-c-compression"
        self.cpp_info.components["aws-c-event-stream"].libs = ["aws-c-event-stream"]
        self.cpp_info.components["aws-c-event-stream"].names["cmake_find_package"] = "aws-c-event-stream"
        self.cpp_info.components["aws-c-event-stream"].names["cmake_find_package_multi"] = "aws-c-event-stream"
        self.cpp_info.components["aws-c-http"].libs = ["aws-c-http"]
        self.cpp_info.components["aws-c-http"].names["cmake_find_package"] = "aws-c-http"
        self.cpp_info.components["aws-c-http"].names["cmake_find_package_multi"] = "aws-c-http"
        self.cpp_info.components["aws-c-io"].libs = ["aws-c-io"]
        self.cpp_info.components["aws-c-io"].names["cmake_find_package"] = "aws-c-io"
        self.cpp_info.components["aws-c-io"].names["cmake_find_package_multi"] = "aws-c-io"
        self.cpp_info.components["aws-c-mqtt"].libs = ["aws-c-mqtt"]
        self.cpp_info.components["aws-c-mqtt"].names["cmake_find_package"] = "aws-c-mqtt"
        self.cpp_info.components["aws-c-mqtt"].names["cmake_find_package_multi"] = "aws-c-mqtt"
        self.cpp_info.components["aws-crt-cpp-lib"].libs = ["aws-crt-cpp"]
        self.cpp_info.components["aws-crt-cpp-lib"].names["cmake_find_package"] = "aws-crt-cpp"
        self.cpp_info.components["aws-crt-cpp-lib"].names["cmake_find_package_multi"] = "aws-crt-cpp"

        # TODO: Figure out dependencies of each library
        if self.settings.os == "Linux":
            self.cpp_info.components["aws-crt-cpp-lib"].system_libs = ["m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["aws-crt-cpp-lib"].system_libs = ["bcrypt", "ws2_32"]
        if not self.options.shared:
            if tools.is_apple_os(self.settings.os):
                self.cpp_info.components["aws-crt-cpp-lib"].frameworks = ["CoreFoundation"]
        self.cpp_info.components["aws-crt-cpp-lib"].builddirs = [os.path.join("lib", "cmake")]

