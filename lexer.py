from __future__ import annotations
import json


class Token:
    # Initialize a Token object with type and value
    def __init__(self, token_type: str, value: str):
        self.token_type = token_type
        self.value = value

    def to_dict(self):
        """Convert the Token to a dictionary for JSON serialization."""
        return {"token": self.token_type, "lexeme": self.value}


class Lexer:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.exceed_limit = False

    # Get the current character
    def get_current_char(self):
        if self.position < len(self.source_code):
            return self.source_code[self.position]
        return None
    
    # Move the pointer forward by one position
    def advance(self):
        self.position += 1

    # Skip all whitespace characters
    def skip_whitespace(self):
        while self.get_current_char() and self.get_current_char().isspace():
            self.advance()

    def read_number(self):
        start_position = self.position
        current_char = self.get_current_char()

        # If the number is '0', return it as a separate Token
        if current_char == '0':
            self.advance()
            return Token('num', '0')

        # If it starts with a non-zero digit, read multiple digits
        if current_char and current_char.isdigit() and current_char!= '0':
            while self.get_current_char() and self.get_current_char().isdigit():
                self.advance()

        number_value = self.source_code[start_position:self.position]

        # Check if it exceeds 10 digits
        if len(number_value) > 10:
            self.exceed_limit = True
            return None

        return Token('num', number_value)

    def read_identifier(self, keywords: set):
        """
        Parse identifier: read consecutive lowercase letters.
        Check if the parsed result is a keyword.
        """
        start_position = self.position

        while self.get_current_char() and self.get_current_char().islower():
            self.advance()

        value = self.source_code[start_position:self.position]

        # Check if it's a keyword
        if value in keywords:
            return Token(value, value) 
        return Token('id', value)  

    # Parse operator Token
    def read_operator(self):
        
        char = self.get_current_char()
        valid_operators = {'+', '-', '*', '{', '}', '.', '(', ')', ':', '@', '<', '>', '&', '|', '!', '='}
        if char in valid_operators:
            self.advance()
            return Token(char, char)
        return None

    # Generate all Tokens and return [] if input is illegal
    def next_token(self):
        keywords = {'let', 'be', 'show', 'int', 'set', 'simplify'}  
        set_operators = {'U', 'I'} 
        result = []

        while self.position < len(self.source_code):
            self.skip_whitespace()
            char = self.get_current_char()

            if char is None: 
                break
            
            # Parse lowercase letters as identifier or keyword
            if char.islower():  
                token = self.read_identifier(keywords)
                result.append(token.to_dict())

            elif char.isdigit():  
                token = self.read_number()
                if self.exceed_limit:
                    return json.dumps([], indent=2)
                result.append(token.to_dict())

            # Set operators (U, I)
            elif char in set_operators:  
                result.append(Token(char, char).to_dict())
                self.advance()

            elif char.isupper(): 
                return json.dumps([], indent=2)

            elif char in {'+', '-', '*', '{', '}', '.', '(', ')', ':', '@', '<', '>', '&', '|', '!', '='}:  # Operators
                result.append(self.read_operator().to_dict())
            
            # Unrecognized character, return []
            else:  
                return json.dumps([], indent=2)

        return json.dumps(result, indent=2)
