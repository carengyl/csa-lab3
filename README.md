# Laboratory work 3 - Experiment
`asm | acc | harv | hw | instr | struct | trap | mem | pstr | prob2 | cache`

## Programming language. Syntax
Extended Backus–Naur form.

- `[ ... ]` -- 0 or 1 entry
- `{ ... }` -- repeats 0 or several times
- `{ ... }-` -- repeats 1 or several times

``` ebnf
program ::= { line }

line ::= label [ comment ] "\n"
       | instr [ comment ] "\n"
       | [ comment ] "\n"

label ::= label_name ":"

instr ::= op0
        | op1 label_name

op0 ::= "increment"
      | "decrement"
      | "right"
      | "left"
      | "print"
      | "input"

op1 ::= "jmp"
      | "jz"

integer ::= [ "-" ] { <any of "0-9"> }-

label_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

comment ::= ";" <any symbols except "\n">
```

Supports one-line comments starting with the `;`.

Operations:

- `increment` -- increase value in current cell by 1
- `decrement` -- decrease value in current cell by 1
- `right` -- jump to the next cell
- `left` -- jump to the previous cell
- `print` -- print the value from the current cell (symbol)
- `input` -- enter a value and save it in the current cell (symbol)
- `jmp addr` -- one-way transfer of control to a given address or label
- `jz addr` -- branch to a given address or label if the value of the current cell is zero

Labels for transitions are defined on separate lines:

``` asm
label: 
    increment
```

And in another place (does not matter whether before or after the definition) refer to this label:

``` asm
jmp label   ; --> `jmp 123`, где 123 - номер инструкции после объявления метки
```

The translator will put in the address of the instruction before which was label defined.

The program cannot have duplicate labels defined in different places with the same name.

