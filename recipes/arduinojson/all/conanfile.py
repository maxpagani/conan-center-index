from conan import ConanFile
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.50.0"


class ArduinojsonConan(ConanFile):
    name = "arduinojson"
    description = "C++ JSON library for IoT. Simple and efficient."
    homepage = "https://github.com/bblanchon/ArduinoJson"
    topics = ("json", "arduino", "iot", "embedded", "esp8266")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "6",
            "clang": "6",
        }

    def validate(self):
        if Version(self.version) >= "6.21.0":
            if self.settings.compiler.get_safe("cppstd"):
                check_min_cppstd(self, 11)
            elif str(self.settings.compiler) == 'apple-clang':
                raise ConanInvalidConfiguration("cppstd needs to be set on apple-clang to activate c++11.")
            else:
                minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
                if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                    raise ConanInvalidConfiguration(f"{self.ref} requires C++11, which your compiler does not support.")

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        has_arduinojson_root=Version(self.version) < "6.18.2"
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=has_arduinojson_root)

    def build(self):
        pass

    def package(self):
        copy(self, "*LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "include"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"ArduinoJson": "ArduinoJson::ArduinoJson"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ArduinoJson")
        self.cpp_info.set_property("cmake_target_name", "ArduinoJson")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "ArduinoJson"
        self.cpp_info.names["cmake_find_package_multi"] = "ArduinoJson"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
