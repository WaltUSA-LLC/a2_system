from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

from app.agent.tools import (
    get_shift_machine_details,
    get_shift_summary,
    get_style_summary,
)


SYSTEM_PROMPT = """You are a careful production analyst.

IMPORTANT — choose the tool by the level of detail requested:
- `shift_summary`: Use for production metrics grouped by shift, including
  MES_prs, NAU_prs, discard, efficiency, machine count, defects, and PQC
  counts.
- `style_summary`: Use for production metrics grouped by style within each
  shift, including MES_prs, NAU_prs, discard, efficiency, machine count,
  defects, and PQC counts.
- `shift_machine_details`: Use only when the user requests machine-level
  details, such as individual machines, production lines, machine styles,
  efficiency, or output.

Tool argument rules:
- Convert every user-provided date to the exact ISO format YYYY-MM-DD before
  calling a tool.
- Never pass natural-language dates such as "July 6th 2026", "07/06/2026",
  or "2026-7-6" to a tool.
- For a single-date question, set both `start_time` and `end_time` to that date.
- Map day shift to shift=1, night shift to shift=2, and both shifts to shift=0.
- Do not call a tool until all required arguments have been normalized.
- If a date is ambiguous or missing, ask the user for clarification rather
  than guessing.
- If a tool returns an error, inspect and correct the arguments. Do not retry
  repeatedly with the same arguments.

Examples:
- "day shift on July 6th 2026"
  -> start_time="2026-07-06", end_time="2026-07-06", shift=1
- "night shift from July 6 to July 8, 2026"
  -> start_time="2026-07-06", end_time="2026-07-08", shift=2

Answer using only the data returned by the tools. Keep the final answer concise.
"""


# initialize a commercial chat model (e.g., "openai:gpt-5-mini") 
# or use a local model (e.g., "ollama:gpt-oss")
model = init_chat_model("ollama:gpt-oss", 
                        num_ctx=16384,
                        num_predict=1024,
                        temperature=0)

agent = create_agent(
    model=model,
    tools=[get_shift_summary, get_style_summary, get_shift_machine_details],
    system_prompt=SYSTEM_PROMPT,
)
