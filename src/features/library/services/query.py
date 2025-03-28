# src.features.library.services.query
import logging

logger = logging.getLogger(__name__)


class Token:
    """Represents a token in the query language."""

    # Token types
    WORD = "WORD"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COLON = "COLON"
    OPERATOR = "OPERATOR"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    EOF = "EOF"

    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __str__(self):
        return f"Token({self.type}, {self.value})"


class QueryLexer:
    """Tokenizes a query string into tokens."""

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None

    def advance(self):
        """Move to the next character."""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        """Skip any whitespace characters."""
        while self.current_char and self.current_char.isspace():
            self.advance()

    def get_word(self):
        """Extract a word token."""
        result = ""
        while self.current_char and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            result += self.current_char
            self.advance()

        # Check for AND/OR keywords
        upper_result = result.upper()
        if upper_result == "AND":
            return Token(Token.AND, result)
        elif upper_result == "OR":
            return Token(Token.OR, result)

        return Token(Token.WORD, result)

    def get_quoted_string(self):
        """Extract a quoted string."""
        self.advance()  # Skip the opening quote
        result = ""
        while self.current_char and self.current_char != '"':
            # Basic handling for escaped quotes within the string
            if (
                self.current_char == "\\"
                and self.pos + 1 < len(self.text)
                and self.text[self.pos + 1] == '"'
            ):
                result += '"'
                self.advance()  # Skip '\'
                self.advance()  # Skip '"'
            else:
                result += self.current_char
                self.advance()

        if self.current_char == '"':
            self.advance()  # Skip the closing quote

        return Token(Token.WORD, result)

    def get_next_token(self):
        """Get the next token from the input."""
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalnum() or self.current_char == "_":
                return self.get_word()

            if self.current_char == '"':
                return self.get_quoted_string()

            if self.current_char == "(":
                self.advance()
                return Token(Token.LPAREN, "(")

            if self.current_char == ")":
                self.advance()
                return Token(Token.RPAREN, ")")

            if self.current_char == ":":
                self.advance()
                return Token(Token.COLON, ":")

            if self.current_char == "!":
                # Check for != operator first
                if self.pos + 1 < len(self.text) and self.text[self.pos + 1] == "=":
                    self.advance()  # Skip !
                    self.advance()  # Skip =
                    return Token(Token.OPERATOR, "!=")
                # Otherwise, it's a NOT token
                self.advance()
                return Token(Token.NOT, "!")

            if self.current_char in [">", "<", "="]:
                op = self.current_char
                self.advance()

                # Handle two-character operators (>=, <=)
                if self.current_char == "=" and op in [">", "<"]:
                    op += "="
                    self.advance()

                return Token(Token.OPERATOR, op)

            logger.warning(f"Unrecognized character skipped: {self.current_char}")
            self.advance()

        return Token(Token.EOF)


class QueryParser:
    """
    A recursive descent parser for search queries.
    Grammar:
    expression : or_expr
    or_expr    : and_expr (OR and_expr)*
    and_expr   : not_expr (AND? not_expr)*  (AND is optional/implicit)
    not_expr   : NOT atom | atom
    atom       : LPAREN expression RPAREN | field_expr | WORD
    field_expr : WORD COLON [OPERATOR] value
    value      : WORD | quoted_string (handled by lexer returning WORD)
    """

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message):
        raise ValueError(f"Parser error: {message} near token {self.current_token}")

    def eat(self, token_type):
        """
        Compare the current token type with the expected type
        and if they match, consume the token and get the next one.
        """
        if self.current_token.type == token_type:
            result = self.current_token
            self.current_token = self.lexer.get_next_token()
            return result
        self.error(f"Expected {token_type}, got {self.current_token.type}")

    def parse(self):
        """Parse the expression and return an expression tree."""
        node = self.expression()
        if self.current_token.type != Token.EOF:
            self.error("Unexpected token at end of query")
        return node

    def expression(self):
        """expression : or_expr"""
        return self.or_expr()

    def or_expr(self):
        """or_expr : and_expr (OR and_expr)*"""
        node = self.and_expr()

        while self.current_token.type == Token.OR:
            self.eat(Token.OR)
            node = {"type": "OR", "left": node, "right": self.and_expr()}

        return node

    def and_expr(self):
        """and_expr : not_expr (AND? not_expr)*"""
        node = self.not_expr()

        # Implicit AND: loop as long as the next token can start a new expression
        # and is not OR or EOF.
        while self.current_token.type not in [Token.OR, Token.RPAREN, Token.EOF]:
            # Skip explicit AND token if present
            if self.current_token.type == Token.AND:
                self.eat(Token.AND)

            # Check if the next token can actually start a 'not_expr'
            if self.current_token.type not in [Token.NOT, Token.LPAREN, Token.WORD]:
                self.error(
                    f"Expected expression component after implicit/explicit AND, got {self.current_token.type}"
                )

            node = {"type": "AND", "left": node, "right": self.not_expr()}

        return node

    def not_expr(self):
        """not_expr : NOT atom | atom"""
        if self.current_token.type == Token.NOT:
            self.eat(Token.NOT)
            # Ensure NOT is followed by a valid expression part
            if self.current_token.type not in [Token.LPAREN, Token.WORD]:
                self.error(
                    f"Expected expression component after NOT, got {self.current_token.type}"
                )
            return {"type": "NOT", "expr": self.atom()}
        return self.atom()

    def atom(self):
        """atom : LPAREN expression RPAREN | field_expr | WORD"""
        token = self.current_token

        if token.type == Token.LPAREN:
            self.eat(Token.LPAREN)
            node = self.expression()
            self.eat(Token.RPAREN)
            return node

        if token.type == Token.WORD:
            word_token = self.eat(Token.WORD)

            # Check if it's a field expression (followed by a colon)
            if self.current_token.type == Token.COLON:
                self.eat(Token.COLON)

                # Default operator is '='
                operator = "="
                if self.current_token.type == Token.OPERATOR:
                    operator = self.eat(Token.OPERATOR).value

                # Expecting a value (WORD token, could be number, word, or quoted string)
                if self.current_token.type == Token.WORD:
                    value_token = self.eat(Token.WORD)
                    value = value_token.value

                    # Determine if the value looks numeric for SQL generation hint
                    is_numeric = False
                    if value:  # Avoid error on empty string
                        try:
                            # Try parsing as float, which covers ints too
                            float(value)
                            is_numeric = True
                        except ValueError:
                            is_numeric = False

                    return {
                        "type": "FIELD",
                        "field": word_token.value,
                        "operator": operator,
                        "value": value,
                        "is_numeric": is_numeric,  # Hint for SQL generator
                    }
                else:
                    logger.warning(
                        f"Field expression '{word_token.value}{operator}' has no value. Treating as empty string search."
                    )
                    return {
                        "type": "FIELD",
                        "field": word_token.value,
                        "operator": operator,
                        "value": "",
                        "is_numeric": False,
                    }

            # If not followed by colon, it's a simple search term
            return {"type": "TERM", "value": word_token.value}

        # If token is not LPAREN or WORD, it's unexpected in this position
        self.error(f"Unexpected token: {token}")


