import asyncio
import sys
import traceback

from beeai_framework.backend import ChatModel
from beeai_framework.emitter import EmitterOptions
from beeai_framework.errors import FrameworkError
from beeai_framework.tools.search.wikipedia import WikipediaTool
from beeai_framework.tools.weather import OpenMeteoTool
from beeai_framework.workflows.agent import AgentWorkflow, AgentWorkflowInput
from examples.helpers.io import ConsoleReader


async def main() -> None:
    llm = ChatModel.from_name("ollama:granite3.3:8b")
    workflow = AgentWorkflow(name="Smart assistant")
    reader = ConsoleReader()

    workflow.add_agent(
        name="Researcher",
        role="A diligent researcher",
        instructions="You look up and provide information about a specific topic.",
        tools=[WikipediaTool()],
        llm=llm,
    )

    workflow.add_agent(
        name="WeatherForecaster",
        role="A weather reporter",
        instructions="You provide detailed weather reports.",
        tools=[OpenMeteoTool()],
        llm=llm,
    )

    workflow.add_agent(
        name="DataSynthesizer",
        role="A meticulous and creative data synthesizer",
        instructions="You can combine disparate information into a final coherent summary.",
        llm=llm,
    )

    location = "Saint-Tropez"

    await (
        workflow.run(
            inputs=[
                AgentWorkflowInput(
                    prompt=f"Provide a short history of {location}.",
                ),
                AgentWorkflowInput(
                    prompt=f"Provide a comprehensive weather summary for {location} today.",
                    expected_output="Essential weather details such as chance of rain, temperature and wind. Only report information that is available.",
                ),
                AgentWorkflowInput(
                    prompt=f"Summarize the historical and weather data for {location}.",
                    expected_output=f"A paragraph that describes the history of {location}, followed by the current weather conditions.",
                ),
            ]
        )
        .on(
            # Event Matcher -> match agent's 'success' events
            lambda event: isinstance(event.creator, ChatModel) and event.name == "success",
            # log data to the console
            lambda data, event: reader.write(
                "->Got response from the LLM",
                "  \n->".join([str(message.content[0].model_dump()) for message in data.value.messages]),
            ),
            EmitterOptions(match_nested=True),
        )
        .on(
            "success",
            lambda data, event: reader.write(
                f"->Step '{data.step}' has been completed with the following outcome.\n\n{data.state.final_answer}\n\n",
                data.model_dump(exclude={"data"}),
            ),
        )
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except FrameworkError as e:
        traceback.print_exc()
        sys.exit(e.explain())
