"""Alternative execution backends for SAPL programs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from . import nodes


@dataclass
class MachineInstruction:
    opcode: str
    operands: Tuple[Any, ...] = ()

    def render(self) -> str:
        if not self.operands:
            return self.opcode
        operand_text = ", ".join(repr(item) for item in self.operands)
        return f"{self.opcode} {operand_text}"


@dataclass
class MachineCodeProgram:
    instructions: List[MachineInstruction]

    def render(self) -> str:
        return "\n".join(instruction.render() for instruction in self.instructions)


@dataclass
class BytecodeProgram:
    instructions: List[Tuple[str, Any]]
    constants: List[Any]


class MachineCodeCompiler:
    """Compile high level statements into pseudo machine code."""

    def compile(self, program: nodes.Program) -> MachineCodeProgram:
        bytecode = BytecodeCompiler().compile(program)
        instructions = []
        for opcode, operand in bytecode.instructions:
            if isinstance(operand, tuple):
                operands = operand
            elif operand is None:
                operands = ()
            else:
                operands = (operand,)
            instructions.append(MachineInstruction(opcode, operands))
        return MachineCodeProgram(instructions)


class BytecodeCompiler:
    """Compile SAPL statements into a small stack-based bytecode."""

    def __init__(self) -> None:
        self.constants: List[Any] = []
        self.instructions: List[Tuple[str, Any]] = []

    def compile(self, program: nodes.Program) -> BytecodeProgram:
        for statement in program.statements:
            self._compile_statement(statement)
        return BytecodeProgram(self.instructions, self.constants)

    def _compile_statement(self, statement: nodes.Statement) -> None:
        if isinstance(statement, nodes.AssignmentStatement) and len(statement.targets) == 1 and isinstance(statement.targets[0], nodes.Identifier):
            self._compile_expression(statement.value)
            self.instructions.append(("STORE_NAME", statement.targets[0].name))
            return
        if isinstance(statement, nodes.ExpressionStatement):
            self._compile_expression(statement.expression)
            self.instructions.append(("POP_TOP", None))
            return
        if isinstance(statement, nodes.ReturnStatement):
            if statement.value is not None:
                self._compile_expression(statement.value)
            else:
                self.instructions.append(("LOAD_CONST", self._store_constant(None)))
            self.instructions.append(("RETURN_VALUE", None))
            return
        # fall back to no-op for unsupported statements

    def _compile_expression(self, expression: nodes.Expression) -> None:
        if isinstance(expression, (int, float, str, bool, type(None))):
            self.instructions.append(("LOAD_CONST", self._store_constant(expression)))
            return
        if isinstance(expression, nodes.Identifier):
            self.instructions.append(("LOAD_NAME", expression.name))
            return
        if isinstance(expression, nodes.BinaryExpression):
            self._compile_expression(expression.left)
            self._compile_expression(expression.right)
            mapping = {
                "PLUS": "BINARY_ADD",
                "MINUS": "BINARY_SUB",
                "STAR": "BINARY_MUL",
                "SLASH": "BINARY_DIV",
                "DBLSLASH": "BINARY_FLOORDIV",
                "PERCENT": "BINARY_MOD",
                "POWER": "BINARY_POW",
            }
            opcode = mapping.get(expression.operator)
            if opcode is None:
                raise ValueError(f"Unsupported operator {expression.operator} for bytecode compilation")
            self.instructions.append((opcode, None))
            return
        if isinstance(expression, nodes.CallExpression):
            self._compile_expression(expression.function)
            for arg in expression.args:
                self._compile_expression(arg)
            if expression.kwargs:
                raise ValueError("Keyword arguments are not supported in bytecode compilation")
            self.instructions.append(("CALL_FUNCTION", len(expression.args)))
            return
        raise ValueError(f"Unsupported expression type {type(expression)!r}")

    def _store_constant(self, value: Any) -> int:
        try:
            index = self.constants.index(value)
        except ValueError:
            self.constants.append(value)
            index = len(self.constants) - 1
        return index


class VirtualMachine:
    """Execute bytecode produced by :class:`BytecodeCompiler`."""

    def __init__(self) -> None:
        self.stack: List[Any] = []
        self.globals: Dict[str, Any] = {}

    def run(self, program: BytecodeProgram) -> Any:
        self.stack.clear()
        ip = 0
        instructions = program.instructions
        constants = program.constants
        while ip < len(instructions):
            opcode, operand = instructions[ip]
            if opcode == "LOAD_CONST":
                self.stack.append(constants[operand])
            elif opcode == "STORE_NAME":
                value = self.stack.pop()
                self.globals[operand] = value
            elif opcode == "LOAD_NAME":
                self.stack.append(self.globals[operand])
            elif opcode == "BINARY_ADD":
                right, left = self.stack.pop(), self.stack.pop()
                self.stack.append(left + right)
            elif opcode == "BINARY_SUB":
                right, left = self.stack.pop(), self.stack.pop()
                self.stack.append(left - right)
            elif opcode == "BINARY_MUL":
                right, left = self.stack.pop(), self.stack.pop()
                self.stack.append(left * right)
            elif opcode == "BINARY_DIV":
                right, left = self.stack.pop(), self.stack.pop()
                self.stack.append(left / right)
            elif opcode == "BINARY_FLOORDIV":
                right, left = self.stack.pop(), self.stack.pop()
                self.stack.append(left // right)
            elif opcode == "BINARY_MOD":
                right, left = self.stack.pop(), self.stack.pop()
                self.stack.append(left % right)
            elif opcode == "BINARY_POW":
                right, left = self.stack.pop(), self.stack.pop()
                self.stack.append(left ** right)
            elif opcode == "CALL_FUNCTION":
                args = [self.stack.pop() for _ in range(operand)][::-1]
                func = self.stack.pop()
                self.stack.append(func(*args))
            elif opcode == "POP_TOP":
                if self.stack:
                    self.stack.pop()
            elif opcode == "RETURN_VALUE":
                return self.stack.pop() if self.stack else None
            else:
                raise ValueError(f"Unknown opcode {opcode}")
            ip += 1
        return self.stack[-1] if self.stack else None


class Transpiler:
    """Translate SAPL AST nodes into Python source code."""

    INDENT = "    "

    def transpile(self, program: nodes.Program) -> str:
        self._needs_async_helper = False
        self._async_stack: List[bool] = [False]
        lines: List[str] = []
        for statement in program.statements:
            self._emit_statement(statement, 0, lines)
        header: List[str] = ["# Auto-generated from SAPL"]
        if self._needs_async_helper:
            header.extend(
                [
                    "import asyncio",
                    "import inspect",
                    "",
                    "def __sapl_await__(value):",
                    "    if inspect.isawaitable(value):",
                    "        try:",
                    "            return asyncio.run(value)",
                    "        except RuntimeError:",
                    "            loop = asyncio.new_event_loop()",
                    "            previous = None",
                    "            try:",
                    "                try:",
                    "                    previous = asyncio.get_event_loop()",
                    "                except RuntimeError:",
                    "                    previous = None",
                    "                asyncio.set_event_loop(loop)",
                    "                return loop.run_until_complete(value)",
                    "            finally:",
                    "                loop.close()",
                    "                asyncio.set_event_loop(previous)",
                    "    return value",
                    "",
                ]
            )
        return "\n".join(header + lines) + "\n"

    def _emit_statement(self, statement: nodes.Statement, indent: int, lines: List[str]) -> None:
        prefix = self.INDENT * indent
        if isinstance(statement, nodes.SetStatement):
            lines.append(f"{prefix}{statement.name} = {self._emit_expression(statement.value)}")
            return
        if isinstance(statement, nodes.AssignmentStatement) and len(statement.targets) == 1 and isinstance(statement.targets[0], nodes.Identifier):
            lines.append(f"{prefix}{statement.targets[0].name} = {self._emit_expression(statement.value)}")
            return
        if isinstance(statement, nodes.ExpressionStatement):
            lines.append(f"{prefix}{self._emit_expression(statement.expression)}")
            return
        if isinstance(statement, nodes.TaskStatement):
            lines.append(f"{prefix}# TASK {statement.name}")
            if statement.docstring:
                lines.append(f"{prefix}{self.INDENT}# Doc: {statement.docstring}")
            for inner in statement.body:
                self._emit_statement(inner, indent + 1, lines)
            return
        if isinstance(statement, nodes.FunctionDefinition):
            params = []
            for param in statement.parameters:
                if param.default is not None:
                    params.append(f"{param.name}={self._emit_expression(param.default)}")
                else:
                    params.append(param.name)
            keyword = "async def" if statement.is_async else "def"
            lines.append(f"{prefix}{keyword} {statement.name}({', '.join(params)}):")
            if statement.docstring:
                lines.append(f"{prefix}{self.INDENT}{repr(statement.docstring)}")
            if not statement.body:
                lines.append(f"{prefix}{self.INDENT}pass")
            self._async_stack.append(statement.is_async)
            for inner in statement.body:
                self._emit_statement(inner, indent + 1, lines)
            self._async_stack.pop()
            return
        if isinstance(statement, nodes.ReturnStatement):
            if statement.value is None:
                lines.append(f"{prefix}return")
            else:
                lines.append(f"{prefix}return {self._emit_expression(statement.value)}")
            return
        if isinstance(statement, nodes.IfStatement):
            lines.append(f"{prefix}if {self._emit_expression(statement.condition)}:")
            for inner in statement.body:
                self._emit_statement(inner, indent + 1, lines)
            for cond, body in statement.elif_blocks:
                lines.append(f"{prefix}elif {self._emit_expression(cond)}:")
                for inner in body:
                    self._emit_statement(inner, indent + 1, lines)
            if statement.else_body:
                lines.append(f"{prefix}else:")
                for inner in statement.else_body:
                    self._emit_statement(inner, indent + 1, lines)
            return
        if isinstance(statement, nodes.ForStatement):
            lines.append(f"{prefix}for {statement.iterator} in {self._emit_expression(statement.iterable)}:")
            for inner in statement.body:
                self._emit_statement(inner, indent + 1, lines)
            return
        if isinstance(statement, nodes.WhileStatement):
            lines.append(f"{prefix}while {self._emit_expression(statement.condition)}:")
            for inner in statement.body:
                self._emit_statement(inner, indent + 1, lines)
            if statement.else_body:
                lines.append(f"{prefix}else:")
                for inner in statement.else_body:
                    self._emit_statement(inner, indent + 1, lines)
            return
        if isinstance(statement, nodes.NoteStatement):
            lines.append(f"{prefix}print({self._emit_expression(statement.message)})")
            return
        if isinstance(statement, nodes.InputStatement):
            prompt = "" if statement.prompt is None else self._emit_expression(statement.prompt)
            call = f"input({prompt})" if prompt else "input()"
            if statement.target:
                lines.append(f"{prefix}{statement.target} = {call}")
            else:
                lines.append(f"{prefix}{call}")
            return
        if isinstance(statement, nodes.OutputStatement):
            lines.append(f"{prefix}print({self._emit_expression(statement.value)})")
            return
        lines.append(f"{prefix}# Unsupported statement: {type(statement).__name__}")

    def _emit_expression(self, expression: nodes.Expression) -> str:
        if isinstance(expression, (int, float)):
            return repr(expression)
        if isinstance(expression, str):
            return repr(expression)
        if expression is None:
            return "None"
        if isinstance(expression, nodes.Identifier):
            return expression.name
        if isinstance(expression, nodes.ListExpression):
            return "[" + ", ".join(self._emit_expression(elem) for elem in expression.elements) + "]"
        if isinstance(expression, nodes.TupleExpression):
            inner = ", ".join(self._emit_expression(elem) for elem in expression.elements)
            return f"({inner})"
        if isinstance(expression, nodes.DictExpression):
            items = ", ".join(f"{self._emit_expression(key)}: {self._emit_expression(value)}" for key, value in expression.entries)
            return "{" + items + "}"
        if isinstance(expression, nodes.SetExpression):
            return "{" + ", ".join(self._emit_expression(elem) for elem in expression.elements) + "}"
        if isinstance(expression, nodes.ListComprehension):
            clause = f"[{self._emit_expression(expression.expression)} for {expression.iterator} in {self._emit_expression(expression.iterable)}"
            if expression.condition is not None:
                clause += f" if {self._emit_expression(expression.condition)}"
            clause += "]"
            return clause
        if isinstance(expression, nodes.BinaryExpression):
            mapping = {
                "PLUS": "+",
                "MINUS": "-",
                "STAR": "*",
                "SLASH": "/",
                "DBLSLASH": "//",
                "PERCENT": "%",
                "POWER": "**",
            }
            op = mapping.get(expression.operator, expression.operator.lower())
            return f"({self._emit_expression(expression.left)} {op} {self._emit_expression(expression.right)})"
        if isinstance(expression, nodes.CallExpression):
            args = ", ".join(self._emit_expression(arg) for arg in expression.args)
            kwargs = ", ".join(f"{key}={self._emit_expression(value)}" for key, value in expression.kwargs.items())
            parts = [part for part in [args, kwargs] if part]
            return f"{self._emit_expression(expression.function)}({', '.join(parts)})"
        if isinstance(expression, nodes.AttributeReference):
            return f"{self._emit_expression(expression.value)}.{expression.attribute}"
        if isinstance(expression, nodes.IndexReference):
            return f"{self._emit_expression(expression.value)}[{self._emit_expression(expression.index)}]"
        if isinstance(expression, nodes.UnaryExpression):
            mapping = {"NEGATE": "-", "POSITIVE": "+", "NOT": "not "}
            op = mapping.get(expression.operator, expression.operator.lower())
            return f"({op}{self._emit_expression(expression.operand)})"
        if isinstance(expression, nodes.ConditionalExpression):
            return (
                f"({self._emit_expression(expression.if_true)} if {self._emit_expression(expression.condition)} else "
                f"{self._emit_expression(expression.if_false)})"
            )
        if isinstance(expression, nodes.LambdaExpression):
            params = []
            for param in expression.parameters:
                if param.default is not None:
                    params.append(f"{param.name}={self._emit_expression(param.default)}")
                else:
                    params.append(param.name)
            return f"(lambda {', '.join(params)}: {self._emit_expression(expression.body)})"
        if isinstance(expression, nodes.AwaitExpression):
            if self._async_stack and self._async_stack[-1]:
                return f"await {self._emit_expression(expression.expression)}"
            self._needs_async_helper = True
            return f"__sapl_await__({self._emit_expression(expression.expression)})"
        return repr(expression)


class _ExpressionRenderer:
    """Utility helper to normalise SAPL expressions for other emitters."""

    def __init__(self, *, language: str) -> None:
        self.language = language

    def render(self, expression: nodes.Expression) -> str:
        if isinstance(expression, (int, float)):
            return repr(expression)
        if isinstance(expression, bool):
            if self.language in {"c", "assembly"}:
                return "1" if expression else "0"
            if self.language in {"perl"}:
                return "1" if expression else "0"
            if self.language in {"sql", "r"}:
                return "TRUE" if expression else "FALSE"
            return "true" if expression else "false"
        if expression is None:
            if self.language == "csharp":
                return "null"
            if self.language == "assembly":
                return "0"
            if self.language in {"php", "javascript", "java"}:
                return "null"
            if self.language == "go":
                return "nil"
            if self.language == "perl":
                return "undef"
            if self.language == "rust":
                return "None"
            if self.language == "ruby":
                return "nil"
            if self.language == "r":
                return "NULL"
            return "NULL"
        if isinstance(expression, str):
            return json.dumps(expression)
        if isinstance(expression, nodes.Identifier):
            name = expression.name
            if self.language in {"php", "perl"}:
                return f"${name}"
            return name
        if isinstance(expression, nodes.AttributeReference):
            return f"{self.render(expression.value)}.{expression.attribute}"
        if isinstance(expression, nodes.IndexReference):
            return f"{self.render(expression.value)}[{self.render(expression.index)}]"
        if isinstance(expression, nodes.BinaryExpression):
            op_map = {
                "PLUS": "+",
                "MINUS": "-",
                "STAR": "*",
                "SLASH": "/",
                "DBLSLASH": "/",
                "PERCENT": "%",
                "POWER": "^",
            }
            operator = op_map.get(expression.operator, expression.operator)
            return f"({self.render(expression.left)} {operator} {self.render(expression.right)})"
        if isinstance(expression, nodes.UnaryExpression):
            mapping = {"NOT": "!", "MINUS": "-"}
            operator = mapping.get(expression.operator, expression.operator)
            return f"({operator}{self.render(expression.operand)})"
        if isinstance(expression, nodes.CallExpression):
            function = self.render(expression.function)
            args = ", ".join(self.render(arg) for arg in expression.args)
            if expression.kwargs:
                kwargs = ", ".join(
                    f"{name}={self.render(value)}"
                    for name, value in expression.kwargs.items()
                )
                args = ", ".join(filter(None, [args, kwargs]))
            return f"{function}({args})"
        if isinstance(expression, nodes.ListExpression):
            return "[" + ", ".join(self.render(item) for item in expression.elements) + "]"
        if isinstance(expression, nodes.TupleExpression):
            return "(" + ", ".join(self.render(item) for item in expression.elements) + ")"
        if isinstance(expression, nodes.DictExpression):
            entries = [
                f"{self.render(key)}: {self.render(value)}"
                for key, value in expression.entries
            ]
            return "{" + ", ".join(entries) + "}"
        if isinstance(expression, nodes.SetExpression):
            return "{" + ", ".join(self.render(item) for item in expression.elements) + "}"
        if isinstance(expression, nodes.ListComprehension):
            body = self.render(expression.expression)
            iterable = self.render(expression.iterable)
            condition = (
                f" if {self.render(expression.condition)}"
                if expression.condition is not None
                else ""
            )
            return f"/* comprehension */ ({body} for {expression.iterator} in {iterable}{condition})"
        if isinstance(expression, nodes.ConditionalExpression):
            return (
                f"({self.render(expression.condition)} ? {self.render(expression.if_true)} : "
                f"{self.render(expression.if_false)})"
            )
        if isinstance(expression, nodes.LambdaExpression):
            params = ", ".join(param.name for param in expression.parameters)
            return f"/* lambda */ ({params}) => {self.render(expression.body)}"
        if isinstance(expression, nodes.AwaitExpression):
            return f"await {self.render(expression.expression)}"
        return f"/*{expression.__class__.__name__}*/"


class AssemblyEmitter:
    """Render SAPL programs as pseudo-assembly listings."""

    def __init__(self) -> None:
        self.renderer = _ExpressionRenderer(language="assembly")

    def emit(self, program: nodes.Program) -> str:
        main_lines: List[str] = []
        function_blocks: List[str] = []
        for statement in program.statements:
            if isinstance(statement, nodes.FunctionDefinition):
                function_blocks.append(self._emit_function(statement))
            else:
                main_lines.extend(self._emit_statement(statement))
        lines = [
            "; Auto-generated assembly from SAPL",
            "section .text",
            "global _sapl_main",
            "_sapl_main:",
        ]
        if main_lines:
            lines.extend("    " + line for line in main_lines)
        lines.append("    RET")
        if function_blocks:
            lines.append("")
            lines.extend(function_blocks)
        return "\n".join(lines) + "\n"

    def _emit_function(self, function: nodes.FunctionDefinition) -> str:
        body_lines: List[str] = []
        for statement in function.body:
            body_lines.extend(self._emit_statement(statement))
        if not any(line.startswith("RET") for line in body_lines):
            body_lines.append("RET")
        block = [f"{function.name}:"]
        if function.docstring:
            block.append(f"    ; {function.docstring}")
        if function.is_async:
            block.append("    ; async function")
        block.extend("    " + line for line in body_lines)
        return "\n".join(block)

    def _emit_statement(self, statement: nodes.Statement) -> List[str]:
        if isinstance(statement, nodes.AssignmentStatement) and len(statement.targets) == 1:
            target = statement.targets[0]
            if isinstance(target, nodes.Identifier):
                return [f"MOV {target.name}, {self.renderer.render(statement.value)}"]
        if isinstance(statement, nodes.ReturnStatement):
            value = (
                self.renderer.render(statement.value)
                if statement.value is not None
                else "0"
            )
            return [f"MOV R0, {value}", "RET"]
        if isinstance(statement, nodes.ExpressionStatement):
            return [f"; evaluate {self.renderer.render(statement.expression)}"]
        if isinstance(statement, nodes.TaskStatement):
            return [f"; task {statement.name}"]
        if isinstance(statement, nodes.PayloadStatement):
            return [f"; payload {statement.name} = {self.renderer.render(statement.value)}"]
        if isinstance(statement, nodes.IfStatement):
            lines = [f"; if {self.renderer.render(statement.condition)}"]
            for inner in statement.body:
                lines.extend(";   " + text for text in self._emit_statement(inner))
            for cond, body in statement.elif_blocks:
                lines.append(f"; elif {self.renderer.render(cond)}")
                for inner in body:
                    lines.extend(";   " + text for text in self._emit_statement(inner))
            if statement.else_body:
                lines.append("; else")
                for inner in statement.else_body:
                    lines.extend(";   " + text for text in self._emit_statement(inner))
            lines.append("; end if")
            return lines
        if isinstance(statement, nodes.ForStatement):
            lines = [f"; for {statement.iterator} in {self.renderer.render(statement.iterable)}"]
            for inner in statement.body:
                lines.extend(";   " + text for text in self._emit_statement(inner))
            lines.append("; end for")
            return lines
        return [f"; unsupported {statement.__class__.__name__}"]


class _CLikeEmitterBase:
    """Base class for emitters that target C-family or similar languages."""

    language: str
    header_lines: Sequence[str]
    main_signature: str
    footer_lines: Sequence[str]

    def __init__(self) -> None:
        self.renderer = _ExpressionRenderer(language=self.language)

    # ------------------------------------------------------------------
    def emit(self, program: nodes.Program) -> str:
        functions = [
            statement
            for statement in program.statements
            if isinstance(statement, nodes.FunctionDefinition)
        ]
        others = [
            statement
            for statement in program.statements
            if not isinstance(statement, nodes.FunctionDefinition)
        ]
        lines: List[str] = list(self.header_lines)
        lines.append(self.main_signature)
        lines.append(self._block_open())
        body: List[str] = []
        for statement in others:
            body.extend(self._emit_statement(statement))
        if not any(self._is_return_statement(line) for line in body):
            body.append(self._function_return_default_line())
        lines.extend(self._indent_line(line) for line in body)
        lines.append(self._block_close())
        for function in functions:
            lines.append("")
            lines.extend(self._emit_function(function))
        lines.extend(self.footer_lines)
        return "\n".join(lines).rstrip() + "\n"

    # ------------------------------------------------------------------
    def _emit_statement(self, statement: nodes.Statement) -> List[str]:
        if (
            isinstance(statement, nodes.AssignmentStatement)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], nodes.Identifier)
        ):
            target = self._format_identifier(statement.targets[0].name)
            value = self.renderer.render(statement.value)
            return [self._format_assignment_line(target, value)]
        if isinstance(statement, nodes.ExpressionStatement):
            expr = self.renderer.render(statement.expression)
            return [self._format_expression_line(expr)]
        if isinstance(statement, nodes.ReturnStatement):
            if statement.value is not None:
                value = self.renderer.render(statement.value)
            else:
                value = self._default_return_value()
            return [self._format_return_line(value)]
        if isinstance(statement, nodes.TaskStatement):
            return [self._format_task_line(statement)]
        if isinstance(statement, nodes.PayloadStatement):
            rendered = self.renderer.render(statement.value)
            return [self._format_payload_line(statement.name, rendered)]
        if isinstance(statement, nodes.IfStatement):
            lines = [self._format_if_line(self.renderer.render(statement.condition))]
            for inner in statement.body:
                for emitted in self._emit_statement(inner):
                    lines.append(self._indent_line(emitted))
            for cond, body in statement.elif_blocks:
                lines.append(self._format_elif_line(self.renderer.render(cond)))
                for inner in body:
                    for emitted in self._emit_statement(inner):
                        lines.append(self._indent_line(emitted))
            if statement.else_body:
                lines.append(self._format_else_line())
                for inner in statement.else_body:
                    for emitted in self._emit_statement(inner):
                        lines.append(self._indent_line(emitted))
            lines.append(self._block_close())
            return lines
        if isinstance(statement, nodes.ForStatement):
            iterable = self.renderer.render(statement.iterable)
            iterator = self._format_identifier(statement.iterator)
            lines = [self._format_for_line(iterator, iterable)]
            for inner in statement.body:
                for emitted in self._emit_statement(inner):
                    lines.append(self._indent_line(emitted))
            lines.append(self._block_close())
            return lines
        return [self._format_comment_line(f"unsupported {statement.__class__.__name__}")]

    def _emit_function(self, function: nodes.FunctionDefinition) -> List[str]:
        params = [self._format_parameter(param) for param in function.parameters]
        signature = self._format_signature(function.name, params)
        lines = [signature, self._block_open()]
        if function.docstring:
            lines.append(self._indent_line(self._format_comment_line(function.docstring)))
        if function.is_async:
            lines.append(self._indent_line(self._format_comment_line("async function")))
        body: List[str] = []
        for statement in function.body:
            body.extend(self._emit_statement(statement))
        if not any(self._is_return_statement(line) for line in body):
            body.append(self._function_return_default_line())
        lines.extend(self._indent_line(line) for line in body)
        lines.append(self._block_close())
        return lines

    # ------------------------------------------------------------------
    def _indent_line(self, line: str) -> str:
        return "    " + line

    def _is_return_statement(self, line: str) -> bool:
        return line.strip().startswith("return")

    def _block_open(self) -> str:
        return "{"

    def _block_close(self) -> str:
        return "}"

    def _format_identifier(self, name: str) -> str:
        return name

    def _format_assignment_line(self, name: str, value: str) -> str:
        return f"auto {name} = {value};"

    def _format_expression_line(self, expression: str) -> str:
        return f"/* expression {expression} */"

    def _default_return_value(self) -> str:
        return "0"

    def _format_return_line(self, value: str) -> str:
        return f"return {value};"

    def _function_return_default_line(self) -> str:
        return "return 0;"

    def _format_comment_line(self, text: str) -> str:
        return f"// {text}"

    def _format_task_line(self, statement: nodes.TaskStatement) -> str:
        note = f"task {statement.name}"
        if statement.docstring:
            note += f" : {statement.docstring}"
        return self._format_comment_line(note)

    def _format_payload_line(self, name: str, value: str) -> str:
        return self._format_comment_line(f"payload {name} = {value}")

    def _format_if_line(self, condition: str) -> str:
        return f"if {condition} {self._block_open()}"

    def _format_elif_line(self, condition: str) -> str:
        return f"}} else if {condition} {self._block_open()}"

    def _format_else_line(self) -> str:
        return f"}} else {self._block_open()}"

    def _format_for_line(self, iterator: str, iterable: str) -> str:
        return f"for (auto {iterator} : {iterable}) {self._block_open()}"

    def _format_parameter(self, parameter: nodes.Parameter) -> str:
        descriptor = f"auto {parameter.name}"
        if parameter.default is not None:
            descriptor += f" /*= {self.renderer.render(parameter.default)}*/"
        return descriptor

    # ------------------------------------------------------------------
    def _format_signature(self, name: str, params: List[str]) -> str:
        raise NotImplementedError


class CLanguageEmitter(_CLikeEmitterBase):
    """Emit C-style pseudo code from SAPL programs."""

    language = "c"
    header_lines = ("/* Auto-generated from SAPL */", "#include <stdio.h>", "")
    main_signature = "int main(void)"
    footer_lines: Sequence[str] = ("",)

    def _format_signature(self, name: str, params: List[str]) -> str:
        joined = ", ".join(params) or "void"
        return f"static int {name}({joined})"


class CppEmitter(_CLikeEmitterBase):
    """Emit C++-style pseudo code from SAPL programs."""

    language = "cpp"
    header_lines = (
        "// Auto-generated from SAPL",
        "#include <iostream>",
        "using namespace std;",
        "",
    )
    main_signature = "int main()"
    footer_lines: Sequence[str] = ("",)

    def _format_signature(self, name: str, params: List[str]) -> str:
        joined = ", ".join(params) or "void"
        return f"auto {name}({joined}) -> int"


class CSharpEmitter(_CLikeEmitterBase):
    """Emit C# pseudo code from SAPL programs."""

    language = "csharp"
    header_lines = ("// Auto-generated from SAPL", "using System;", "public static class SaplProgram", "{")
    main_signature = "public static int Main(string[] args)"
    footer_lines: Sequence[str] = ("}",)

    def emit(self, program: nodes.Program) -> str:  # type: ignore[override]
        functions = [
            statement
            for statement in program.statements
            if isinstance(statement, nodes.FunctionDefinition)
        ]
        others = [
            statement
            for statement in program.statements
            if not isinstance(statement, nodes.FunctionDefinition)
        ]
        lines = list(self.header_lines)
        lines.append("    " + self.main_signature)
        lines.append("    {")
        body: List[str] = []
        for statement in others:
            body.extend(self._emit_statement(statement))
        if not any(line.strip().startswith("return") for line in body):
            body.append("return 0;")
        lines.extend("        " + line for line in body)
        lines.append("    }")
        for function in functions:
            lines.append("")
            for text in self._emit_function(function):
                lines.append("    " + text)
        lines.append(self.footer_lines[0])
        return "\n".join(lines).rstrip() + "\n"

    def _format_signature(self, name: str, params: List[str]) -> str:
        joined = ", ".join(params)
        return f"public static int {name}({joined})"


