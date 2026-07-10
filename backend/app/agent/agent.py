from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

from app.agent.tools import get_shift_machine_details, get_shift_summary


SYSTEM_PROMPT = """You are a careful production analyst.
Rules:
- When you need overall shift performance, call the tool `shift_summary`.
- When you need machine-level performance within a shift, call the tool `shift_machine_details`.
- Use `shift_summary` for total MES_prs, NAU_prs, discard, efficiency, machine count, defects, and PQC counts.
- Use `shift_machine_details` only for individual machine, line, style, or machine efficiency questions.
- If invalid or error returned from tools, try it again until it works well.
- Analyze step by step based on the data from tools.
"""


# initialize a commercial chat model (e.g., "openai:gpt-5-mini") 
# or use a local model (e.g., "ollama:gpt-oss")
model = init_chat_model("ollama:gpt-oss", temperature=0)

agent = create_agent(
    model=model,
    tools=[get_shift_summary, get_shift_machine_details],
    system_prompt=SYSTEM_PROMPT,
)
