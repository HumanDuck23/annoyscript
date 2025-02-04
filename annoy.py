#!/usr/bin/env python3
import sys

# =============================================================================
# Comment Preprocessing
# =============================================================================

def strip_comments(source):
    """
    Removes any comments from the source.
    A comment starts with a semicolon (;) and runs until the end of the line.
    """
    lines = source.splitlines()
    new_lines = []
    for line in lines:
        semicolon_index = line.find(';')
        if semicolon_index != -1:
            line = line[:semicolon_index]
        new_lines.append(line)
    return "\n".join(new_lines)

# =============================================================================
# Data Structures for the Parser
# =============================================================================

class Block:
    def __init__(self, block_type, items):
        """
        block_type: "normal" or "conditional"
        items: list of items (each is either a literal string of operations or a nested Block)
        """
        self.block_type = block_type
        self.items = items

    def __repr__(self):
        return f"Block({self.block_type!r}, {self.items!r})"

# =============================================================================
# Parser
# =============================================================================

def parse_program(source):
    """Parses the entire AnnoyScript source and returns a list of top–level Block objects."""
    index = 0
    blocks = []
    while index < len(source):
        # Skip any whitespace outside tokens.
        if source[index].isspace():
            index += 1
            continue
        if source[index] == '(':
            block, index = parse_block(source, index)
            blocks.append(block)
        else:
            raise Exception(f"Unexpected character at top level: '{source[index]}' at index {index}")
    return blocks

def parse_block(source, index):
    """
    Parses a token pair starting at source[index].  
    Expects either a normal block starting with '(<' (ending with '>)')
    or a conditional block starting with '(?' (ending with '?)').
    Returns a tuple (block, new_index) where new_index is after the closing token.
    """
    if index >= len(source) or source[index] != '(':
        raise Exception(f"Expected '(' at index {index}")
    index += 1  # consume '('

    if index >= len(source):
        raise Exception(f"Unexpected end of input after '(' at index {index}")

    # Determine block type from the next character.
    if source[index] == '<':
        block_type = "normal"
        closing_token = '>)'
    elif source[index] == '?':
        block_type = "conditional"
        closing_token = '?)'
    else:
        raise Exception(f"Invalid token after '(' at index {index}: expected '<' or '?', found '{source[index]}'")
    index += 1  # consume the token character (< or ?)

    items = []       # will hold literal strings and nested Blocks
    literal_buffer = ""

    # Parse until we hit the closing token.
    while index < len(source):
        # Check if the next two characters match the closing token.
        if source[index:index+2] == closing_token:
            if literal_buffer:
                items.append(literal_buffer)
                literal_buffer = ""
            index += 2  # consume closing token
            return Block(block_type, items), index

        # If a nested block begins here: look for '(' followed immediately by '<' or '?'
        if source[index] == '(' and index + 1 < len(source) and source[index+1] in ['<', '?']:
            # Flush any buffered literal ops before starting a nested block.
            if literal_buffer:
                items.append(literal_buffer)
                literal_buffer = ""
            nested_block, index = parse_block(source, index)
            items.append(nested_block)
            continue

        # Otherwise, add the character to the literal buffer.
        literal_buffer += source[index]
        index += 1

    raise Exception(f"Missing closing token '{closing_token}' for block starting at index {index}")

# =============================================================================
# Interpreter
# =============================================================================