class PhpEmitter(_CLikeEmitterBase):
    """Emit PHP-style pseudo code from SAPL programs."""

    language = "php"
    header_lines = ("<?php", "// Auto-generated from SAPL", "")
    main_signature = "function sapl_main()"
    footer_lines: Sequence[str] = ("",)

    def _format_signature(self, name: str, params: List[str]) -> str:
        return f"function {name}({', '.join(params)})"

    def _format_identifier(self, name: str) -> str:
        return f"${name}"

    def _format_assignment_line(self, name: str, value: str) -> str:
        return f"{name} = {value};"

    def _format_expression_line(self, expression: str) -> str:
        return f"// expression {expression}"

    def _default_return_value(self) -> str:
        return "null"

    def _format_return_line(self, value: str) -> str:
        return f"return {value};"

    def _function_return_default_line(self) -> str:
        return "return null;"

    def _format_comment_line(self, text: str) -> str:
        return f"// {text}"

    def _format_if_line(self, condition: str) -> str:
        return f"if ({condition}) {self._block_open()}"

    def _format_elif_line(self, condition: str) -> str:
        return f"}} elseif ({condition}) {self._block_open()}"

    def _format_for_line(self, iterator: str, iterable: str) -> str:
        return f"foreach ({iterable} as {iterator}) {self._block_open()}"

    def _format_parameter(self, parameter: nodes.Parameter) -> str:
        descriptor = f"${parameter.name}"
        if parameter.default is not None:
            descriptor += f" = {self.renderer.render(parameter.default)}"
        return descriptor


