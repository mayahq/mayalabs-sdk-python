### Branching and recombining split data

Maya with PAC-1 follows a flow based programming (FBP) paradigm. One of the core strengths in an FBP system is to branch out and merge back provided data is not corrupted for the succeeding logic unit. Maya with PAC-1 has attempted to create a synatactical structure to define such an FBP in natural language sequence code.

The branching syntax in Maya with PAC-1 works on three special character (or character classes). 
- 1. Identation: a step starting from 4-indentation on right from the start position of previous step is considered a branch-out

- 2. `-` dash symbol on an indented step refers to parallel child branches from a preceding step
- 3. Numeric step identification with `.` dot symbol: The steps are identified for readability and sequential clarity using bulleted numbering system (1., 1.1., 2., 2.1, 2.1.1, etc.)

The branched scripts can get a bit unruly and unreadable. The following examples should help understand implementation of branching in Maya with PAC-1 interpreter:

```python
import mayalabs

fn = mayalabs.Function(name="Branching_1")

script = """
1. trigger on receive
2. branch out
    - 2.1. extract 'text' from {{msg.payload.wikipedia}}
        - 2.1.1. set {{msg.payload.webExtract.wikitext}} to {{msg.payload.webExtract.text}}
        2.1.2. go to step 3.
        - 2.1.3. print {{msg.payload.webExtract}}
        - 2.1.4. set {{global.wikipedia}} to {{msg.payload.webExtract}}
    - 2.2. extract 'description and text' from {{msg.payload.academic}}
        - 2.2.1. set {{msg.payload.webExtract.acadtext}} to {{msg.payload.webExtract.text}}
        2.2.2. set {{msg.payload.webExtract.acadDesc}} to {{msg.payload.webExtract.description}}
        2.2.3. go to step 3.
        - 2.2.4. print {{msg.payload.webExtract}}
    - 2.3. extract 'text' from {{msg.payload.google_research}}
        - 2.3.1. set {{msg.payload.webExtract.googletext}} to {{msg.payload.webExtract.text}}
        2.3.2. go to step 3.
        - 2.3.3. print {{msg.payload.webExtract}}
3. combine messages in {{msg.payload.webExtract}}
4. respond back with {{msg.payload.webExtract}}
"""
input = {
    "name": "Geoffrey Hinton",
    "age": "75",
    "wikipedia": "https://en.wikipedia.org/wiki/Geoffrey_Hinton",
    "academic" : "https://www.cs.toronto.edu/~hinton/",
    "google_research" : "https://research.google/people/GeoffreyHinton/"
}

fn.update(script=script)

output = fn.call(payload=input)

```
The objective of above program is to extract required information from static HTML hosted on the URLs in the input object. The program structure is such that task of scraping the said information is performed in parallel.

This example helps elucidate few key concepts regarding branching and recombination of split branches when working on Maya with PAC-1 interpreter.

There are two ways to branch with multiple children path from a logical step:
1. With `branch out` step
   The `branch out` step adds a unique marker to the copies of the message object being sent down to the child paths. This marker is used by the `combine` step to wait for all messages with same marker to arrive before pushing it ahead.
2. Without `branch out` step
   This pattern is useful when we do not foresee a recombination of split data in successive steps. 

Hence, the step 2. `branch out` is required only if we want to recombine the data from split paths again down the succession of logic, as we see is done in our example in step 3.

Now let's pay attention to succession from steps `2.1` to `- 2.1.1` and `2.1.2.` This pattern is suggests that the step `2.1` creates at least one child branch (starting with `2.1.1.`) which continues independently till `2.1.2` and stops execution at that point. 
The steps `- 2.1.3.` and `- 2.1.4` are parallel branches to branch started by `- 2.1.1`

In such cases `go to` step is used to move the flow of data and execution flow to desired step(s). In the case of example above, `go to` is used as jump step to bring all the results of split branches back for recombination.