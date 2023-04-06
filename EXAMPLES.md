# Use Cases

The PAC-1 natural language interpreter can assemble natural language programs across a wide range of useful tasks and applications. It comes equipped with a standard library of functions that can be indefinitely extended and built on top of. Here are a few examples :

## Index

- [If...Then Conditionals and Looping](#ifthen-conditionals-and-looping)
- Custom Functions
- Web Scrapers
- Repeating Workflows
- Custom Dashboards
- Data Transformation
- Platform Bots
- Complex Business Processes
- Long-term memory
- Division of labour
  - Parallelization
  - Concurrency

---

### If...Then Conditionals and Looping

A simple if...then else switch, with a loop written in English.

```
1. set {{payload}} to 0
2. add 1 to {{payload}}
3. print {{payload}}
4. if {{payload}} is less than 20
    - 4.1. go to step 2
5. else if {{payload}} is more than 20
    - 4.2. print {{payload}}
```

### Custom Functions

PAC-1 uses code generation models for synthesising Javascript and Python functions for simple variable manipulation.

```
1. trigger on recieve
2. make a GET request to '<apilink>'
3. run a custom function to 'add 5 to every element of {{payload}}'
4. send response back
```

### Web Scrapers

Fetching data from a source, and splitting it into three branches that go scrape the web, and display results in a table.

```
1. from gsheet get {{Name}}, {{Website}}, {{Company}}, {{Email}}, {{Linkedin}}
2. split data into batches and send at intervals of 2 seconds
    - 2.1. scrape and extract title, description and text from {{Website}}
        2.1.1. go to step 3
    - 2.2. scrape and extract text from {{Linkedin}}
        2.2.1. go to step 3
    - 2.3. store {{Company}} in {{company}}
        2.3.1. go to step 3
3. show in a table with button Research
```

### Repeating Workflows

Creating scripts that run once and automatically having them repeat at arbitrary intervals, with just one step added in the beginning.

```
1. repeat every 5 days
2. fetch weekly mongo records for collection synth-db
3. save to s3 bucket 'synth-db-backup'
```

### Custom Dashboards

Modelling interactive UI components like tables, rich-text, forms, buttons, templates, images, which can be used in the beginning of a script:

```
// create a form to put data into spreadsheet

1. create a form with fields {{Name}}, {{Age}}, {{Occupation}}
2. put Name, Age, Occupation into gsheet
```

Or interspersed in between steps.

```
// create a dashboard to ask questions about an SQL db
// and

1. add a button with label 'fetch schema'
   - 1.1. connect to a MySQL Database and store it's create schema in {{schema}}
     1.2. store {{schema}} in flow.{{context}}
2. show a text editor to take input {{input}}
3. create sql query to get {{input}} using {{schema}}
4. show a text editor to show {{query}}
5. run sql query {{query}} on MySQL
6. show results in table with button 'Submit'
```

### Data Transformation

Moving data from one data source to another, and modifying in between by just adding a few display steps.

For instance, here's a natural language script to move some columns from SQL to Gsheet.

```
1. from SQL fetch 'all users who live in Bangalore'
2. put all data into gsheet
```

Which can be changed into an interactive dashboard by adding three lines in between, for showing the data in a table and modifying it item-wise in a form.

```
1. from SQL fetch 'all users who live in Bangalore'
2. show in a table with button labelled Modify
   - 2.1. edit in a form with fields User, Name, Email
     2.1. go to step 3
3. put all data into gsheet
```

### Platform Bots

A Reddit bot that filters and sends messages to a Slack bot.

```
1. search subreddit r/dankmemes for 'automation', order by top daily
2. filter out all messages that include ["BOTS", "AMA"]
2. send to channel #alerts on slack
```

### Long Business Processes

PAC-1 can be taught and interpret to scripts of arbitrary complexity and length, extending to complex business processes.

For instance, the script below automates a sales process of fetching leads from a google sheet, researching them on the web, composing blurbs to place in the mails based on some email templates it's been shown before.

```
1. from gsheet get {{Name}}, {{Website}}, {{Company}}, {{Email}}, {{Linkedin}}
2. split data into batches and send at intervals of 2 seconds
    - 2.1. scrape and extract title, description and text from {{Website}}
        2.1.1. go to step 3
    - 2.2. scrape and extract text from {{Linkedin}}
        2.2.1. go to step 3
    - 2.3. store {{Company}} in {{company}}
        2.3.1. go to step 3
3. show in a table with button Research
4. create a research prompt with instructions "Write a 100 word blurb on {{company}}"
    - 4.1. show in text editor
    4.2. go to step 5
5. generate using large model
    - 5.1. show in text editor
    5.2. go to step 5.2.1
        5.2.1. set {{global.CompanyBlurb}} to {{msg.payload.completed}}, delete {{global.CompanyInfo}}, delete {{msg.payload.completed}}
        5.2.2. go to step 5.2.3.
        - 5.2.3. AI email template search in doc library
            - 5.2.3.1. go to step 6
        - 5.2.4. Search company info in doc library
            5.2.4.1 check search query results
            5.2.4.2. if {{condition}} is Bad
                - 5.2.4.2.1. rephrase search query
                5.2.4.2.2. Loop thrice before breaking
                5.2.4.2.3 go to step 5.2.
            5.2.4.3. else if {{condition}} is Good
                - 5.2.4.3.1. go to step 6
6. combine messages
7. create an email prompt with blurb from {{CompanyBlurb}} and description from {{CompanyInfo}} to "Write an email for {{Company}} in {{FromCompany}}'s perspective"
    - 7.1. show in text editor
    7.2. generate using large model
    7.3 go to step 8
8. show output in editor
```

### Long-term memory

PAC-1 can generating programs to selectively call its own API - in this case it's own native vector database, allowing for long-term storage and retrieval of knowledge.

```
// A command to store any document in a persistent database for later recall.
1. store {{payload}} in native memory

// Commands to search and ask questions from the stored documents, like this:
1. search native memory for 'emailing templates'
2. ask native memory 'What was the last internal memo?"
```

Persisting information and use it later across Workers and programs, like this :

```
// Worker 1
1. research 'Nelson Mandela' on wikipedia
2. store {{payload}} to native memory

// Worker 2
1. search native memory for 'Nelson Mandela monuments'
2. create a prompt to "write a 100 word essay about the monuments named after nelson mandela"
3. generate using a large language model
```

### Division of Labour

Since PAC-1 can call its own API, Maya Workers can requisition other workers, deploy custom software on them, and instruct each other to make changes.

For instance, take this simple task that fetches certain data from SQL every day and sends it to a slack channel :

```
// every day at 5pm, fetch all users who signed up today and send to channel #insights on slack
1. repeat every day at 5pm
2. connect to a MySQL Database and store it's create schema in {{schema}}
3. store {{schema}} in flow.{{context}}
4. create sql query to run 'fetch all users who signed up today' using {{schema}}
5. send to slack channel #insights
```

#### Parallelization

If you wanted to try instantiate different variations of this task in one go in parallel, you could just teach PAC-1 a script to spawn new workers :

```
// fetch relevant user insights and send alerts to slack
1. add a button with label 'Spawn Workers'
	- 1.1. spawn a worker 'ABC' to run 'fetch all the users who signed up and send to channel #growth on slack, every day at 8pm'
    - 1.2. spawn a worker 'DEF' which runs 'fetch all the users who churned this week and send to channel #growth on slack, every week on Monday'
    - 1.3. spawn a worker 'GHI' which runs 'fetch all users in the schema and send to channel #marketing on slack'
```

#### Concurrency

Tasks can also be broken down and distributed concurrently amongst workers, so they function as an assembly line, like this script that splits the task of creating a report on the product sales every month :

```
1. add a button with label 'Create Workers'
    - 1.1. spawn a worker 'ABC' to run "query SQL to fetch all products that sold more than 5000 units this month"
         1.1.2. go to step 2
    - 1.2. create worker 'DEF' to run 'create a PDF report based on the tabular data in {{rowData}}'
        1.2.2. go to step 2
2. call worker 'ABC'
3. set {{rowData}} to {{payload}}
4. call worker 'DEF' with {{rowData}}
5. print {{payload}}
6. repeat every month, second Saturday
	- 5.1. send instruction 'add 1000 to units value to be checked'
         5.2. go to step 2
```
