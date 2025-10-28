from sapl.advanced_compiler import AdvancedCompiler


def test_advanced_compiler_collects_metadata():
    source = """
IMPORT math

DEF greet(name="world"):
    "Generate a greeting."
    RETURN "hi " + name

CLASS Greeter:
    "Wrapper class around greet."
    DEF __init__(self, name):
        self.name = name

    DEF speak(self):
        RETURN greet(self.name)
"""
    compiler = AdvancedCompiler()
    artifact = compiler.compile_source(source, target="python", module_name="demo")
    metadata = artifact.metadata
    assert metadata["module"] == "demo"
    assert "math" in metadata["imports"]
    func = metadata["functions"][0]
    assert func["name"] == "greet"
    assert func["parameters"][0]["default"] == "'world'"
    cls = metadata["classes"][0]
    assert cls["name"] == "Greeter"
    assert any(method["name"] == "speak" for method in cls["methods"])
    serialised = artifact.serialise()
    assert serialised["target"] == "python"
    assert "payload" in serialised


def test_advanced_compiler_supports_additional_targets():
    source = "value = 42"
    compiler = AdvancedCompiler()
    assembly_artifact = compiler.compile_source(source, target="assembly")
    assert "section .text" in assembly_artifact.payload
    c_artifact = compiler.compile_source(source, target="c")
    assert "int main" in c_artifact.payload
    php_artifact = compiler.compile_source(source, target="php")
    assert "<?php" in php_artifact.payload