class AnnoyInterpreter:
    def __init__(self, blocks):
        self.blocks = blocks
        self.tape = [0] * 128      # 128 cells (8–bit unsigned, wrap at 256)
        self.pointer = 0           # starting at cell 0
        self.instruction_counter = 0  # counts each token pair executed

    def run(self):
        """Execute each top–level block in sequence."""
        for block in self.blocks:
            self.execute_block(block, depth=0)

    def execute_block(self, block, depth):
        """
        Execute a Block (token pair).  
        depth: current nesting depth (top–level blocks have depth 0).
        """
        # For a conditional block, check the condition:
        if block.block_type == "conditional":
            if self.tape[self.pointer] == 0:
                # Condition false: skip block content but count it as an instruction.
                self.instruction_counter += 1
                # No pointer override from content; use default movement.
                self.apply_pointer_movement(override=0)
                return

        # If we reach here, either it’s a normal block or a conditional whose condition held.
        # Process the block's items.
        block_pointer_override = 0  # local override accumulator for this block

        for item in block.items:
            if isinstance(item, str):
                # Process literal sequence.
                override = self.execute_literal(item, depth)
                block_pointer_override += override
            elif isinstance(item, Block):
                # Execute nested block at increased depth.
                self.execute_block(item, depth + 1)
            else:
                raise Exception(f"Unknown block item type: {item}")

        # After processing all items in this token pair, count this as an instruction.
        self.instruction_counter += 1
        # Then update pointer movement.
        self.apply_pointer_movement(override=block_pointer_override)

    def execute_literal(self, literal, depth):
        """
        Execute a literal string of operations (from within a token pair).
        Returns the pointer override sum produced by any '^' or 'v' operations.
        """
        pointer_override = 0
        i = 0
        while i < len(literal):
            ch = literal[i]
            if ch in ['+', '-']:
                # Count how many consecutive same characters.
                count = 1
                j = i + 1
                while j < len(literal) and literal[j] == ch:
                    count += 1
                    j += 1
                effect = 0
                for k in range(1, count + 1):
                    if ch == '+':
                        # In even nesting, '+' adds; in odd nesting, it subtracts.
                        effect += k if (depth % 2 == 0) else -k
                    else:  # ch == '-'
                        effect -= k if (depth % 2 == 0) else -k
                self.tape[self.pointer] = (self.tape[self.pointer] + effect) % 256
                i = j
            elif ch in ['^', 'v']:
                # Pointer override symbols.
                if ch == '^':
                    # At even nesting, '^' moves pointer right (+1); at odd, it moves left (-1).
                    pointer_override += (1 if (depth % 2 == 0) else -1)
                else:  # ch == 'v'
                    # At even nesting, 'v' moves pointer left (-1); at odd, it moves right (+1).
                    pointer_override += (-1 if (depth % 2 == 0) else 1)
                i += 1
            elif ch == '.':
                # Output the ASCII character from current cell.
                value = self.tape[self.pointer]
                if value < 32 or value > 126:
                    raise Exception(f"Display of Dismay error: cell[{self.pointer}] = {value} is not in printable range")
                sys.stdout.write(chr(value))
                sys.stdout.flush()
                i += 1
            elif ch == ',':
                # Read one character from input.
                inp = sys.stdin.read(1)
                if inp == '':
                    raise Exception("Input error: no input available")
                self.tape[self.pointer] = ord(inp) % 256
                i += 1
            elif ch == '#':
                # Reset current cell to zero.
                self.tape[self.pointer] = 0
                i += 1
            elif ch.isspace():
                # Ignore whitespace inside a token pair.
                i += 1
            else:
                raise Exception(f"Unknown operation symbol '{ch}' encountered in literal (depth {depth}).")
        return pointer_override

    def apply_pointer_movement(self, override):
        """
        Updates the pointer after finishing a token pair (instruction).  
        If an override was produced by '^' or 'v', use it. Otherwise,
        use the default rule: after the n–th instruction, if n is odd move left,
        if even move right.
        """
        if override != 0:
            self.pointer = (self.pointer + override) % 128
        else:
            if self.instruction_counter % 2 == 1:
                # Odd-numbered instruction: move pointer left by 1.
                self.pointer = (self.pointer - 1) % 128
            else:
                # Even-numbered instruction: move pointer right by 1.
                self.pointer = (self.pointer + 1) % 128

# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 annoy.py <sourcefile.annoy>")
        sys.exit(1)
    try:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Strip out semicolon comments.
    source = strip_comments(source)

    try:
        blocks = parse_program(source)
    except Exception as e:
        print(f"Parse Error: {e}")
        sys.exit(1)

    interpreter = AnnoyInterpreter(blocks)
    try:
        interpreter.run()
    except Exception as e:
        print(f"\nRuntime Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