class SqlEmitter:
    """Emit SQL-flavoured scripts from SAPL programs."""

    def __init__(self) -> None:
        self.renderer = _ExpressionRenderer(language="sql")

    def emit(self, program: nodes.Program) -> str:
        lines: List[str] = ["-- Auto-generated from SAPL", "BEGIN;"]
        for statement in program.statements:
            lines.extend(self._emit_statement(statement))
        lines.append("COMMIT;")
        return "\n".join(lines).rstrip() + "\n"

    def _emit_statement(self, statement: nodes.Statement) -> List[str]:
        if (
            isinstance(statement, nodes.AssignmentStatement)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], nodes.Identifier)
        ):
            target = statement.targets[0].name
            value = self.renderer.render(statement.value)
            return [f"SET {target} = {value};"]
        if isinstance(statement, nodes.ExpressionStatement):
            expr = self.renderer.render(statement.expression)
            return [f"-- expression {expr}"]
        if isinstance(statement, nodes.ReturnStatement):
            if statement.value is not None:
                value = self.renderer.render(statement.value)
            else:
                value = "NULL"
            return [f"SELECT {value} AS result;"]
        if isinstance(statement, nodes.TaskStatement):
            note = f"task {statement.name}"
            if statement.docstring:
                note += f" : {statement.docstring}"
            return [f"-- {note}"]
        if isinstance(statement, nodes.PayloadStatement):
            rendered = self.renderer.render(statement.value)
            return [f"-- payload {statement.name} = {rendered}"]
        if isinstance(statement, nodes.IfStatement):
            condition = self.renderer.render(statement.condition)
            lines = [f"-- if {condition}"]
            for inner in statement.body:
                for emitted in self._emit_statement(inner):
                    lines.append(f"--   {emitted}")
            for cond, body in statement.elif_blocks:
                alt = self.renderer.render(cond)
                lines.append(f"-- elif {alt}")
                for inner in body:
                    for emitted in self._emit_statement(inner):
                        lines.append(f"--   {emitted}")
            if statement.else_body:
                lines.append("-- else")
                for inner in statement.else_body:
                    for emitted in self._emit_statement(inner):
                        lines.append(f"--   {emitted}")
            lines.append("-- end if")
            return lines
        if isinstance(statement, nodes.ForStatement):
            iterable = self.renderer.render(statement.iterable)
            iterator = statement.iterator
            lines = [f"-- for {iterator} in {iterable}"]
            for inner in statement.body:
                for emitted in self._emit_statement(inner):
                    lines.append(f"--   {emitted}")
            lines.append("-- end for")
            return lines
        return [f"-- unsupported {statement.__class__.__name__}"]


