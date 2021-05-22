from conans import CMake, ConanFile, tools
import os

required_conan_version = ">=1.28.0"

class AzureStorageCpp(ConanFile):
    name = "azure-storage-cpp"
    description = "Azure Storage Client Library for C++ (7.5.0)"
    topics = ("conan", "azure", "cloud", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Azure/azure-storage-cpp"
    license = "Apache-2.0",
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type", "cppstd"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    requires = (
        "libxml2/2.9.10",
        "cpprestsdk/2.10.18",
        "websocketpp/0.8.2",
        # TODO: Might require libuuid
    )

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "azure-storage-cpp-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.settings.os == "Macos":
            self._cmake.definitions["CMAKE_XCODE_ATTRIBUTE_CLANG_CXX_LIBRARY"] = "libc++"
            self._cmake.definitions["CXXFLAGS"] = "-stdlib=libc++ -std=c++11"
            self._cmake.definitions["CMAKE_FIND_FRAMEWORK"] = "LAST"
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_SAMPLES"] = False
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

        tools.rmdir(os.path.join(self.package_folder, "lib", "azure-storage-cpp"))

    def package_info(self):

        self.cpp_info.filenames["cmake_find_package"] = "azure-storage-cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "azure-storage-cpp"
        self.cpp_info.names["cmake_find_package"] = "azure-storage-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "azure-storage-cpp"
        self.cpp_info.libs = ["azurestorage"]
