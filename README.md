[[Japanese/日本語](README.ja.md)]

# JVM-PyBind

JVM bindings for Python that enable seamless integration between Python and Java code through JNI (Java Native Interface).

## Features

- **Direct JNI Integration**: Low-level JNI bindings using ctypes for maximum performance
- **Dynamic Class Discovery**: Automatic discovery of Java classes, methods, and fields using reflection
- **Python Import Hook**: Use standard Python import syntax to access Java classes
- **Type Conversion**: Automatic conversion between Python and Java types
- **Memory Safety**: Proper JNI reference management and safe shutdown procedures
- **Cross-Platform**: Support for Windows, macOS (including ARM64), and Linux
- **Configuration**: Flexible configuration through pyproject.toml

## Quick Start

### Installation

```bash
pip install jvm
```

### Basic Usage

```python
# Import Java classes using standard Python syntax
from java.lang import System

# Call Java methods directly
System.out.println("Hello from JVM!")

# Access Java properties
print(f"Java Version: {System.getProperty('java.version')}")
print(f"Java Vendor: {System.getProperty('java.vendor')}")
```

## Command Line Interface

jvm-pybind provides a CLI for managing Java type stubs in your development environment.

### Installation

Install type stubs to enable IDE support and autocompletion:

```bash
# Install Java type stubs to current virtual environment
python -m jvm --install-stub
```

### Uninstallation

Remove type stubs when no longer needed:

```bash
# Remove Java type stubs from current virtual environment
python -m jvm --uninstall-stub
```

### Features

**Type Stub Management:**

- **Install stubs**: Automatically detects your virtual environment and installs Java type stubs for better IDE support
- **Uninstall stubs**: Cleanly removes all installed Java type stubs
- **Auto-generation**: Generates fresh stubs from your JVM installation if needed
- **Virtual environment detection**: Works with venv, virtualenv, conda, and other Python environment managers

**Supported Packages:**

- `java.lang` - Core Java classes (String, System, Object, etc.)
- `java.util` - Collections and utilities (List, Map, ArrayList, etc.)
- `java.io` - Input/output classes (File, InputStream, OutputStream, etc.)

### Requirements

- **Virtual Environment**: CLI operations require an active virtual environment
- **JVM Installation**: Java must be installed and accessible for stub generation

### Examples

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install jvm-pybind
pip install jvm-pybind

# Install type stubs for IDE support
python -m jvm --install-stub

# Now you get autocompletion in your IDE
from java.lang import System  # IDE will show available methods
```

### Help

```bash
python -m jvm --help
```

Output:

```
usage: jvm [-h] (--install-stub | --uninstall-stub)

JVM-PyBind: Python bindings for JVM with type stub management

options:
  -h, --help         show this help message and exit
  --install-stub     Install JDK type stubs to the current virtual environment
  --uninstall-stub   Remove JDK type stubs from the current virtual environment

Examples:
  python -m jvm --install-stub     Install JDK type stubs to virtual environment
  python -m jvm --uninstall-stub   Remove JDK type stubs from virtual environment
```

### Working with Custom Java Classes (Experimental)

> ⚠️ **Note**: Custom Java class access is currently experimental. While JAR files can be included in the classpath during JVM startup, direct access to custom classes through Python import syntax is not yet fully implemented.

**Current Capability:**

```toml
# pyproject.toml - JAR files are loaded into JVM classpath
[tool.jvm]
java-version = "17"
classpath = ["hello.jar"]
```

**Planned Feature (Not Yet Available):**

```python
# This will be supported in future versions
from mypkg import Hello  # Not yet implemented
message = Hello.greet("World")
```

**Current Workaround:**
Use the internal API to access custom classes:

```python
import jvm

# Get JVM instance
jvm_instance = jvm.JVM.get_instance()

# Find your custom class
hello_class = jvm_instance.find_class("mypkg/Hello")