class GoEmitter(_CLikeEmitterBase):
    """Emit Go-style pseudo code from SAPL programs."""

    language = "go"
    header_lines = ("// Auto-generated from SAPL", "package main", "", "import \"fmt\"", "")
    main_signature = "func main()"
    footer_lines: Sequence[str] = ("",)

    def _format_signature(self, name: str, params: List[str]) -> str:
        return f"func {name}({', '.join(params)})"

    def _format_assignment_line(self, name: str, value: str) -> str:
        return f"var {name} = {value}"

    def _format_expression_line(self, expression: str) -> str:
        return f"// expression {expression}"

    def _format_return_line(self, value: str) -> str:
        return f"return {value}"

    def _function_return_default_line(self) -> str:
        return "return 0"

    def _format_comment_line(self, text: str) -> str:
        return f"// {text}"

    def _format_for_line(self, iterator: str, iterable: str) -> str:
        return f"for _, {iterator} := range {iterable} {self._block_open()}"

    def _format_parameter(self, parameter: nodes.Parameter) -> str:
        descriptor = f"{parameter.name} any"
        if parameter.default is not None:
            descriptor += f" /* default {self.renderer.render(parameter.default)} */"
        return descriptor


class JavaEmitter(_CLikeEmitterBase):
    """Emit Java-style pseudo code from SAPL programs."""

    language = "java"
    header_lines = ("// Auto-generated from SAPL", "public class SaplProgram", "{")
    main_signature = "public static int main(String[] args)"
    footer_lines: Sequence[str] = ("}",)

    def emit(self, program: nodes.Program) -> str:  # type: ignore[override]
        functions = [
            statement
            for statement in program.statements
            if isinstance(statement, nodes.FunctionDefinition)
        ]
        others = [
            statement
            for statement in program.statements
            if not isinstance(statement, nodes.FunctionDefinition)
        ]
        lines: List[str] = list(self.header_lines)
        lines.append("    " + self.main_signature)
        lines.append("    " + self._block_open())
        body: List[str] = []
        for statement in others:
            body.extend(self._emit_statement(statement))
        if not any(self._is_return_statement(line) for line in body):
            body.append(self._function_return_default_line())
        lines.extend("        " + line for line in body)
        lines.append("    " + self._block_close())
        for function in functions:
            lines.append("")
            rendered = self._emit_function(function)
            lines.extend("    " + line for line in rendered)
        lines.append(self.footer_lines[0])
        return "\n".join(lines).rstrip() + "\n"

    def _format_signature(self, name: str, params: List[str]) -> str:
        return f"public static int {name}({', '.join(params)})"

    def _format_assignment_line(self, name: str, value: str) -> str:
        return f"var {name} = {value};"

    def _format_expression_line(self, expression: str) -> str:
        return f"/* expression {expression} */"

    def _format_for_line(self, iterator: str, iterable: str) -> str:
        return f"for (var {iterator} : {iterable}) {self._block_open()}"

    def _format_parameter(self, parameter: nodes.Parameter) -> str:
        descriptor = f"var {parameter.name}"
        if parameter.default is not None:
            descriptor += f" /*= {self.renderer.render(parameter.default)}*/"
        return descriptor


