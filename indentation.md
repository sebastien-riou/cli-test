# Indentation

## Indentation stripping rules
A block is processed in two steps:

- stripping of the 'block level indendation'
- stripping of the 'content level indentation'

'block level indentation' is defined as the start of the line until the last character before `cli-test-cmd`.
It may contain ANY characters, including non white characters.

'content level indentation' is defined by the line immediatly below `cli-test-cmd`, after stripping the 'block level indentation'. It is defined as all white characters before the first non white character.

## Indentation examples
In all examples below, the expected output is ' he'.

### raw text, no indentation
````
cli-test-cmd
echo ' he'
cli-test-out
 he
cli-test-end
````

- block level indendation is ''
- content level indentation is ''

### raw text, indentation with white space
````
    cli-test-cmd
    echo ' he'
    cli-test-out
     he
    cli-test-end
````

- block level indendation is '    '
- content level indentation is ''

### raw text, indentation with white space and extra indentation of content
````
    cli-test-cmd
        echo ' he'
    cli-test-out
         he
    cli-test-end
````

- block level indendation is '    '
- content level indentation is '    '


### line comment, no indentation
````
#cli-test-cmd
#echo ' he'
#cli-test-out
# he
#cli-test-end
````

- block level indendation is '#'
- content level indentation is ''

### raw text, indentation with white space
````
#    cli-test-cmd
#    echo ' he'
#    cli-test-out
#     he
#    cli-test-end
````

- block level indendation is '#    '
- content level indentation is ''

### raw text, indentation with white space and extra indentation of content
````
#    cli-test-cmd
#        echo ' he'
#    cli-test-out
#         he
#    cli-test-end
````

- block level indendation is '#    '
- content level indentation is '    '