# Access methods through low-level API
# (See Internal API section below)
```

## Configuration

Configure jvm-pybind through your `pyproject.toml` file:

```toml
[tool.jvm]
java-version = "17"  # Java version to use
classpath = [        # JAR files and directories to include
    "path/to/your.jar",
    "path/to/classes/"
]

[tool.jvm.deps]
maven = [            # Maven dependencies (future feature)
    "org.apache.commons:commons-lang3:3.12.0"
]
```

## System Requirements

### Java Runtime

- **Java 17** (recommended, configurable)
- Supported JDK distributions:
  - Oracle JDK
  - Eclipse Adoptium (formerly AdoptOpenJDK)
  - Amazon Corretto
  - Microsoft Build of OpenJDK
  - Azul Zulu
  - OpenJDK

### Python

- **Python 3.12+**
- Supported platforms:
  - Windows (x64)
  - macOS (Intel and Apple Silicon)
  - Linux (x64, ARM64)

## Architecture

jvm-pybind consists of several key components:

- **JVMLoader**: Initializes the JVM and loads the libjvm library
- **JNIHelper**: Low-level JNI function bindings with type safety
- **JVM**: Main interface for Java class discovery and method execution
- **Proxy Classes**: Python wrappers for Java packages, classes, and objects
- **Import Hook**: Integration with Python's import system

## Advanced Usage

### Direct JNI Access

```python
import jvm

# Get the JVM instance
jvm_instance = jvm.get_jvm()

# Find a Java class
string_class = jvm_instance.find_class("java.lang.String")

# Access class information
print(f"Methods: {len(string_class.methods)}")
print(f"Fields: {len(string_class.fields)}")
```

### Memory Management

The library automatically manages JNI references, but you can also control memory explicitly:

```python
from java.lang import System

# The JVM will be automatically shut down when Python exits
# For explicit control:
jvm.shutdown()
```

## Internal API Reference

> 📋 **Note**: This section documents the internal API for advanced users and developers. For most use cases, the high-level import syntax (`from java.lang import System`) is recommended.

### JVM Instance Management

```python
import jvm

# Get the current JVM instance (if running)
jvm_instance = jvm.get_jvm()  # Returns None if JVM not started

# Start JVM with custom configuration
from jvm.config import Config
from jvm.loader import JVMLoader

config = Config(java_version="17", classpath=["path/to/jar"], deps={})
jvm_instance = JVMLoader(config).start()
```

### Low-Level Class Access

```python
# Find a Java class by name
java_class = jvm_instance.find_class("java/lang/String")
print(f"Class: {java_class.name}")
print(f"Methods: {len(java_class.methods)}")
print(f"Fields: {len(java_class.fields)}")

# Access class methods and fields
for method in java_class.methods:
    print(f"Method: {method.name}({', '.join(method.parameters)}) -> {method.return_type}")
    print(f"Static: {method.is_static}")
```

### Direct JNI Operations

```python
# Access the underlying JNI helper
jni = jvm_instance.jni

# Find class and get method ID
string_class = jni.FindClass("java/lang/String")
length_method = jni.GetMethodID(string_class, "length", "()I")

# Create a Java string
java_str = jni.NewStringUTF("Hello World")

# Call method
length = jni.CallIntMethod(java_str, length_method)
print(f"String length: {length}")
```

### Package Discovery

```python
# Discover classes in a package
classes = jvm_instance.discover_package_classes("java.util")
for class_name in classes:
    print(f"Found class: {class_name}")
```

### Proxy Objects

```python
from jvm.proxy import ClassProxy, PackageProxy

# Create proxy for a Java package
java_lang = PackageProxy(jvm_instance, "java.lang")
system_class = java_lang.System  # Returns ClassProxy

# Access static methods
system_class.gc()  # Calls System.gc()
property_value = system_class.getProperty("java.version")
```

### Configuration Access

```python
from jvm.config import Config

# Load configuration from pyproject.toml
config = Config.from_pyproject()
print(f"Java Version: {config.java_version}")
print(f"Classpath: {config.classpath}")
print(f"Dependencies: {config.deps}")

