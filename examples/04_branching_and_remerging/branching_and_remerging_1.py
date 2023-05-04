import mayalabs

fn = mayalabs.Function(name="Branching_1")

mayalabs.log_level = "debug"
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