class JavaScriptEmitter(_CLikeEmitterBase):
    """Emit JavaScript-style pseudo code from SAPL programs."""

    language = "javascript"
    header_lines = ("// Auto-generated from SAPL", "")
    main_signature = "function main()"
    footer_lines: Sequence[str] = ("",)

    def _format_signature(self, name: str, params: List[str]) -> str:
        return f"function {name}({', '.join(params)})"

    def _format_assignment_line(self, name: str, value: str) -> str:
        return f"let {name} = {value};"

    def _format_expression_line(self, expression: str) -> str:
        return f"// expression {expression}"

    def _format_return_line(self, value: str) -> str:
        return f"return {value};"

    def _function_return_default_line(self) -> str:
        return "return 0;"

    def _format_comment_line(self, text: str) -> str:
        return f"// {text}"

    def _format_for_line(self, iterator: str, iterable: str) -> str:
        return f"for (const {iterator} of {iterable}) {self._block_open()}"

    def _format_parameter(self, parameter: nodes.Parameter) -> str:
        descriptor = parameter.name
        if parameter.default is not None:
            descriptor += f" = {self.renderer.render(parameter.default)}"
        return descriptor


class PerlEmitter(_CLikeEmitterBase):
    """Emit Perl-style pseudo code from SAPL programs."""

    language = "perl"
    header_lines = ("#!/usr/bin/env perl", "use strict;", "use warnings;", "")
    main_signature = "sub main"
    footer_lines: Sequence[str] = ("", "main();")

    def _format_signature(self, name: str, params: List[str]) -> str:
        if params:
            param_comment = ", ".join(params)
            return f"sub {name} /* params: {param_comment} */"
        return f"sub {name}"

    def _format_identifier(self, name: str) -> str:
        return f"${name}"

    def _format_assignment_line(self, name: str, value: str) -> str:
        return f"my {name} = {value};"

    def _format_expression_line(self, expression: str) -> str:
        return f"# expression {expression}"

    def _default_return_value(self) -> str:
        return "undef"

    def _format_return_line(self, value: str) -> str:
        return f"return {value};"

    def _function_return_default_line(self) -> str:
        return "return undef;"

    def _format_comment_line(self, text: str) -> str:
        return f"# {text}"

    def _format_if_line(self, condition: str) -> str:
        return f"if ({condition}) {self._block_open()}"

    def _format_elif_line(self, condition: str) -> str:
        return f"}} elsif ({condition}) {self._block_open()}"

    def _format_for_line(self, iterator: str, iterable: str) -> str:
        return f"foreach {iterator} ({iterable}) {self._block_open()}"

    def _format_parameter(self, parameter: nodes.Parameter) -> str:
        descriptor = f"${parameter.name}"
        if parameter.default is not None:
            descriptor += f" = {self.renderer.render(parameter.default)}"
        return descriptor


