# Rules of Value Assignment

Writing a program in Maya with PAC-1 interpreter just listing business logic in sequence in English language. Anyone who has written any program before would however ask for rules of assignment and use of `state` in the program. But before we get into understanding how we assign and use states in Maya we should first go through a primer on where these states are stored.

First up, ephemeral storage `contexts` . Maya workers can have three types of context stores within which state is assigned and manipulated:

1. **Node Context**: this one is an implicit context, any state assignment to a field of a node implicitly gets stored in the node context. Depending on how the node for which the assignment is done such state may or may not persist over worker runtime restarts. Conventionally, all fields default to a node’s configuration persist over worker runtime restart. However, an explicit usage of `node.<key name>` for state storage and manipulation does not persist over worker restart. Explicit assignment and manipulation of a node context is allowed only in a custom function node.
2. **Flow Context**: this context needs to be explicitly stated using `flow.<key name>` to assign or read any value to/from it. In the current version of Maya flow context is not different from Global context. Flow context does not persist over worker runtime restart.
3. **Global Context**: this context also needs to be explicitly stated using `global.<key name>` to assign or read any value to/from it. This states stored in this context are globally available to a worker at any stage of the execution. Global context does not persist over worker runtime restarts.

Secondly, `types` . Maya is loosely typed and performs a best guess to infer type of value assignment from user input in the instruction provided. However between a program graph execution would fail should the output of preceding step is not consistent of expected input type and signature of succeeding step. This is true for the ephemeral storage contexts too i.e. if a step is using a global state which was assigned by some preceding step in the program, and that step does not set the state to a type and signature of what was expected, program shall error out and cascade it till the end.

Lastly, the `msg` object. This is a special context which is the manifestation of execution flow in the flow based paradigm of programming with Maya. `msg` object is a javascript object which flows through the program graph carrying the states required by individual nodes that execute on the received input from this `msg` and also modifying it for successive steps of the program graph.

While it is the entirety of `msg` object which gets shuttled from one node to next in the program graph, the `payload` field in root of `msg` object is ***conventionally*** used as the principal operating state which takes input for a step (or a node) and modifies (if required) it for operating on rest of the program graph.

Now that those are covered let’s see how state assignment is done in Maya lang

- Assigning a string value in a step that takes a string as input
    
    ```python
    # in this example the search step takes a string input and that value is inferred from string provided between single quotes.
    ...
    3. In doc library search for 'Which month did we file the state compliance tax in 2021?'
    ...
    
    # if the input string contains a single quote, the quote in the string is recommended to be escaped
    ... 
        - 5.1. ...
        - 5.2. print 'What\'s up doc?' 
    ...
    
    ```
    
- Assigning a numerical value in a step that takes number as input
    
    ```python
    # in this example the loop step takes a number as input to define how many times the loop should run before exiting
    ...
    3. loop 40 times
    ...
    
    # ideally this same step responds word description of number too, but the confidence in such interpretations are lower than numeric input 
    ...
    3. loop forty times
    ...
    ```
    
- Assigning a JSON like object as input to a step takes such a script
    
    ```python
    # in this example we are sending a JSON or a complex data structure that is serializable as a string
    script="""
    ...
    3. set {{global.authorization}} as '{\"x-api-ley\":\"mayakey-$12f$123456789012\"}
    ...
    """
    ```
    It's always possible or easy to supply large JSON or python dictionary like objects in a string with escaped special characters. In such cases while using python SDK utilize string.format() method to substitute objects into string as follows
    ```python
    ...
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer mayakey-$512a$1234567801234567812345678"
    }
    ...

    script="""
    
    ...
    3. set {{global.authorization}} as '{header}'
    ...
    
    """.format(header=headers)
    ```
    here the python dictionary object self substitutes with escaped sequences and treated as input for the PAC-1 interpreter.