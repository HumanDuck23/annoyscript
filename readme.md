# AnnoyScript Documentation

Welcome to **AnnoyScript**, the deterministic esoteric programming language designed to be as predictably painful and difficult as possible. This document describes every aspect of how AnnoyScript works and provides a simple example to get you started.

---

## Table of Contents

1. [Overview](#overview)
2. [Memory Model](#memory-model)
3. [Syntax and Tokens](#syntax-and-tokens)
    - [Token Pairs](#token-pairs)
    - [Conditional Blocks](#conditional-blocks)
    - [Comments](#comments)
4. [Operations](#operations)
    - [Arithmetic Operations (`+` and `-`)](#arithmetic-operations)
    - [Pointer Overrides (`^` and `v`)](#pointer-overrides)
    - [I/O Operations (`.` and `,`)](#io-operations)
    - [Reset Operation (`#`)](#reset-operation)
5. [Pointer Movement](#pointer-movement)
6. [Control Flow](#control-flow)
7. [Error Handling](#error-handling)
8. [Example: Outputting a Letter](#example-outputting-a-letter)
9. [Conclusion](#conclusion)

---

## Overview

AnnoyScript is a deliberately obtuse language whose features force you to track hidden modes and non‑linear arithmetic effects. Every instruction is enclosed in token pairs, and the behavior of the operations within these tokens depends on the nesting depth. The language is entirely deterministic—given the same source code and input, it always produces the same output—but its design makes even simple programs challenging to write and debug.

---

## Memory Model

- **Tape:** AnnoyScript uses a one-dimensional tape of **128 cells** (each cell holds an 8‑bit unsigned integer, values 0–255).
- **Pointer:** The data pointer starts at cell 0.
- **Forced Pointer Movement:** After each token pair (instruction) completes, the pointer moves:
  - **Default:** If no pointer override is produced by the current token, the pointer moves:
    - **Left by 1** after an odd-numbered instruction.
    - **Right by 1** after an even-numbered instruction.
  - **Override:** If the token contains pointer override symbols (`^` or `v`), their cumulative effect replaces the default movement.

---

## Syntax and Tokens

AnnoyScript programs are composed of token pairs that encapsulate one or more operations.

### Token Pairs

- **Normal Token Pair:** Begins with `(<` and ends with `>)`.
- **Usage:** Every operation must be enclosed in a matching token pair. For example:
  ```(< ... >)```
- **Literal Content:** Within a token pair, you may have a literal sequence of operation symbols (see [Operations](#operations)).

### Conditional Blocks

- **Conditional Token Pair:** Begins with `(?` and ends with `?)`.
- **Execution:** The block is executed **only if** the current cell’s value is **nonzero** at the moment the block is encountered. If the current cell equals zero, the entire block is skipped (though it still counts as an instruction).

### Comments

- **Comments:** Any text beginning with a semicolon (`;`) and continuing to the end of the line is treated as a comment and ignored by the interpreter.
- **Example:**
  ```annoyscript
  ; This is a comment
  (<++++++++++++---.>)  ; This token pair outputs "H"
  ```

---

## Operations

Inside each token pair, you use various symbols that perform operations. The meaning of some symbols depends on the current *nesting depth* (top-level blocks are at depth 0, an even nesting level).

### Arithmetic Operations

- **`+` (Plus):**
  - **Even Nesting:** Increments the current cell’s value.
  - **Odd Nesting:** Decrements the current cell’s value.
  - **Chaining:** Multiple consecutive `+` symbols are not linear; the first adds 1, the second adds 2, the third adds 3, etc.
  
- **`-` (Minus):**
  - **Even Nesting:** Decrements the current cell’s value.
  - **Odd Nesting:** Increments the current cell’s value.
  - **Chaining:** Follows the same multiplicative rule as `+`.

### Pointer Overrides

- **`^`:**
  - **Even Nesting:** Moves the pointer one cell to the **right**.
  - **Odd Nesting:** Moves the pointer one cell to the **left**.
  
- **`v`:**
  - **Even Nesting:** Moves the pointer one cell to the **left**.
  - **Odd Nesting:** Moves the pointer one cell to the **right**.

*Note:* Pointer override symbols are cumulative and, if present in a token pair, override the default pointer movement after execution.

### I/O Operations

- **`.` (Period):**  
  Outputs the ASCII character corresponding to the value in the current cell.  
  - *Error:* If the value is not within the printable range (32–126), an error is raised.
  
- **`,` (Comma):**  
  Reads one character from input and stores its ASCII value in the current cell.

### Reset Operation

- **`#` (Hash):**  
  Resets the current cell’s value to zero.

---

## Pointer Movement

After every token pair (instruction), the interpreter updates the data pointer:

- **Default Movement:**  
  - If the instruction count is **odd**, move the pointer **left** by 1 (wrapping around from cell 0 to cell 127).
  - If the instruction count is **even**, move the pointer **right** by 1 (wrapping around as needed).

- **Override:**  
  - If the token pair contains any pointer override operations (`^` or `v`), the combined override value is applied instead of the default movement.

---

## Control Flow

- **Conditional Blocks:**  
  Conditional blocks use the token pair delimiters `(?` and `?)`.  
  - The condition is evaluated at the moment the block is encountered: if the current cell is nonzero, the block is executed; otherwise, it is skipped.
  - Nested conditional blocks are allowed.

---

## Error Handling

AnnoyScript’s interpreter will raise errors in several cases:

- **Syntax Errors:** Missing closing tokens, unexpected characters, or invalid token order produce “Syntax of Agony” errors.
- **Display of Dismay Errors:** Outputting a character from a cell whose value is outside the printable ASCII range (32–126) causes a runtime error.
- **Input Errors:** Failure to read input when expected produces an error.

Each error message is intentionally terse and unhelpful, contributing to the language’s overall frustration factor.

---

## Example: Outputting a Letter

Below is a short AnnoyScript program that outputs the letter **H** (ASCII code 72). This example uses a single, top-level (even nesting) token pair.

```annoyscript
; This token pair resets the cell, increments it to 72, then outputs "H"
(<#++++++++++++---.>)
```

**Explanation:**

1. **`#`**  
   - Resets the current cell (cell 0) to zero.
2. **`++++++++++++`**  
   - Twelve consecutive `+` symbols at even nesting:
     - The first `+` adds 1, the second adds 2, …, the twelfth adds 12.
     - Total addition: 1 + 2 + … + 12 = 78.
3. **`---`**  
   - Three consecutive `-` symbols at even nesting:
     - The first `-` subtracts 1, the second subtracts 2, the third subtracts 3.
     - Total subtraction: 1 + 2 + 3 = 6.
4. **Net Effect:**  
   - 78 − 6 = 72, which is the ASCII code for **H**.
5. **`.`**  
   - Outputs the character corresponding to the value in the current cell (72 → "H").

*Note:* The forced pointer movement happens after the token pair completes. Since this is the only token pair in the program, the output is not affected.

---

## Conclusion

AnnoyScript is a deterministic, yet maddeningly non‑linear language built as a challenge and a piece of art. Its strict syntax, context‑dependent operations, and forced pointer oscillation require careful planning and calculation, even for the simplest tasks.

Use this documentation as your guide to navigate the pain—and maybe even find a strange satisfaction—in programming AnnoyScript. Happy coding (or happy suffering)!