class RustEmitter(_CLikeEmitterBase):
    """Emit Rust-style pseudo code from SAPL programs."""

    language = "rust"
    header_lines = ("// Auto-generated from SAPL", "")
    main_signature = "fn main()"
    footer_lines: Sequence[str] = ("",)

    def _format_signature(self, name: str, params: List[str]) -> str:
        joined = ", ".join(params)
        return f"fn {name}({joined}) -> i32"

    def _format_assignment_line(self, name: str, value: str) -> str:
        return f"let mut {name} = {value};"

    def _format_expression_line(self, expression: str) -> str:
        return f"// expression {expression}"

    def _format_return_line(self, value: str) -> str:
        return f"return {value};"

    def _function_return_default_line(self) -> str:
        return "return 0;"

    def _format_comment_line(self, text: str) -> str:
        return f"// {text}"

    def _format_for_line(self, iterator: str, iterable: str) -> str:
        return f"for {iterator} in {iterable} {self._block_open()}"

    def _format_parameter(self, parameter: nodes.Parameter) -> str:
        descriptor = f"{parameter.name}: i32"
        if parameter.default is not None:
            descriptor += f" /*= {self.renderer.render(parameter.default)}*/"
        return descriptor


class RubyEmitter:
    """Emit Ruby code from SAPL programs."""

    def __init__(self) -> None:
        self.renderer = _ExpressionRenderer(language="ruby")

    def emit(self, program: nodes.Program) -> str:
        functions: List[nodes.FunctionDefinition] = []
        others: List[nodes.Statement] = []
        for statement in program.statements:
            if isinstance(statement, nodes.FunctionDefinition):
                functions.append(statement)
            else:
                others.append(statement)
        lines: List[str] = ["# Auto-generated from SAPL", "", "def main"]
        body: List[str] = []
        for statement in others:
            body.extend(self._emit_statement(statement))
        if not any(line.strip().startswith("return") for line in body):
            body.append(self._indent("return nil"))
        lines.extend(body)
        lines.append("end")
        for function in functions:
            lines.append("")
            lines.extend(self._emit_function(function))
        return "\n".join(lines).rstrip() + "\n"

    def _emit_statement(self, statement: nodes.Statement, level: int = 1) -> List[str]:
        indent = "  " * level
        if (
            isinstance(statement, nodes.AssignmentStatement)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], nodes.Identifier)
        ):
            name = statement.targets[0].name
            value = self.renderer.render(statement.value)
            return [f"{indent}{name} = {value}"]
        if isinstance(statement, nodes.ExpressionStatement):
            expr = self.renderer.render(statement.expression)
            return [f"{indent}# expression {expr}"]
        if isinstance(statement, nodes.ReturnStatement):
            value = (
                self.renderer.render(statement.value)
                if statement.value is not None
                else "nil"
            )
            return [f"{indent}return {value}"]
        if isinstance(statement, nodes.TaskStatement):
            note = f"task {statement.name}"
            if statement.docstring:
                note += f" : {statement.docstring}"
            return [f"{indent}# {note}"]
        if isinstance(statement, nodes.PayloadStatement):
            rendered = self.renderer.render(statement.value)
            return [f"{indent}# payload {statement.name} = {rendered}"]
        if isinstance(statement, nodes.IfStatement):
            lines = [f"{indent}if {self.renderer.render(statement.condition)}"]
            for inner in statement.body:
                lines.extend(self._emit_statement(inner, level + 1))
            for cond, body in statement.elif_blocks:
                lines.append(f"{indent}elsif {self.renderer.render(cond)}")
                for inner in body:
                    lines.extend(self._emit_statement(inner, level + 1))
            if statement.else_body:
                lines.append(f"{indent}else")
                for inner in statement.else_body:
                    lines.extend(self._emit_statement(inner, level + 1))
            lines.append(f"{indent}end")
            return lines
        if isinstance(statement, nodes.ForStatement):
            lines = [f"{indent}for {statement.iterator} in {self.renderer.render(statement.iterable)}"]
            for inner in statement.body:
                lines.extend(self._emit_statement(inner, level + 1))
            lines.append(f"{indent}end")
            return lines
        return [f"{indent}# unsupported {statement.__class__.__name__}"]

    def _emit_function(self, function: nodes.FunctionDefinition) -> List[str]:
        params = []
        for param in function.parameters:
            descriptor = param.name
            if param.default is not None:
                descriptor += f" = {self.renderer.render(param.default)}"
            params.append(descriptor)
        signature = f"def {function.name}({', '.join(params)})"
        lines = [signature]
        if function.docstring:
            lines.append(self._indent(f"# {function.docstring}"))
        if function.is_async:
            lines.append(self._indent("# async function"))
        body: List[str] = []
        for statement in function.body:
            body.extend(self._emit_statement(statement))
        if not any(line.strip().startswith("return") for line in body):
            body.append(self._indent("return nil"))
        lines.extend(body)
        lines.append("end")
        return lines

    def _indent(self, text: str) -> str:
        return "  " + text


