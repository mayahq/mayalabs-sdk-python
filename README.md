# Maya Labs : Program machines using natural language.

<p align="left">
  <a href="https://pypi.org/project/mayalabs">
    <img src="https://img.shields.io/pypi/v/mayalabs?style=for-the-badge" />
  </a>
  <a href="https://mayalabs.io/docs">
    <img src="https://img.shields.io/badge/Documentation-blue?logo=GitBook&logoColor=white&style=for-the-badge" />
  </a>
</p>
<br>

The Maya Labs Python SDK provides easy async access to our PAC-1 program synthesis engine, with a CLI to instruct and generate programs from instructions in natural language.

## Installation

```
pip install --upgrade mayalabs
```
## Preview

https://user-images.githubusercontent.com/52493077/233965080-856dcad6-12ab-4412-8fae-2a4e98ec51e3.webm


## Usage

Get the Maya Labs API key from the Settings > Developer [section](https://app.mayalabs.io/settings/developers).

```
export MAYA_API_KEY = "mayakey-..."
```

Or set `mayalabs.api_key` to its value:

```
import mayalabs

mayalabs.api_key = "mayakey-..."

script = """
1. trigger on receive
2. research {{term}} on wikipedia
3. extract 'title' and 'summary' from tabular data
4. send response back
"""

function = mayalabs.Function(name="Scrape2")
# Creating new worker...

function.update(script=script)
# Generating program graph...
# Starting worker...
# Installing dependencies...
# Deployed!

output = function.call({"term": "Dr. Vikram Sarabhai"})
print(output)
# finds and outputs title and summary from wikipedia results

```

PAC-1 takes in steps written in English, writes & assembles a discrete program graph, and deploys ready-to-use software on our compute infrastructure, that you can call within your code. You can set up missing dependencies / visualize the flow of logic by following the link to flow-based editor it provides after deployment.

Check our [documentation]("https://mayalabs.io/docs") for more usage and tutorials.

## Use Cases

- [If...Then Conditionals and Looping](/EXAMPLES.md#ifthen-conditionals-and-looping)
- [Custom Functions](/EXAMPLES.md#custom-functions)
- [Web Scrapers](/EXAMPLES.md#web-scrapers)
- [Repeating Workflows](/EXAMPLES.md#repeating-workflows)
- [Custom Dashboards](/EXAMPLES.md#custom-dashboards)
- [Data Transformation](/EXAMPLES.md#data-transformation)
- [Platform Bots](/EXAMPLES.md#platform-bots)
- [Business Processes](/EXAMPLES.md#business-processes)
- [Long-term memory](/EXAMPLES.md#long-term-memory)

## Command Line Usage

Today, script need to be manually written step-by-step, but we are offering early WIP preview of iterative script generation via our CLI. Try running:

```
$ mayalabs instruct -c 'fetch Name and Email from gsheet, write function to merge all columns, and return data'
```

And then use the generated script as function.

https://user-images.githubusercontent.com/52493077/231979284-a7d1c43d-f6c6-4726-89fe-28e103cd198f.mp4

## Requirements

- Python 3.7.1+

## Issues

All feedback and bug reports welcome! Report in the [issues section](https://github.com/mayahq/mayalabs-sdk-python/issues), or mail us at humans@mayalabs.io.

Full list of capabilities and limits [here](https://docs.mayalabs.io/capabilities-and-limits).


## Roadmap
- [x] Cleaner logs and exception handling
- [x] Dependency configuration UX improvement
- [ ] Import skill repositories for reusing skills created by user or present in store
- [ ] Create and call downstream auto-deployed functions
- [ ] Allow multi-profile and team profile access
