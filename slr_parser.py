class Parser:
    def __init__(self, grammar_file: str, parsing_table_file: str):
        self.grammar = self.load_grammar(grammar_file)
        self.parsing_table = self.load_parsing_table(parsing_table_file)

    def load_grammar(self, grammar_file):
        grammar = {}
        with open(grammar_file, 'r') as file:
            for line in file:
                if '->' in line:
                    index, rule = line.strip().split('.', 1)
                    head, body = rule.split('->')
                    grammar[int(index)] = (head.strip(), body.strip().split())
        return grammar

    def load_parsing_table(self, parsing_table_file):
        parsing_table = {}
        with open(parsing_table_file, 'r') as file:
            file.readline()  
            headers = file.readline().strip().split(',')[1:]  
            headers = [header.strip() for header in headers]  # Remove whitespace from headers

            for line in file:
                cells = line.strip().split(',')
                if not cells[0].isdigit():
                    continue  # Skip invalid or empty rows
                state = int(cells[0])  

                for index, value in enumerate(cells[1:]):
                    if value.strip():  
                        symbol = headers[index]  # Map to the corresponding header
                        parsing_table[(state, symbol)] = value.strip()

        # Verify that parsing table contains required keys
        if (0, 'show') not in parsing_table:
            raise ValueError("Parsing Table does not contain action for (0, 'show')")

        return parsing_table

    def parse(self, tokens):
        self.state_stack = [0]  # Initialize state stack
        self.symbol_stack = []  # Symbol stack
        position = 0  # Position in the input tokens

        parse_tree = {"name": "S'", "children": []}  # Root of the parse tree
        tree_stack = [parse_tree]  

        try:
            while True:
                current_state = self.state_stack[-1]

                if position < len(tokens):
                    current_token = tokens[position]
                    token_type = current_token["token"]
                else:
                    current_token = {"token": "$", "lexeme": "$"}
                    token_type = "$"

                action = self.parsing_table.get((current_state, token_type))
                if not action:
                    available_tokens = [
                        key[1] for key in self.parsing_table.keys() if key[0] == current_state
                    ]   
                    raise SyntaxError(
                        f"Parsing Table Lookup Failed: State {current_state}, Token '{token_type}'. "
                        f"Available tokens for this state: {available_tokens}"
                    )

                if action.startswith('s'):  
                    next_state = int(action[1:])  # Get the next state
                    self.state_stack.append(next_state)
                    self.symbol_stack.append(token_type)
                    new_node = {"token": token_type, "lexeme": current_token["lexeme"]}
                    tree_stack.append(new_node) 
                    position += 1 

                elif action.startswith('r'):  
                    rule_index = int(action[1:])  
                    head, body = self.grammar[rule_index]  

                    # Pop the appropriate number of elements from the stacks
                    for _ in range(len(body)):
                        self.state_stack.pop()
                        self.symbol_stack.pop()

                    # Create a new node for the reduction and set up its children
                    subtree = {"name": head, "children": []}
                    for _ in range(len(body)):
                        child_node = tree_stack.pop()
                        subtree["children"].insert(0, child_node)  # Insert at the front to maintain order

                    tree_stack.append(subtree)

                    # Perform GOTO action
                    current_state = self.state_stack[-1]
                    goto_state = self.parsing_table.get((current_state, head))
                    if not goto_state:
                        raise SyntaxError(f"Invalid GOTO action for state {current_state} and symbol '{head}'")

                    self.state_stack.append(int(goto_state))
                    self.symbol_stack.append(head)

                elif action == "acc":  # Accept action
                    break

            result = tree_stack.pop()
            return result

        except Exception as e:
            return {}  