class REmitter(_CLikeEmitterBase):
    """Emit R-language pseudo code from SAPL programs."""

    language = "r"
    header_lines = ("# Auto-generated from SAPL", "")
    main_signature = "sapl_main <- function()"
    footer_lines: Sequence[str] = ("",)

    def _format_signature(self, name: str, params: List[str]) -> str:
        return f"{name} <- function({', '.join(params)})"

    def _format_assignment_line(self, name: str, value: str) -> str:
        return f"{name} <- {value}"

    def _format_expression_line(self, expression: str) -> str:
        return f"# expression {expression}"

    def _default_return_value(self) -> str:
        return "NULL"

    def _format_return_line(self, value: str) -> str:
        return f"return({value})"

    def _function_return_default_line(self) -> str:
        return "return(NULL)"

    def _format_comment_line(self, text: str) -> str:
        return f"# {text}"

    def _format_for_line(self, iterator: str, iterable: str) -> str:
        return f"for ({iterator} in {iterable}) {self._block_open()}"

    def _format_parameter(self, parameter: nodes.Parameter) -> str:
        descriptor = parameter.name
        if parameter.default is not None:
            descriptor += f" = {self.renderer.render(parameter.default)}"
        return descriptor

__all__ = [
    "AssemblyEmitter",
    "BytecodeCompiler",
    "CLanguageEmitter",
    "CSharpEmitter",
    "CppEmitter",
    "GoEmitter",
    "JavaEmitter",
    "JavaScriptEmitter",
    "MachineCodeCompiler",
    "PerlEmitter",
    "PhpEmitter",
    "REmitter",
    "RubyEmitter",
    "RustEmitter",
    "SqlEmitter",
    "Transpiler",
    "VirtualMachine",
]