# Create custom configuration
custom_config = Config(
    java_version="11",
    classpath=["/path/to/custom.jar"],
    deps={"maven": ["org.apache.commons:commons-lang3:3.12.0"]}
)
```

### Type Conversion

```python
from jvm.typeconv import to_java, to_python

# Convert Python values to Java
java_string = to_java(jvm_instance, "Hello")
java_int = to_java(jvm_instance, 42)
java_bool = to_java(jvm_instance, True)

# Convert Java values to Python
python_value = to_python(jvm_instance, java_string)
```

### Exception Handling

```python
from jvm.jvm import JNIException

try:
    # JNI operations that might fail
    unknown_class = jvm_instance.find_class("com/nonexistent/Class")
except JNIException as e:
    print(f"JNI error: {e}")
```

### Available Classes and Methods

The main classes you can import and use:

| Class           | Purpose                  | Example Usage                   |
| --------------- | ------------------------ | ------------------------------- |
| `jvm.JVM`       | Main JVM interface       | `jvm_instance.find_class()`     |
| `jvm.JNIHelper` | Low-level JNI functions  | `jni.FindClass()`               |
| `jvm.Config`    | Configuration management | `Config.from_pyproject()`       |
| `jvm.JVMLoader` | JVM initialization       | `JVMLoader(config).start()`     |
| `jvm.proxy.*`   | Java object proxies      | `ClassProxy()`, `ObjectProxy()` |

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/t3tra-dev/jvm-pybind.git
cd jvm-pybind

# Initialize environment
./reinstall.sh  # Or manually create a virtual environment
```

### Running Tests

```bash
# Run the example
cd examples/hello
python main.py
```

### Project Structure

```
jvm-pybind/
├── src/jvm/           # Main package
│   ├── __init__.py    # Package initialization
│   ├── jvm.py         # JVM interface
│   ├── jni.py         # JNI bindings
│   ├── loader.py      # JVM loader
│   ├── proxy.py       # Java object proxies
│   ├── config.py      # Configuration management
│   ├── typeconv.py    # Type conversion utilities
│   └── import_hook/   # Python import hook
├── examples/          # Usage examples
└── tests/            # Test suite
```

## Supported Java Types

### Primitive Types

- `boolean` ↔ `bool`
- `int` ↔ `int`
- `long` ↔ `int`
- `float` ↔ `float`
- `double` ↔ `float`
- `String` ↔ `str`

### Complex Types

- Java objects are wrapped in proxy classes
- Arrays and collections (planned)
- Custom classes through reflection

## Performance Considerations

- **JVM Startup**: The JVM is initialized lazily on first Java import
- **Memory Usage**: JNI references are managed automatically
- **Method Calls**: Direct JNI calls for optimal performance
- **ARM64 Optimization**: Special optimizations for Apple Silicon

## Troubleshooting

### Common Issues

1. **Java not found**: Ensure Java is installed and `JAVA_HOME` is set
2. **ClassNotFoundException**: Check your classpath configuration
3. **Memory errors**: Verify adequate heap space for your application

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from java.lang import System  # Will show debug output
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python's ctypes for JNI integration
- Inspired by JPype and similar Java-Python bridge projects
- Special thanks to the Python and Java communities

## Roadmap

### High Priority

- [ ] **Custom Java class import support** - Enable `from mypkg import MyClass` syntax for custom classes
- [ ] **Enhanced type conversion** - Support for more Java types (arrays, collections, etc.)
- [ ] **Comprehensive test suite** - Full test coverage for all features

### Medium Priority

- [ ] **Maven dependency resolution** - Automatic downloading and management of Maven dependencies
- [ ] **Java collection support** - Native Python integration with Java Lists, Maps, etc.
- [ ] **Performance optimizations** - Method call optimization and caching

### Low Priority

- [ ] **Callback support** - Enable Java code to call Python functions
- [ ] **Advanced debugging tools** - Better error messages and debugging capabilities
- [ ] **IDE integration** - Type hints and autocompletion for Java classes
