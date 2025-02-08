from lexer import Lexer
from slr_parser import Parser
from type_checker import type_checking
from evaluator import evaluating
import sys
import json

# WARNING:
# - You are not allowed to use any external libraries other than the standard library
# - Please do not modify the file name of the entry file 'main.py'
# - Our autograder will test your code by running 'python main.py <test_file>'
#   The current directory will be the same directory as the entry file
#   So please make sure your import statement is correct

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python main.py <test_file>")
        sys.exit(1)

    file_name = sys.argv[1]

    with open(file_name, 'r') as f:
        # Read file content
        source_code = f.read()

    # Step 1: Lexer Phase
    lexer = Lexer(source_code)
    token_output = lexer.next_token()

    # Save lexer output to 'lexer_out.json'
    lexer_output_file = "lexer_out.json"
    with open(lexer_output_file, 'w') as output_file:
        output_file.write(token_output)

    # Step 2: Parser Phase
    grammar_file = "SLR Grammar.txt"
    parsing_table_file = "SLR Parsing Table.csv"
    parser = Parser(grammar_file, parsing_table_file)

    # Initialize empty parse tree
    parse_tree = {}

    try:
        # Parse the tokens from lexer
        tokens = json.loads(token_output)
        parse_tree = parser.parse(tokens)

        # Step 3: Save the parse tree to 'parser_out.json' if parsing is successful
        parser_output_file = "parser_out.json"
        with open(parser_output_file, 'w') as output_file:
            json.dump(parse_tree, output_file)

    except Exception as e:
        # If there's any error, create empty JSON files
        with open("parser_out.json", 'w') as output_file:
            json.dump({}, output_file)

type_checking("parser_out.json", "typing_out.json")
evaluating("parser_out.json", "evaluation_out.json")


