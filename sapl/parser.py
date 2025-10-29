"""Parser for the extended SAPL language."""

from __future__ import annotations

from typing import List, Optional

from .errors import ParseError
from .lexer import BOOL_KEYWORDS, Token
from . import nodes


BINARY_PRECEDENCE = {
    "OR": 1,
    "AND": 2,
    "EQ": 3,
    "NEQ": 3,
    "LT": 4,
    "LTE": 4,
    "GT": 4,
    "GTE": 4,
    "IN": 4,
    "PLUS": 5,
    "MINUS": 5,
    "STAR": 6,
    "SLASH": 6,
    "DBLSLASH": 6,
    "PERCENT": 6,
    "POWER": 7,
}

RIGHT_ASSOCIATIVE = {"POWER"}


class Parser:
    """Recursive descent parser producing an AST from tokens."""

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.position = 0

    # Entry point ------------------------------------------------------

    def parse(self) -> nodes.Program:
        statements: List[nodes.Statement] = []
        self._skip_layout()
        while not self._check("EOF"):
            if self._check("DEDENT"):
                self._advance()
                continue
            statements.append(self._statement())
            self._skip_layout()
        return nodes.Program(statements)

    # Layout helpers ---------------------------------------------------

    def _skip_layout(self) -> None:
        while True:
            if self._match("NEWLINE"):
                continue
            if self._match("COMMENT"):
                continue
            break

    # Statement parsing ------------------------------------------------

    def _statement(self) -> nodes.Statement:
        token = self._peek()
        if token.type == "SET":
            return self._parse_set()
        if token.type == "TARGET":
            return self._parse_target()
        if token.type == "SCOPE":
            return self._parse_scope()
        if token.type == "PAYLOAD":
            return self._parse_payload()
        if token.type == "EMBED":
            return self._parse_embed()
        if token.type == "TASK":
            return self._parse_task()
        if token.type == "PORTSCAN":
            return self._parse_portscan()
        if token.type == "HTTP":
            return self._parse_http()
        if token.type == "FUZZ":
            return self._parse_fuzz()
        if token.type == "NOTE":
            return self._parse_note()
        if token.type == "FINDING":
            return self._parse_finding()
        if token.type == "RUN":
            return self._parse_run()
        if token.type == "REPORT":
            return self._parse_report()
        if token.type == "INPUT":
            return self._parse_input()
        if token.type == "OUTPUT":
            return self._parse_output()
        if token.type == "FOR":
            return self._parse_for()
        if token.type == "IF":
            return self._parse_if()
        if token.type == "WHILE":
            return self._parse_while()
        if token.type == "BREAK":
            line = token.line
            self._advance()
            return nodes.BreakStatement(line)
        if token.type == "CONTINUE":
            line = token.line
            self._advance()
            return nodes.ContinueStatement(line)
        if token.type == "PASS":
            line = token.line
            self._advance()
            return nodes.PassStatement(line)
        if token.type == "RETURN":
            return self._parse_return()
        if token.type == "DEF":
            return self._parse_function()
        if token.type == "ASYNC":
            return self._parse_async()
        if token.type == "CLASS":
            return self._parse_class()
        if token.type == "WITH":
            return self._parse_with()
        if token.type == "TRY":
            return self._parse_try()
        if token.type == "RAISE":
            return self._parse_raise()
        if token.type == "IMPORT":
            return self._parse_import()
        if token.type == "FROM":
            return self._parse_from_import()
        return self._parse_assignment_or_expression()

    def _parse_set(self) -> nodes.SetStatement:
        keyword = self._consume("SET")
        name = self._consume("IDENT", "Expected identifier after SET")
        self._consume("ASSIGN", "Expected '=' after identifier")
        value = self._expression()
        return nodes.SetStatement(name.value, value, keyword.line)

    def _parse_target(self) -> nodes.TargetStatement:
        keyword = self._consume("TARGET")
        value = self._expression()
        return nodes.TargetStatement(value, keyword.line)

    def _parse_scope(self) -> nodes.ScopeStatement:
        keyword = self._consume("SCOPE")
        value = self._expression()
        return nodes.ScopeStatement(value, keyword.line)

    def _parse_payload(self) -> nodes.PayloadStatement:
        keyword = self._consume("PAYLOAD")
        name = self._consume("IDENT", "Expected payload identifier")
        self._consume("ASSIGN", "Expected '=' after payload name")
        value = self._expression()
        return nodes.PayloadStatement(name.value, value, keyword.line)

    def _parse_embed(self) -> nodes.EmbedStatement:
        keyword = self._consume("EMBED")
        language_token = self._advance()
        if language_token.type not in {"IDENT", "STRING"}:
            raise ParseError(language_token.line, language_token.column, "Expected embed language identifier or string")
        language = language_token.value
        if isinstance(language, str):
            language_value = language
        else:
            language_value = str(language)
        name_token = self._consume("IDENT", "Expected identifier after embed language")
        self._consume("ASSIGN", "Expected '=' after embed name")
        content = self._expression()
        metadata = None
        if self._match("USING"):
            metadata = self._expression()
        return nodes.EmbedStatement(language_value, name_token.value, content, keyword.line, metadata)

    def _parse_task(self) -> nodes.TaskStatement:
        keyword = self._consume("TASK")
        name_token = self._consume("STRING", "Expected task name string")
        body, docstring = self._parse_suite_with_docstring()
        return nodes.TaskStatement(name_token.value, body, keyword.line, docstring)

    def _parse_portscan(self) -> nodes.PortScanStatement:
        keyword = self._consume("PORTSCAN")
        ports = self._expression()
        tool = None
        if self._match("TOOL"):
            tool = self._expression()
        return nodes.PortScanStatement(ports, tool, keyword.line)

    def _parse_http(self) -> nodes.HttpRequestStatement:
        keyword = self._consume("HTTP")
        method_token = self._advance()
        if method_token.type not in {"IDENT", "STRING"}:
            raise ParseError(method_token.line, method_token.column, "Expected HTTP method")
        method = method_token.value.upper()
        target = self._expression()
        expect_status = None
        contains = None
        if self._match("EXPECT"):
            expect_token = self._peek()
            if expect_token.type == "NUMBER":
                expect_status = int(float(self._advance().value))
            else:
                raise ParseError(expect_token.line, expect_token.column, "Expected numeric status code")
        if self._match("CONTAINS"):
            contains = self._expression()
        return nodes.HttpRequestStatement(method, target, expect_status, contains, keyword.line)

    def _parse_fuzz(self) -> nodes.FuzzStatement:
        keyword = self._consume("FUZZ")
        resource = self._expression()
        method = None
        payload_name = None
        payloads_expr = None
        while True:
            if self._match("METHOD"):
                method_token = self._consume("IDENT", "Expected method name after METHOD")
                method = method_token.value.upper()
                continue
            if self._match("USING"):
                payload_token = self._consume("IDENT", "Expected payload identifier after USING")
                payload_name = payload_token.value
                continue
            if self._match("WITH"):
                payloads_expr = self._expression()
                continue
            break
        return nodes.FuzzStatement(resource, method, payload_name, payloads_expr, keyword.line)

    def _parse_note(self) -> nodes.NoteStatement:
        keyword = self._consume("NOTE")
        message = self._expression()
        return nodes.NoteStatement(message, keyword.line)

    def _parse_finding(self) -> nodes.FindingStatement:
        keyword = self._consume("FINDING")
        severity_token = self._consume("IDENT", "Expected severity level")
        message = self._expression()
        return nodes.FindingStatement(severity_token.value.upper(), message, keyword.line)

    def _parse_run(self) -> nodes.RunStatement:
        keyword = self._consume("RUN")
        command = self._expression()
        save_as = None
        if self._match("SAVE"):
            self._consume("AS", "Expected AS after SAVE")
            save_token = self._consume("IDENT", "Expected identifier after SAVE AS")
            save_as = save_token.value
        return nodes.RunStatement(command, save_as, keyword.line)

    def _parse_report(self) -> nodes.ReportStatement:
        keyword = self._consume("REPORT")
        destination = self._expression()
        return nodes.ReportStatement(destination, keyword.line)

    def _parse_for(self) -> nodes.ForStatement:
        keyword = self._consume("FOR")
        iterator = self._consume("IDENT", "Expected loop variable name")
        self._consume("IN", "Expected IN in for loop")
        iterable = self._expression()
        body = self._parse_suite()
        return nodes.ForStatement(iterator.value, iterable, body, keyword.line)

    def _parse_if(self) -> nodes.IfStatement:
        keyword = self._consume("IF")
        condition = self._expression()
        body = self._parse_suite()
        elif_blocks: List[tuple[nodes.Expression, List[nodes.Statement]]] = []
        while self._match("ELIF"):
            elif_condition = self._expression()
            elif_body = self._parse_suite()
            elif_blocks.append((elif_condition, elif_body))
        else_body: List[nodes.Statement] = []
        if self._match("ELSE"):
            else_body = self._parse_suite()
        return nodes.IfStatement(condition, body, elif_blocks, else_body, keyword.line)

    def _parse_while(self) -> nodes.WhileStatement:
        keyword = self._consume("WHILE")
        condition = self._expression()
        body = self._parse_suite()
        else_body: List[nodes.Statement] = []
        if self._match("ELSE"):
            else_body = self._parse_suite()
        return nodes.WhileStatement(condition, body, else_body, keyword.line)

    def _parse_return(self) -> nodes.ReturnStatement:
        keyword = self._consume("RETURN")
        if self._check("NEWLINE") or self._check("DEDENT") or self._check("EOF"):
            return nodes.ReturnStatement(None, keyword.line)
        value = self._expression()
        return nodes.ReturnStatement(value, keyword.line)

    def _parse_function(self, *, is_async: bool = False) -> nodes.FunctionDefinition:
        keyword = self._consume("DEF")
        name = self._consume("IDENT", "Expected function name")
        self._consume("LPAREN", "Expected '(' after function name")
        parameters: List[nodes.Parameter] = []
        if not self._check("RPAREN"):
            while True:
                param_name = self._consume("IDENT", "Expected parameter name")
                default = None
                if self._match("ASSIGN"):
                    default = self._expression()
                parameters.append(nodes.Parameter(param_name.value, default))
                if self._match("COMMA"):
                    continue
                break
        self._consume("RPAREN", "Expected closing ')' in parameter list")
        body, docstring = self._parse_suite_with_docstring()
        return nodes.FunctionDefinition(name.value, parameters, body, keyword.line, docstring, is_async)

    def _parse_async(self) -> nodes.Statement:
        keyword = self._consume("ASYNC")
        next_token = self._peek()
        if next_token.type == "DEF":
            return self._parse_function(is_async=True)
        raise ParseError(keyword.line, keyword.column, "ASYNC must prefix DEF")

    def _parse_class(self) -> nodes.ClassDefinition:
        keyword = self._consume("CLASS")
        name = self._consume("IDENT", "Expected class name")
        bases: List[nodes.Expression] = []
        if self._match("LPAREN"):
            if not self._check("RPAREN"):
                while True:
                    bases.append(self._expression())
                    if self._match("COMMA"):
                        continue
                    break
            self._consume("RPAREN", "Expected closing ')' after base list")
        body, docstring = self._parse_suite_with_docstring()
        return nodes.ClassDefinition(name.value, bases, body, keyword.line, docstring)

    def _parse_with(self) -> nodes.WithStatement:
        keyword = self._consume("WITH")
        items: List[nodes.WithItem] = []
        while True:
            context = self._expression()
            alias = None
            if self._match("AS"):
                alias_token = self._consume("IDENT", "Expected identifier after AS")
                alias = alias_token.value
            items.append(nodes.WithItem(context, alias))
            if self._match("COMMA"):
                continue
            break
        body = self._parse_suite()
        return nodes.WithStatement(items, body, keyword.line)

    def _parse_try(self) -> nodes.TryStatement:
        keyword = self._consume("TRY")
        body = self._parse_suite()
        handlers: List[nodes.ExceptHandler] = []
        while self._match("EXCEPT"):
            exception_type = None
            alias = None
            if not self._check("COLON") and not self._check("NEWLINE") and not self._check("INDENT"):
                exception_type = self._expression()
                if self._match("AS"):
                    alias_token = self._consume("IDENT", "Expected identifier after AS")
                    alias = alias_token.value
            handler_body = self._parse_suite()
            handlers.append(nodes.ExceptHandler(exception_type, alias, handler_body))
        else_body: List[nodes.Statement] = []
        finally_body: List[nodes.Statement] = []
        if self._match("ELSE"):
            else_body = self._parse_suite()
        if self._match("FINALLY"):
            finally_body = self._parse_suite()
        if not handlers and not finally_body:
            raise ParseError(keyword.line, keyword.column, "TRY block requires except or finally")
        return nodes.TryStatement(body, handlers, else_body, finally_body, keyword.line)

    def _parse_raise(self) -> nodes.RaiseStatement:
        keyword = self._consume("RAISE")
        if self._check("NEWLINE") or self._check("DEDENT") or self._check("EOF"):
            return nodes.RaiseStatement(None, keyword.line)
        value = self._expression()
        return nodes.RaiseStatement(value, keyword.line)

    def _parse_import(self) -> nodes.ImportStatement:
        keyword = self._consume("IMPORT")
        items: List[nodes.ImportItem] = []
        while True:
            module = self._parse_dotted_name()
            alias = None
            if self._match("AS"):
                alias_token = self._consume("IDENT", "Expected alias name")
                alias = alias_token.value
            items.append(nodes.ImportItem(module, alias))
            if self._match("COMMA"):
                continue
            break
        return nodes.ImportStatement(items, keyword.line)

    def _parse_from_import(self) -> nodes.FromImportStatement:
        keyword = self._consume("FROM")
        module = self._parse_dotted_name()
        self._consume("IMPORT", "Expected IMPORT after module path")
        items: List[nodes.FromImportItem] = []
        if self._match("STAR"):
            items.append(nodes.FromImportItem("*", None))
        else:
            while True:
                name_token = self._consume("IDENT", "Expected imported name")
                alias = None
                if self._match("AS"):
                    alias_token = self._consume("IDENT", "Expected alias name")
                    alias = alias_token.value
                items.append(nodes.FromImportItem(name_token.value, alias))
                if self._match("COMMA"):
                    continue
                break
        return nodes.FromImportStatement(module, items, keyword.line)

    def _parse_assignment_or_expression(self) -> nodes.Statement:
        expr = self._expression()
        if self._match("ASSIGN"):
            value = self._expression()
            targets = self._collect_assignment_targets(expr)
            return nodes.AssignmentStatement(targets, value, self._previous().line)
        for op_token in ("PLUSEQ", "MINUSEQ", "STAREQ", "SLASHEQ", "DBLSLASHEQ", "PERCENTEQ", "POWEQ"):
            if self._match(op_token):
                value = self._expression()
                target = self._ensure_assignment_target(expr)
                return nodes.AugmentedAssignmentStatement(target, op_token, value, self._previous().line)
        return nodes.ExpressionStatement(expr, self._previous().line)

    def _collect_assignment_targets(self, expr: nodes.Expression) -> List[nodes.Identifier | nodes.AttributeReference | nodes.IndexReference]:
        if isinstance(expr, (nodes.Identifier, nodes.AttributeReference, nodes.IndexReference)):
            return [expr]
        if isinstance(expr, nodes.TupleExpression):
            return [self._ensure_assignment_target(item) for item in expr.elements]
        if isinstance(expr, nodes.ListExpression):
            return [self._ensure_assignment_target(item) for item in expr.elements]
        raise ParseError(self._previous().line, self._previous().column, "Invalid assignment target")

    def _ensure_assignment_target(self, expr: nodes.Expression) -> nodes.Identifier | nodes.AttributeReference | nodes.IndexReference:
        if isinstance(expr, (nodes.Identifier, nodes.AttributeReference, nodes.IndexReference)):
            return expr
        raise ParseError(self._previous().line, self._previous().column, "Invalid assignment target")

    # Expression parsing ------------------------------------------------

    def _expression(self, precedence: int = 0) -> nodes.Expression:
        expr = self._prefix()
        while True:
            token = self._peek()
            if token.type == "IF" and precedence <= 0:
                if not self._conditional_else_pending():
                    break
                self._advance()
                condition = self._expression()
                self._consume("ELSE", "Expected ELSE in conditional expression")
                if_false = self._expression(precedence)
                expr = nodes.ConditionalExpression(condition, expr, if_false)
                continue
            if token.type == "DOT":
                self._advance()
                name_token = self._consume("IDENT", "Expected attribute name after '.'")
                expr = nodes.AttributeReference(expr, name_token.value)
                continue
            if token.type == "LBRACKET":
                self._advance()
                index_expr = self._expression()
                self._consume("RBRACKET", "Expected closing ']' for index")
                expr = nodes.IndexReference(expr, index_expr)
                continue
            if token.type == "LPAREN":
                expr = self._finish_call(expr)
                continue
            if token.type not in BINARY_PRECEDENCE:
                break
            op_precedence = BINARY_PRECEDENCE[token.type]
            if op_precedence < precedence:
                break
            operator_token = self._advance()
            next_precedence = op_precedence + (0 if operator_token.type in RIGHT_ASSOCIATIVE else 1)
            right = self._expression(next_precedence)
            expr = nodes.BinaryExpression(operator_token.type, expr, right)
        return expr

    def _prefix(self) -> nodes.Expression:
        token = self._advance()
        if token.type == "NUMBER":
            if "." in token.value:
                return float(token.value)
            return int(token.value)
        if token.type == "STRING":
            return token.value
        if token.type in BOOL_KEYWORDS:
            return BOOL_KEYWORDS[token.type]
        if token.type == "IDENT":
            return nodes.Identifier(token.value)
        if token.type == "LPAREN":
            expr = self._expression()
            if self._match("COMMA"):
                elements = [expr]
                while True:
                    elements.append(self._expression())
                    if self._match("COMMA"):
                        continue
                    break
                self._consume("RPAREN", "Expected closing ')' for tuple")
                return nodes.TupleExpression(elements)
            self._consume("RPAREN", "Expected closing ')' for grouping")
            return expr
        if token.type == "LBRACKET":
            elements: List[nodes.Expression] = []
            if self._check("RBRACKET"):
                self._advance()
                return nodes.ListExpression(elements)
            first = self._expression()
            if self._match("FOR"):
                iterator = self._consume("IDENT", "Expected identifier in list comprehension")
                self._consume("IN", "Expected IN in list comprehension")
                iterable = self._expression()
                condition = None
                if self._match("IF"):
                    condition = self._expression()
                self._consume("RBRACKET", "Expected closing ']' for list comprehension")
                return nodes.ListComprehension(first, iterator.value, iterable, condition)
            elements.append(first)
            while self._match("COMMA"):
                if self._check("RBRACKET"):
                    break
                elements.append(self._expression())
            self._consume("RBRACKET", "Expected closing ']' for list")
            return nodes.ListExpression(elements)
        if token.type == "LBRACE":
            if self._check("RBRACE"):
                self._advance()
                return nodes.DictExpression([])
            first = self._expression()
            if self._match("COLON"):
                value = self._expression()
                entries: List[tuple[nodes.Expression, nodes.Expression]] = [(first, value)]
                while self._match("COMMA"):
                    if self._check("RBRACE"):
                        break
                    key = self._expression()
                    self._consume("COLON", "Expected ':' in dictionary literal")
                    value = self._expression()
                    entries.append((key, value))
                self._consume("RBRACE", "Expected closing '}' for dictionary")
                return nodes.DictExpression(entries)
            elements: List[nodes.Expression] = [first]
            while self._match("COMMA"):
                if self._check("RBRACE"):
                    break
                elements.append(self._expression())
            self._consume("RBRACE", "Expected closing '}' for set literal")
            return nodes.SetExpression(elements)
        if token.type == "MINUS":
            operand = self._expression(BINARY_PRECEDENCE["POWER"] + 1)
            return nodes.UnaryExpression("NEGATE", operand)
        if token.type == "PLUS":
            operand = self._expression(BINARY_PRECEDENCE["POWER"] + 1)
            return nodes.UnaryExpression("POSITIVE", operand)
        if token.type == "NOT":
            operand = self._expression(BINARY_PRECEDENCE["AND"])
            return nodes.UnaryExpression("NOT", operand)
        if token.type == "LAMBDA":
            parameters: List[nodes.Parameter] = []
            if not self._check("COLON"):
                while True:
                    param_name = self._consume("IDENT", "Expected parameter name in lambda")
                    default = None
                    if self._match("ASSIGN"):
                        default = self._expression()
                    parameters.append(nodes.Parameter(param_name.value, default))
                    if self._match("COMMA"):
                        continue
                    break
            self._consume("COLON", "Expected ':' after lambda parameters")
            body = self._expression()
            return nodes.LambdaExpression(parameters, body)
        if token.type == "AWAIT":
            expr = self._expression()
            return nodes.AwaitExpression(expr)
        raise ParseError(token.line, token.column, f"Unexpected token {token.type}")

    def _finish_call(self, callee: nodes.Expression) -> nodes.Expression:
        lparen = self._consume("LPAREN", "Expected '(' to start call")
        args: List[nodes.Expression] = []
        kwargs: dict[str, nodes.Expression] = {}
        if not self._check("RPAREN"):
            while True:
                if self._check("IDENT") and self._peek_next().type == "ASSIGN":
                    name = self._advance().value
                    self._consume("ASSIGN", "Expected '=' in keyword argument")
                    kwargs[name] = self._expression()
                else:
                    args.append(self._expression())
                if self._match("COMMA"):
                    continue
                break
        self._consume("RPAREN", "Expected ')' to close call")
        return nodes.CallExpression(callee, args, kwargs)

    # Blocks ------------------------------------------------------------

    def _parse_suite(self) -> List[nodes.Statement]:
        if self._match("COLON"):
            self._skip_layout()
            if self._match("INDENT"):
                block: List[nodes.Statement] = []
                self._skip_layout()
                while not self._check("DEDENT"):
                    block.append(self._statement())
                    self._skip_layout()
                self._consume("DEDENT", "Expected DEDENT to close block")
                return block
            # single-line suite
            statement = self._statement()
            return [statement]
        if self._match("LBRACE"):
            block: List[nodes.Statement] = []
            self._skip_layout()
            while not self._check("RBRACE"):
                block.append(self._statement())
                self._skip_layout()
            self._consume("RBRACE", "Expected '}' to close block")
            return block
        raise ParseError(self._peek().line, self._peek().column, "Expected ':' or '{' to start block")

    def _parse_suite_with_docstring(self) -> tuple[List[nodes.Statement], Optional[str]]:
        body = self._parse_suite()
        docstring: Optional[str] = None
        if body and isinstance(body[0], nodes.ExpressionStatement) and isinstance(body[0].expression, str):
            docstring = body[0].expression
            body = body[1:]
        return body, docstring

    def _parse_input(self) -> nodes.InputStatement:
        keyword = self._consume("INPUT")
        prompt: Optional[nodes.Expression] = None
        if not self._check("AS") and not self._check("NEWLINE") and not self._check("EOF"):
            prompt = self._expression()
        target: Optional[str] = None
        if self._match("AS"):
            name = self._consume("IDENT", "Expected identifier after AS in INPUT")
            target = name.value
        return nodes.InputStatement(prompt, target, keyword.line)

    def _parse_output(self) -> nodes.OutputStatement:
        keyword = self._consume("OUTPUT")
        value = self._expression()
        return nodes.OutputStatement(value, keyword.line)

    def _parse_dotted_name(self) -> List[str]:
        parts: List[str] = []
        first = self._consume("IDENT", "Expected module name")
        parts.append(first.value)
        while self._match("DOT"):
            part = self._consume("IDENT", "Expected name after '.'")
            parts.append(part.value)
        return parts

    # Token helpers ----------------------------------------------------

    def _match(self, token_type: str) -> bool:
        if self._check(token_type):
            self._advance()
            return True
        return False

    def _check(self, token_type: str) -> bool:
        return self._peek().type == token_type

    def _peek(self) -> Token:
        return self.tokens[self.position]

    def _peek_next(self) -> Token:
        if self.position + 1 >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.position + 1]

    def _advance(self) -> Token:
        token = self.tokens[self.position]
        self.position += 1
        return token

    def _previous(self) -> Token:
        return self.tokens[self.position - 1]

    def _conditional_else_pending(self) -> bool:
        depth = 0
        index = self.position
        while index < len(self.tokens):
            token = self.tokens[index]
            if token.type in {"LPAREN", "LBRACKET", "LBRACE"}:
                depth += 1
            elif token.type in {"RPAREN", "RBRACKET", "RBRACE"}:
                if depth == 0 and token.type in {"RBRACKET", "RBRACE"}:
                    return False
                depth = max(depth - 1, 0)
            elif depth == 0:
                if token.type == "ELSE":
                    return True
                if token.type in {"COMMA", "COLON", "NEWLINE", "DEDENT", "EOF", "FOR"}:
                    return False
            index += 1
        return False

    def _consume(self, token_type: str, message: Optional[str] = None) -> Token:
        if self._check(token_type):
            return self._advance()
        token = self._peek()
        raise ParseError(token.line, token.column, message or f"Expected token {token_type}")


def parse(tokens: List[Token]) -> nodes.Program:
    """Helper function to build an AST from the token sequence."""

    return Parser(tokens).parse()
