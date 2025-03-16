# src.features.library.services.query


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
                self.advance()
                return Token(Token.NOT, "!")

            if self.current_char in [">", "<", "=", "!"]:
                op = self.current_char
                self.advance()

                # Handle two-character operators (>=, <=, !=)
                if self.current_char == "=" and op in [">", "<", "!"]:
                    op += "="
                    self.advance()

                return Token(Token.OPERATOR, op)

            # Skip unrecognized characters
            self.advance()

        return Token(Token.EOF)


class QueryParser:
    """
    A recursive descent parser for search queries.
    Grammar:
    expression : or_expr
    or_expr    : and_expr (OR and_expr)*
    and_expr   : not_expr (AND not_expr)*
    not_expr   : NOT atom | atom
    atom       : LPAREN expression RPAREN | field_expr | WORD
    field_expr : WORD COLON [OPERATOR] value
    """

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message):
        raise Exception(f"Parser error: {message}")

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
        return self.expression()

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
        """and_expr : not_expr (AND not_expr)*"""
        node = self.not_expr()

        while self.current_token.type == Token.AND or (
            self.current_token.type in [Token.WORD, Token.LPAREN, Token.NOT]
            and self.current_token.type != Token.OR
        ):
            # Skip explicit AND token
            if self.current_token.type == Token.AND:
                self.eat(Token.AND)

            node = {"type": "AND", "left": node, "right": self.not_expr()}

        return node

    def not_expr(self):
        """not_expr : NOT atom | atom"""
        if self.current_token.type == Token.NOT:
            self.eat(Token.NOT)
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
            # Check for field expression (word:value)
            word_token = self.eat(Token.WORD)

            if self.current_token.type == Token.COLON:
                # This is a field expression
                self.eat(Token.COLON)

                operator = "="
                if self.current_token.type == Token.OPERATOR:
                    operator = self.eat(Token.OPERATOR).value

                if self.current_token.type == Token.WORD:
                    value = self.eat(Token.WORD).value
                else:
                    value = ""

                return {
                    "type": "FIELD",
                    "field": word_token.value,
                    "operator": operator,
                    "value": value,
                }

            # Simple word term
            return {"type": "TERM", "value": word_token.value}

        self.error(f"Unexpected token: {token}")


class SQLGenerator:
    """Converts a parsed expression tree into SQL."""

    def __init__(self):
        # Field mappings to handle JSON fields
        # Format: {lowercase_field_name: (json_container, field_name, field_type)}
        self.field_mappings = {
            # Tags fields
            "title": ("tags", "TITLE", "text"),
            "artist": ("tags", "ARTIST", "text"),
            "album": ("tags", "ALBUM", "text"),
            "genre": ("tags", "GENRE", "text"),
            "albumartist": ("tags", "ALBUM_ARTIST", "text"),
            "date": ("tags", "DATE", "text"),  # Todo: Date might need special handling
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
        }

    def generate(self, expr):
        """Generate SQL WHERE clause and parameters from an expression tree."""
        return self._generate_node(expr)

    def _generate_node(self, node):
        """
        Recursively generate SQL for a node in the expression tree.
        Returns (sql_fragment, params).
        """
        node_type = node["type"]

        if node_type == "AND":
            left_sql, left_params = self._generate_node(node["left"])
            right_sql, right_params = self._generate_node(node["right"])
            return f"({left_sql} AND {right_sql})", left_params + right_params

        elif node_type == "OR":
            left_sql, left_params = self._generate_node(node["left"])
            right_sql, right_params = self._generate_node(node["right"])
            return f"({left_sql} OR {right_sql})", left_params + right_params

        elif node_type == "NOT":
            expr_sql, expr_params = self._generate_node(node["expr"])
            return f"NOT ({expr_sql})", expr_params

        elif node_type == "FIELD":
            field = node["field"].lower()  # Case-insensitive field names
            value = node["value"]
            operator = node["operator"]

            # Get field mapping or use default
            if field in self.field_mappings:
                json_container, field_name, field_type = self.field_mappings[field]

                # Create the JSON extraction expression
                json_path = f"$.{field_name}"
                field_expr = f"json_extract({json_container}, '{json_path}')"

                # Handle different field types
                if field_type == "text":
                    if operator in ["=", "LIKE"]:
                        return f"{field_expr} LIKE ?", [f"%{value}%"]
                    elif operator in ["!=", "NOT LIKE"]:
                        return f"{field_expr} NOT LIKE ?", [f"%{value}%"]
                    else:
                        # Default to LIKE for text fields
                        return f"{field_expr} LIKE ?", [f"%{value}%"]
                elif field_type == "numeric":
                    # Handle special numeric field values
                    if field == "date" and value.endswith("s"):
                        # Handle decade (e.g., 1980s)
                        try:
                            decade = int(value[:-1])
                            return f"({field_expr} >= ? AND {field_expr} <= ?)", [
                                decade,
                                decade + 9,
                            ]
                        except ValueError:
                            return "1=0", []  # Invalid decade format

                    try:
                        # Try to convert value to number for numeric comparisons
                        if "." in value:
                            num_value = float(value)
                        else:
                            num_value = int(value)

                        return f"{field_expr} {operator} ?", [num_value]
                    except ValueError:
                        # Not a valid number
                        return "1=0", []  # Will never match
            else:
                # For unknown fields, default to searching tags with LIKE
                field_expr = f"json_extract(tags, '$.{field.upper()}')"
                return f"{field_expr} LIKE ?", [f"%{value}%"]

        elif node_type == "TERM":
            # Simple term searches across all common text fields
            value = node["value"]
            sql_parts = []
            params = []

            # Search in common text fields within tags
            text_fields = ["TITLE", "ARTIST", "ALBUM", "GENRE"]
            for field in text_fields:
                sql_parts.append(f"json_extract(tags, '$.{field}') LIKE ?")
                params.append(f"%{value}%")

            return f"({' OR '.join(sql_parts)})", params

        # Default case - should not reach here
        return "1=1", []
