# Maya Labs SDK

The Maya Labs Python SDK provides easy async access to our PAC-1 program synthesis engine, with a CLI to instruct and generate programs from instructions in natural language.

Check out the [examples](/examples) folder for use cases, and read more about PAC-1 on our [blog](https://mayalabs.io/pac-1).

## Installation

```
pip install --upgrade mayalabs
```

## Usage

Get the Maya Labs API key from the Settings > Developer [section](https://app.mayalabs.io/settings/developers).

```
export MAYA_API_KEY = "mayakey-..."
```

Or set `mayalabs.api_key` to its value:

```
from mayalabs import Function

mayalabs.api_key = "<MAYA_API_KEY>"

script = """
1. trigger on receive
2. scrape wikipedia for {{term}}
3. create a summary in 200 words
4. send response back
"""

function = Function.create(name="Scrape", script="script")

function.deploy()
# Generating program...
# Starting worker...
# Installing dependencies...
# Deployed!

function.call({ "term" : "Dr. Homi Bhabha"})
# finds and outputs a summary of the first matching wiki page
```

PAC-1 takes in steps written in English, writes & assembles a discrete program graph, and deploys ready-to-use software on our compute infrastructure, that you can call within your code. You can set up missing dependencies / visualize the flow of logic by following the link to flow-based editor it provides after deployment.

## Use Cases

- [If...Then Conditionals and Looping](/EXAMPLES.md#ifthen-conditionals-and-looping)
- [Custom Functions](/EXAMPLES.md#custom-functions)
- [Web Scrapers](/EXAMPLES.md#web-scrapers)
- [Repeating Workflows](/EXAMPLES.md#repeating-workflows)
- [Custom Dashboards](/EXAMPLES.md#custom-dashboards)
- [Data Transformation](/EXAMPLES.md#data-transformation)
- [Platform Bots](/EXAMPLES.md#platform-bots)
- [Complex Processes](/EXAMPLES.md#complex-processes)
- [Long-term memory](/EXAMPLES.md#long-term-memory)
- [Division of labour](/EXAMPLES.md#division-of-labour)
  - [Parallelization](/EXAMPLES.md#parallelization)
  - [Concurrency](/EXAMPLES.md#concurrency)

## Command Line Usage

Today, script need to be manually written step-by-step, but we are offering early WIP preview of iterative script generation via our CLI. Try running:

```
$ mayalabs instruct -c 'fetch Name and Email from gsheet, write function to merge all columns, and return data'
```

And then use the generated script as function.

## Development

To test and develop natural language functions iteratively, just set environment variable `MAYA_ENVIRONMENT` to `development`.

```
os.environ["MAYA_ENVIRONMENT"] = "development"
```

This ensures our program synthesis engine only incremental generates and deploys changes you make to the script, instead of deploying from scratch.

## Requirements

- Python 3.7.1+

## Issues

All feedback and bug reports welcome! Report in the [issues section](https://github.com/mayahq/mayalabs-sdk-python/issues), or mail us at humans@mayalabs.io.
