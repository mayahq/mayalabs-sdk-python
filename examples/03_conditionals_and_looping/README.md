### If...Then Conditionals and Looping

A simple if...else flow, with a loop written in English. Maya and PAC-1 utlizes an assembly style `go to` to direct a program flow execution to a preceding or jump over a succeeding step. Looping, hence is just `if ... otherwise` conditional checks on `go to` checkpoints.

```python
1. trigger on receive message
2. set {{msg.payload}} to '{"num": 29}'
3. add 1 to {{msg.payload.num}}
4. print {{msg.payload.num}}
5. if {{msg.payload.num}} is less than 36
    - 5.1. go to step 3
6. if {{payload.num}} is more than 36
    - 6.1. print {{msg.payload.num}}
7. respond back with {{msg.payload}}
```

Maya with PAC-1 interpreter doesn't have an `else if ...` paradigm and utilizes multiple `if ... else` to bring the same effects.

```python
1. trigger on receive message
2. if {{msg.payload.num}} is less or equal to 18
    - 2.1 set {{msg.payload.response}} to "Number less than or equal to 18"
    2.2. print "Number less than or equal to 18"
3. if {{msg.payload.num}} is less than 36
    - 3.1 set {{msg.payload.response}} to "Number less than 36"
    3.2. print "Number less than 36"
4. set {{msg.payload.response}} to "Number greater than or equal to 36"
5. print "Number is greater than or equal to 36"
7. respond back with {{msg.payload}}
```