from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sapl.backends import (
    AssemblyEmitter,
    BytecodeCompiler,
    CLanguageEmitter,
    CSharpEmitter,
    CppEmitter,
    GoEmitter,
    JavaEmitter,
    JavaScriptEmitter,
    MachineCodeCompiler,
    PerlEmitter,
    PhpEmitter,
    REmitter,
    RubyEmitter,
    RustEmitter,
    SqlEmitter,
    Transpiler,
    VirtualMachine,
)
from sapl.lexer import lex
from sapl.parser import parse


def compile_source(source: str):
    tokens = lex(source)
    program = parse(tokens)
    return program


def test_bytecode_and_virtual_machine_execution():
    program = compile_source("\n".join(["value = 2", "value = value + 3"]))
    bytecode = BytecodeCompiler().compile(program)
    vm = VirtualMachine()
    vm.run(bytecode)
    assert vm.globals["value"] == 5


def test_machine_code_rendering_and_transpiler():
    program = compile_source("\n".join(["value = 2", "value = value * 4", "value"]))
    machine = MachineCodeCompiler().compile(program)
    rendered = machine.render()
    assert "STORE_NAME" in rendered
    transpiled = Transpiler().transpile(program)
    assert "value = (value * 4)" in transpiled


def test_additional_emitters_generate_expected_headers():
    program = compile_source(
        "\n".join(
            [
                "value = 1",
                "DEF combine(item):",
                "    RETURN item",
            ]
        )
    )
    assembly = AssemblyEmitter().emit(program)
    assert "section .text" in assembly
    assert "combine:" in assembly
    c_output = CLanguageEmitter().emit(program)
    assert "int main" in c_output
    cpp_output = CppEmitter().emit(program)
    assert "using namespace std;" in cpp_output
    csharp_output = CSharpEmitter().emit(program)
    assert "public static class SaplProgram" in csharp_output
    php_output = PhpEmitter().emit(program)
    assert "<?php" in php_output
    sql_output = SqlEmitter().emit(program)
    assert "BEGIN;" in sql_output
    go_output = GoEmitter().emit(program)
    assert "package main" in go_output
    java_output = JavaEmitter().emit(program)
    assert "public class SaplProgram" in java_output
    js_output = JavaScriptEmitter().emit(program)
    assert "function main()" in js_output
    perl_output = PerlEmitter().emit(program)
    assert "#!/usr/bin/env perl" in perl_output
    rust_output = RustEmitter().emit(program)
    assert "fn main()" in rust_output
    ruby_output = RubyEmitter().emit(program)
    assert "def main" in ruby_output
    r_output = REmitter().emit(program)
    assert "sapl_main <- function()" in r_output