class SQLGenerator:
    """Converts a parsed expression tree into SQL WHERE clause."""

    def __init__(self):
        # Field mappings to handle specific JSON fields efficiently
        # Format: {lowercase_query_field: (json_container, json_key, field_type)}
        self.field_mappings = {
            # Tags fields (using uppercase keys as per metadata.py convention)
            "title": ("tags", "TITLE", "text"),
            "artist": ("tags", "ARTIST", "text"),
            "album": ("tags", "ALBUM", "text"),
            "genre": ("tags", "GENRE", "text"),
            "albumartist": ("tags", "ALBUM_ARTIST", "text"),
            # App data fields
            "play_count": ("app_data", "play_count", "numeric"),
            "rating": ("app_data", "rating", "numeric"),
            "last_played": ("app_data", "last_played", "numeric"),
            "skip_count": ("app_data", "skip_count", "numeric"),
            # File property fields
            "length": ("fileprops", "length", "numeric"),
            "bitrate": ("fileprops", "bitrate", "numeric"),
            "sample_rate": ("fileprops", "sample_rate", "numeric"),
            "size": ("fileprops", "size", "numeric"),
            "release_time": ("tags", "RELEASE_TIME", "numeric"),  # Mapping explicitly
        }
        # Define fields to search for simple TERM queries
        self._term_search_fields = [
            ("tags", "TITLE"),
            ("tags", "ARTIST"),
            ("tags", "ALBUM"),
            ("tags", "GENRE"),
            ("tags", "ALBUM_ARTIST"),
        ]

    def generate(self, expr):
        """Generate SQL WHERE clause and parameters from an expression tree."""
        sql, params = self._generate_node(expr)
        # Handle cases where generation might return empty string if root node is invalid
        return sql if sql else "1=1", params

    def _generate_node(self, node):
        """
        Recursively generate SQL for a node in the expression tree.
        Returns (sql_fragment, params_list).
        """
        if not node:  # Handle potential empty nodes from parsing errors
            return "1=1", []

        node_type = node.get("type")

        if node_type == "AND":
            left_sql, left_params = self._generate_node(node.get("left"))
            right_sql, right_params = self._generate_node(node.get("right"))
            # Avoid generating invalid SQL like "(...) AND " if right side is empty/invalid
            if not right_sql or right_sql == "1=1":
                return left_sql, left_params
            if not left_sql or left_sql == "1=1":
                return right_sql, right_params
            return f"({left_sql} AND {right_sql})", left_params + right_params

        elif node_type == "OR":
            left_sql, left_params = self._generate_node(node.get("left"))
            right_sql, right_params = self._generate_node(node.get("right"))
            # Avoid generating invalid SQL like "(...) OR " if right side is empty/invalid
            if not right_sql or right_sql == "1=1":
                return left_sql, left_params
            if not left_sql or left_sql == "1=1":
                return right_sql, right_params
            return f"({left_sql} OR {right_sql})", left_params + right_params

        elif node_type == "NOT":
            expr_sql, expr_params = self._generate_node(node.get("expr"))
            # Avoid generating "NOT ()" if subexpression is invalid
            if not expr_sql or expr_sql == "1=1":
                return (
                    "1=1",
                    [],
                )  # NOT (always true) is always false, but safer to return 1=1
            return f"NOT ({expr_sql})", expr_params

        elif node_type == "FIELD":
            field = node["field"].lower()  # Use lowercase for mapping lookup
            value = node["value"]
            operator = node["operator"]
            is_numeric_hint = node["is_numeric"]

            # Handle knwon fields
            if field in self.field_mappings:
                json_container, json_key, field_type = self.field_mappings[field]

                # Conditional [0] for tags + numeric
                json_path = f"$.{json_key}"
                is_tags_numeric = json_container == "tags" and field_type == "numeric"
                if is_tags_numeric:
                    json_path += "[0]"

                field_expr = f"json_extract({json_container}, '{json_path}')"

                if field_type == "text":
                    # Use LIKE for =/implicit, NOT LIKE for !=
                    if operator in ["=", "LIKE"]:
                        sql_op = "LIKE"
                        param = f"%{value}%"
                    elif operator in ["!=", "NOT LIKE"]:
                        sql_op = "NOT LIKE"
                        param = f"%{value}%"
                    else:
                        sql_op = operator
                        param = value
                    # Text comparison against extracted value (may be array string for tags)
                    return f"({field_expr} IS NOT NULL AND {field_expr} {sql_op} ?)", [
                        param
                    ]

                elif field_type == "numeric":
                    try:
                        num_value = float(value) if "." in value else int(value)
                        # Generate SQL with explicit CAST. Path already includes [0] if needed.
                        return (
                            f"({field_expr} IS NOT NULL AND CAST({field_expr} AS REAL) {operator} ?)",
                            [num_value],
                        )
                    except ValueError:
                        logger.warning(
                            f"Invalid numeric value '{value}' for field '{field}'. Query part ignored."
                        )
                        return "1=0", []

            # Handle unknown fields
            else:
                logger.debug(
                    f"Field '{field}' not in explicit mappings, using fallback logic."
                )
                key_upper = field.upper()
                key_asis = field

                if is_numeric_hint:
                    try:
                        num_value = float(value) if "." in value else int(value)
                        operator = node["operator"]

                        # Add [0] for numeric fallback in tags
                        json_path_upper = f"$.{key_upper}[0]"
                        json_path_asis = f"$.{key_asis}[0]"

                        # Build SQL checking both casings, casting extracted value to REAL
                        sql = f"""(
                            (
                                json_extract(tags, '{json_path_upper}') IS NOT NULL AND
                                CAST(json_extract(tags, '{json_path_upper}') AS REAL) {operator} ?
                            )
                            OR
                            (
                                json_extract(tags, '{json_path_upper}') IS NULL AND
                                json_extract(tags, '{json_path_asis}') IS NOT NULL AND
                                CAST(json_extract(tags, '{json_path_asis}') AS REAL) {operator} ?
                            )
                        )"""
                        return sql, [num_value, num_value]
                    except ValueError:
                        logger.warning(
                            f"Invalid numeric value '{value}' for fallback field '{field}'. Query part ignored."
                        )
                        return "1=0", []

                # Text comparison for fallback
                else:
                    # Paths remain WITHOUT [0] for text fallback
                    json_path_upper = f"$.{key_upper}"
                    json_path_asis = f"$.{key_asis}"

                    if operator in ["=", "LIKE"]:
                        sql_op = "LIKE"
                        param = f"%{value}%"
                    elif operator in ["!=", "NOT LIKE"]:
                        sql_op = "NOT LIKE"
                        param = f"%{value}%"
                    else:
                        sql_op = operator
                        param = value

                    # Build SQL checking both casings for text match (against array string)
                    sql = f"""(
                        (
                            json_extract(tags, '{json_path_upper}') IS NOT NULL AND
                            json_extract(tags, '{json_path_upper}') {sql_op} ?
                        )
                        OR
                        (
                            json_extract(tags, '{json_path_upper}') IS NULL AND
                            json_extract(tags, '{json_path_asis}') IS NOT NULL AND
                            json_extract(tags, '{json_path_asis}') {sql_op} ?
                        )
                    )"""
                    return sql, [param, param]

        elif node_type == "TERM":
            # Simple term searches across predefined text fields
            value = node["value"]
            sql_parts = []
            params = []

            for container, key in self._term_search_fields:
                # Handle TERM search in 'tags'
                if container == "tags":
                    json_path = f"$.{key}"  # Path without [0] for LIKE matching
                    field_expr = f"json_extract({container}, '{json_path}')"
                    # Check for NULL and use LIKE against array string representation
                    sql_parts.append(
                        f"({field_expr} IS NOT NULL AND {field_expr} LIKE ?)"
                    )
                    params.append(f"%{value}%")

                # Handle non-tags TERM search fields
                else:
                    # Todo
                    pass

            if not sql_parts:
                return "1=0", []  # No fields defined/matched for term search

            return f"({' OR '.join(sql_parts)})", params

        logger.error(f"Unknown or invalid node structure encountered: {node}")
        return "1=1", []
