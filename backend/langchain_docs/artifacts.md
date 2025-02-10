How to return artifacts from a tool
Prerequisites
This guide assumes familiarity with the following concepts:

ToolMessage
Tools
Function/tool calling
Tools are utilities that can be called by a model, and whose outputs are designed to be fed back to a model. Sometimes, however, there are artifacts of a tool's execution that we want to make accessible to downstream components in our chain or agent, but that we don't want to expose to the model itself. For example if a tool returns a custom object, a dataframe or an image, we may want to pass some metadata about this output to the model without passing the actual output to the model. At the same time, we may want to be able to access this full output elsewhere, for example in downstream tools.

The Tool and ToolMessage interfaces make it possible to distinguish between the parts of the tool output meant for the model (this is the ToolMessage.content) and those parts which are meant for use outside the model (ToolMessage.artifact).

Requires langchain-core >= 0.2.19
This functionality was added in langchain-core == 0.2.19. Please make sure your package is up to date.

Defining the tool
If we want our tool to distinguish between message content and other artifacts, we need to specify response_format="content_and_artifact" when defining our tool and make sure that we return a tuple of (content, artifact):

%pip install -qU "langchain-core>=0.2.19"

import random
from typing import List, Tuple

from langchain_core.tools import tool

@tool(response*format="content_and_artifact")
def generate_random_ints(min: int, max: int, size: int) -> Tuple[str, List[int]]:
"""Generate size random ints in the range [min, max]."""
array = [random.randint(min, max) for * in range(size)]
content = f"Successfully generated array of {size} random ints in [{min}, {max}]."
return content, array

API Reference:tool
Invoking the tool with ToolCall
If we directly invoke our tool with just the tool arguments, you'll notice that we only get back the content part of the Tool output:

generate_random_ints.invoke({"min": 0, "max": 9, "size": 10})

'Successfully generated array of 10 random ints in [0, 9].'

Failed to batch ingest runs: LangSmithRateLimitError('Rate limit exceeded for https://api.smith.langchain.com/runs/batch. HTTPError(\'429 Client Error: Too Many Requests for url: https://api.smith.langchain.com/runs/batch\', \'{"detail":"Monthly unique traces usage limit exceeded"}\')')

In order to get back both the content and the artifact, we need to invoke our model with a ToolCall (which is just a dictionary with "name", "args", "id" and "type" keys), which has additional info needed to generate a ToolMessage like the tool call ID:

generate_random_ints.invoke(
{
"name": "generate_random_ints",
"args": {"min": 0, "max": 9, "size": 10},
"id": "123", # required
"type": "tool_call", # required
}
)

ToolMessage(content='Successfully generated array of 10 random ints in [0, 9].', name='generate_random_ints', tool_call_id='123', artifact=[2, 8, 0, 6, 0, 0, 1, 5, 0, 0])

Using with a model
With a tool-calling model, we can easily use a model to call our Tool and generate ToolMessages:

Select chat model:
pip install -qU langchain-openai

import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

llm_with_tools = llm.bind_tools([generate_random_ints])

ai_msg = llm_with_tools.invoke("generate 6 positive ints less than 25")
ai_msg.tool_calls

[{'name': 'generate_random_ints',
'args': {'min': 1, 'max': 24, 'size': 6},
'id': 'toolu_01EtALY3Wz1DVYhv1TLvZGvE',
'type': 'tool_call'}]

generate_random_ints.invoke(ai_msg.tool_calls[0])

ToolMessage(content='Successfully generated array of 6 random ints in [1, 24].', name='generate_random_ints', tool_call_id='toolu_01EtALY3Wz1DVYhv1TLvZGvE', artifact=[2, 20, 23, 8, 1, 15])

If we just pass in the tool call args, we'll only get back the content:

generate_random_ints.invoke(ai_msg.tool_calls[0]["args"])

'Successfully generated array of 6 random ints in [1, 24].'

If we wanted to declaratively create a chain, we could do this:

from operator import attrgetter

chain = llm_with_tools | attrgetter("tool_calls") | generate_random_ints.map()

chain.invoke("give me a random number between 1 and 5")

[ToolMessage(content='Successfully generated array of 1 random ints in [1, 5].', name='generate_random_ints', tool_call_id='toolu_01FwYhnkwDPJPbKdGq4ng6uD', artifact=[5])]

Creating from BaseTool class
If you want to create a BaseTool object directly, instead of decorating a function with @tool, you can do so like this:

from langchain_core.tools import BaseTool

class GenerateRandomFloats(BaseTool):
name: str = "generate_random_floats"
description: str = "Generate size random floats in the range [min, max]."
response_format: str = "content_and_artifact"

    ndigits: int = 2

    def _run(self, min: float, max: float, size: int) -> Tuple[str, List[float]]:
        range_ = max - min
        array = [
            round(min + (range_ * random.random()), ndigits=self.ndigits)
            for _ in range(size)
        ]
        content = f"Generated {size} floats in [{min}, {max}], rounded to {self.ndigits} decimals."
        return content, array

    # Optionally define an equivalent async method

    # async def _arun(self, min: float, max: float, size: int) -> Tuple[str, List[float]]:
    #     ...

API Reference:BaseTool
rand_gen = GenerateRandomFloats(ndigits=4)
rand_gen.invoke({"min": 0.1, "max": 3.3333, "size": 3})

'Generated 3 floats in [0.1, 3.3333], rounded to 4 decimals.'

rand_gen.invoke(
{
"name": "generate_random_floats",
"args": {"min": 0.1, "max": 3.3333, "size": 3},
"id": "123",
"type": "tool_call",
}
)

ToolMessage(content='Generated 3 floats in [0.1, 3.3333], rounded to 4 decimals.', name='generate_random_floats', tool_call_id='123', artifact=[1.5789, 2.464, 2.2719])
