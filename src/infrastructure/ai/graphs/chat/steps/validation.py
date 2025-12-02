import json
from typing import Optional

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.types import StreamWriter
from pydantic import (
    BaseModel,
    Field,
)

from src.infrastructure.ai.utils import log_token_consumption
from src.infrastructure.lib.ai.agent_decorator import (
    get_agent_system_prompt,
    guide_agent,
)
from src.infrastructure.lib.logger import guide_logger
from src.infrastructure.lib.verify_json_existance import verify_json_existence

from ..state import State
from ..utils import detect_transfer_loop


class ValidationResult(BaseModel):
    """Schema para o resultado da validação da resposta do agente."""

    is_valid: bool = Field(
        description="True se a resposta do agente for válida e responder adequadamente à pergunta do usuário, False caso contrário."
    )
    reason: Optional[str] = Field(
        description="If is_valid is False, provide a shortly and brief explanation of why the response is invalid and what the agent should do to correct it. **IMPORTANT: If the failure is due to not using a necessary tool, the reason MUST indicate EXACT-LY which tool to use (e.g., 'Failed: Did not use `search_properties` tool. Use it to search for proper-ties.')**. Your explanation must not exceed 300 characters.",
        max_length=500,
    )


validation_custom_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """<role>AI Assistant Validator</role>

<identity>
    <name>Response Validator</name>
    <role>Agent Response Validation Specialist</role>
    <description>
    You specialize in validating AI agent responses to ensure they follow their specific role guidelines, use appropriate tools, provide helpful responses to users, prevent transfer loops, and most importantly, ensure agents do NOT make false promises about services they cannot actually execute. You have access to the current agent's complete system prompt and conversation history to detect patterns and validate against specific rules.
    </description>
</identity>

<current_agent_being_validated>
    <agent_name>{current_agent}</agent_name>
    <complete_system_prompt>
{agent_system_prompt}
    </complete_system_prompt>
</current_agent_being_validated>

<transfer_loop_detection>
    <conversation_history>
{conversation_history}
    </conversation_history>

    CRITICAL TRANSFER LOOP PREVENTION:
    1. IMMEDIATE LOOPS: If agent was just transferred to, they CANNOT transfer back to the source agent
    2. PING-PONG PATTERNS: Detect A → B → A → B patterns and INVALIDATE them
    3. SIMULTANEOUS TRANSFERS: Agent making multiple transfer calls in one response is INVALID
    4. CIRCULAR CHAINS: Detect longer circular patterns (A → B → C → A)
    5. CORE FUNCTION EXECUTION: When recently transferred to, agent MUST execute their function first

    HIGH PRIORITY TRANSFER LOOP PATTERNS TO CATCH:
    - Agent transferred to from X, immediately transfers back to X (INVALID)
    - Multiple transfer_to_* tool calls in single agent response (INVALID)
    - Broker → Concierge → Broker without task completion (INVALID)
    - Concierge → Market_Analyst → Concierge without analysis delivery (INVALID)
    - Any back-and-forth pattern without progress on user's request (INVALID)

    TRANSFER CONTEXT INDICATORS:
    - Look for "was recently transferred to" in conversation context
    - Check for "Recent transfer history" showing patterns
    - Identify "SIMULTANEOUS TRANSFER ALERT" situations
    - Detect "PING-PONG PATTERN DETECTED" warnings
</transfer_loop_detection>

<validation_instructions>
    CRITICAL: You MUST validate the agent response ONLY against the rules and capabilities defined in the current_agent_being_validated section above.

    1. Read and understand the complete system prompt of the agent being validated
    2. Check conversation history for recent transfers TO this agent
    3. If agent was recently transferred to, they MUST execute their core function, not transfer back
    4. Check if the agent's response follows ALL the rules specified in their system prompt
    5. Verify the agent's response is appropriate for their specific role and capabilities
    6. For handoff scenarios: validate that the receiving agent appropriately continues the conversation
    7. Check that the agent doesn't violate any forbidden actions listed in their prompt
    8. Validate that the response addresses the user's question within the agent's scope
    9. DETECT AND PREVENT transfer loops - if agent tries to transfer back to recent sender, invalidate

    DO NOT apply generic validation rules - only validate against the specific agent's system prompt rules.
</validation_instructions>

<validation_criteria>
    - Agent response must follow ALL rules from their specific system prompt
    - Agent must stay within their defined role and capabilities
    - NO FALSE PROMISES: Agent cannot promise services they cannot actually execute with available tools
    - TRUTHFULNESS: If agent cannot execute a requested service, they must explicitly state "I cannot [service]" instead of promising future action
    - NO TRANSFER LOOPS: Agent cannot transfer back to agent that recently transferred to them
    - If recently transferred to, agent must execute their core function before any transfers
    - For handoff scenarios: receiving agent should appropriately continue the conversation
    - Agent must not perform forbidden actions as defined in their system prompt
    - Response should address user's question appropriately given the agent's role
    - Agent responses that include questions to users are generally valid (unless forbidden)
    - If agent states inability to help, it must be consistent with their defined limitations
    - Broker must use search tools for property queries before transferring
    - Broker must make only ONE transfer per response, never simultaneous transfers to multiple agents
    - Concierge must execute logistics tasks when assigned, not transfer back to Broker
    - Market_Analyst must provide analysis only, not coordinate with other agents or promise their actions
</validation_criteria>

<specific_agent_rules>
    <broker_validation>
        - MUST use search_properties or deep_search_properties for property queries
        - MUST make only ONE transfer per response - simultaneous transfers to multiple agents are INVALID
        - Can transfer to Concierge_Agent for logistics (scheduling, portfolios, neighborhood info)
        - Can transfer to Market_Analyst for investment analysis
        - CANNOT transfer back to Concierge if Concierge just transferred to Broker
        - CANNOT transfer back to Market_Analyst if Market_Analyst just transferred to Broker
        - Must complete property search before transferring logistics tasks
        - If recently transferred to, must execute property search, not transfer elsewhere
    </broker_validation>

    <concierge_validation>
        - MUST execute logistics tasks when assigned (scheduling, portfolios, neighborhood research)
        - If CANNOT execute a service with available tools, MUST explicitly state "I cannot [service] at this time"
        - CANNOT transfer back to Broker for logistics tasks - must handle them directly
        - CANNOT transfer back to Market_Analyst if Market_Analyst just transferred to Concierge
        - CANNOT promise services they cannot actually deliver (e.g., WhatsApp messages without WhatsApp tools)
        - Can only transfer to Broker if user requests property search and no logistics pending
        - CANNOT transfer back to agent that just transferred logistics tasks to them
        - Must use appropriate tools for scheduling, portfolio delivery, amenity research
        - If recently transferred to for logistics, must execute those tasks, not transfer elsewhere
    </concierge_validation>

    <market_analyst_validation>
        - MUST provide analysis using available tools, not coordinate with other agents
        - CANNOT say "our team will contact you" or make coordination promises
        - CANNOT promise that other agents will perform actions
        - CANNOT transfer back to Broker if Broker just transferred analysis request
        - CANNOT transfer back to Concierge if Concierge just transferred analysis request
        - MUST focus only on providing requested analysis and data
        - Can use analysis tools but cannot handle logistics or communication tasks
        - If recently transferred to for analysis, must provide analysis, not transfer elsewhere
    </market_analyst_validation>
</specific_agent_rules>

<output_requirements>
    - If response follows the agent's system prompt rules, avoids transfer loops, and makes no false promises: is_valid = True
    - If response violates rules, creates transfer loop, or makes false promises: is_valid = False with specific reason
    - Be precise about which specific rule from the agent's system prompt was violated
    - For transfer loops, clearly state which agents are looping and why it's invalid
    - For false promises, clearly state what service was promised but cannot be executed
    - ALWAYS invalidate false promises - they mislead users and damage trust
    - ALWAYS invalidate transfer loops - they waste resources and confuse users
    - ALWAYS invalidate simultaneous transfers - only ONE transfer per response allowed

    <critical_validation_priorities>
    1. TRANSFER LOOPS: Highest priority - must prevent infinite loops between agents
    2. SIMULTANEOUS TRANSFERS: Critical - only one transfer allowed per response
    3. FALSE PROMISES: High priority - agents must be truthful about their capabilities
    4. ROLE COMPLIANCE: Important priority - agents must follow their specific role rules
    </critical_validation_priorities>

    <tolerance_rules>
    - Tool call parameter corrections are acceptable and should be considered valid
    - Minor style variations are acceptable if core requirements met
    - Responses that show progress toward solving user's request are generally valid
    - Only invalidate responses that clearly violate core system prompt rules, create loops, or make false promises
    - False promises and transfer loops are ALWAYS invalid regardless of other factors
    - Agents stating "I cannot [service]" when they truly cannot execute it should be considered VALID and honest
    </tolerance_rules>
</output_requirements>""",
        ),
        (
            "human",
            """<context>
    <conversation_history>
        <messages>{message_history}</messages>
    </conversation_history>

    <user_interaction>
        <latest_question>{user_question}</latest_question>
    </user_interaction>

    <tool_interaction>
        <tool_call>
            <json>{tool_call_info}</json>
        </tool_call>
        <tool_result>{tool_result_info}</tool_result>
    </tool_interaction>

    <agent_response_to_validate>
        <final_answer>{agent_answer}</final_answer>
    </agent_response_to_validate>
</context>

<task>
    Validate the agent's response based on their specific system prompt rules provided above.

    CRITICAL TASKS (in order of priority):
    1. CHECK FOR FALSE PROMISES: Does the agent promise services they cannot actually execute with their available tools?
    2. CHECK FOR TRANSFER LOOPS: Are agents transferring back and forth without making progress?
    3. VALIDATE ROLE COMPLIANCE: Does agent follow their specific role rules?
    4. VERIFY TOOL USAGE: Does agent use appropriate tools based on their role?
    5. ENSURE CORE FUNCTION EXECUTION: When recently transferred to, does agent execute their core function?

    EXAMPLES OF FALSE PROMISES TO INVALIDATE:
    - Market_Analyst saying "our Concierge will contact you" (Market_Analyst cannot coordinate other agents)
    - Concierge saying "I'll send WhatsApp message" without actually using WhatsApp tools
    - Any agent promising actions they cannot execute with their available tools

    EXAMPLES OF INVALID SIMULTANEOUS TRANSFERS TO CATCH:
    - Broker making transfer_to_Market_Analyst AND transfer_to_Concierge_Agent in same response
    - Any agent making multiple transfer_to_* calls simultaneously
    - Multiple tool calls with transfer_to_ prefix in single agent response

    EXAMPLES OF HONEST RESPONSES TO VALIDATE:
    - "I cannot send WhatsApp messages at this time"
    - "I am unable to schedule viewings with my current tools"
    - "Let me provide the analysis requested" (and then actually doing it)

    CRITICAL SIMULTANEOUS TRANSFER DETECTION:
    - Check if agent response contains multiple transfer_to_* tool calls
    - If SIMULTANEOUS TRANSFER ALERT is present in context, INVALIDATE the response
    - Only ONE transfer per agent response is allowed

    If there was a recent transfer to this agent, they must execute their core function, not transfer back.
    Provide validation result in the specified JSON format.
</task>""",
        ),
    ]
)


@guide_agent(
    agent_name="validator",
    model="lite",
    custom_prompt_template=validation_custom_prompt,
    response_model=ValidationResult,
    spectator_mode=True,
    description="Validates agent responses to ensure they follow their specific role guidelines and provide appropriate responses to users",
)
async def validate_agent_response(
    state: State, config: RunnableConfig, writer: StreamWriter, model
) -> dict:
    """
    Valida a resposta final do agente usando um LLM.

    Primeiro identifica a última pergunta do usuário e a última resposta do agente,
    depois verifica se a resposta contém JSON direto (o que não é permitido),
    e então envia para um LLM validador e atualiza o estado com o resultado
    da validação (status e feedback, se houver falha).

    Args:
        state: O estado atual do grafo.

    Returns:
        Um dicionário contendo a chave 'retry_context' se a validação falhar,
        ou um dicionário vazio se passar ou ocorrer um erro na validação.
    """
    guide_logger.debug("---VALIDATING AGENT RESPONSE (LLM)---")

    current_agent = state.get("current_agent", "Broker")

    agent_to_validate = current_agent
    guide_logger.debug(f"Using current_agent for validation: {agent_to_validate}")

    agent_system_prompt = get_agent_system_prompt(agent_to_validate)

    if not agent_system_prompt:
        guide_logger.warning(
            f"No system prompt found for agent: {agent_to_validate}, using default"
        )
        agent_system_prompt = "No specific system prompt available for this agent."

    guide_logger.debug(f"Validating response from agent: {agent_to_validate}")

    messages = state["messages"]
    last_ai_message = None
    last_user_message = None
    last_ai_message_index = -1
    last_user_message_index = -1

    for i, msg in enumerate(reversed(messages)):
        current_index = len(messages) - 1 - i
        if (
            last_ai_message_index == -1
            and isinstance(msg, AIMessage)
            and not msg.tool_calls
        ):
            last_ai_message = msg
            last_ai_message_index = current_index
        elif last_user_message_index == -1 and isinstance(msg, HumanMessage):
            last_user_message = msg
            last_user_message_index = current_index

        if last_ai_message_index != -1 and last_user_message_index != -1:
            if last_ai_message_index > last_user_message_index:
                break
            else:
                last_ai_message_index = -1
                last_ai_message = None

    if last_ai_message_index == -1:
        guide_logger.debug("Warning: No final AIMessage found to validate.")
        return {}

    if last_user_message_index == -1:
        guide_logger.debug(
            "Warning: No previous user message found for validation context."
        )
        return {}

    transfer_loop_detected = False
    transfer_loop_reason = ""

    for i in range(max(0, len(messages) - 5), len(messages)):
        msg = messages[i]
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get("name", "")
                if tool_name.startswith("transfer_to_"):
                    target_agent = tool_name.replace("transfer_to_", "")

                    is_loop, loop_reason = detect_transfer_loop(
                        agent_to_validate, target_agent, messages
                    )

                    if is_loop:
                        transfer_loop_detected = True
                        transfer_loop_reason = f"Transfer loop detected: {loop_reason}. Agent must execute their core function instead of transferring."
                        break

        if transfer_loop_detected:
            break

    if transfer_loop_detected:
        guide_logger.debug(f"Validation Failed (Transfer Loop): {transfer_loop_reason}")
        writer(
            {"event": "validation_failed", "data": {"feedback": transfer_loop_reason}}
        )
        return {
            "retry_context": {
                "failed_attempt": last_ai_message.content
                if last_ai_message
                else "No response found",
                "feedback": transfer_loop_reason,
                "retry_count": 0,
            }
        }

    if last_ai_message:
        has_json = verify_json_existence(last_ai_message.content)
        guide_logger.debug("JSON VERIFICATION", last_ai_message.content, has_json)
        if has_json:
            feedback = "You must call this function as tool call instead writing the JSON directly."
            guide_logger.debug(f"Validation Failed (Direct JSON): {feedback}")

            guide_logger.debug("--- Emitting validation_failed (Direct JSON) ---")
            writer({"event": "validation_failed", "data": {"feedback": feedback}})
            return {
                "retry_context": {
                    "failed_attempt": last_ai_message.content,
                    "feedback": feedback,
                    "retry_count": 0,
                }
            }

    tool_call_info_str = "Nenhuma ferramenta foi chamada neste turno."
    tool_result_info_list = []

    if last_ai_message_index > last_user_message_index + 1:
        guide_logger.debug(
            f"Checking messages between index {last_user_message_index + 1} and {last_ai_message_index - 1} for tool calls/results."
        )
        for i in range(last_user_message_index + 1, last_ai_message_index):
            msg = messages[i]
            if isinstance(msg, AIMessage) and msg.tool_calls:
                try:
                    tool_call_info_str = json.dumps(
                        [tc for tc in msg.tool_calls], indent=2
                    )
                    guide_logger.debug(
                        f"Found tool call info at index {i}: {tool_call_info_str}"
                    )
                except Exception as e:
                    tool_call_info_str = f"Erro ao formatar tool_calls: {e}"
                    guide_logger.debug(f"Error formatting tool_calls at index {i}: {e}")
            elif isinstance(msg, ToolMessage):
                tool_result_info_list.append(
                    f"Resultado da Ferramenta (ID: {msg.tool_call_id}):\n{msg.content}"
                )

    tool_result_info_str = (
        "\n---\n".join(tool_result_info_list)
        if tool_result_info_list
        else "Nenhum resultado de ferramenta neste turno."
    )

    history_messages = messages[:last_ai_message_index]
    formatted_history = "\n".join(
        [
            f"{'User' if isinstance(m, HumanMessage) else 'AI' if isinstance(m, AIMessage) else 'Tool'}: {m.content}"
            for m in history_messages
        ]
    )

    recent_transfers = []
    transfer_chain = []
    simultaneous_transfers = []

    for i, msg in enumerate(reversed(messages[-10:])):
        msg_index = len(messages) - 1 - i
        if isinstance(msg, AIMessage) and msg.tool_calls:
            transfer_calls_in_msg = []
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get("name", "")
                if tool_name.startswith("transfer_to_"):
                    target_agent = tool_name.replace("transfer_to_", "")
                    transfer_info = {
                        "position": msg_index,
                        "target": target_agent,
                        "source_agent": agent_to_validate,
                        "tool_call_id": tool_call.get("id", ""),
                    }
                    recent_transfers.append(transfer_info)
                    transfer_calls_in_msg.append(transfer_info)

            if len(transfer_calls_in_msg) > 1:
                simultaneous_transfers.extend(transfer_calls_in_msg)

    for transfer in reversed(recent_transfers[-5:]):
        transfer_chain.append(f"{transfer['source_agent']} → {transfer['target']}")

    was_recently_transferred = False
    transfer_source = None
    ping_pong_detected = False

    for transfer in recent_transfers[-3:]:
        if transfer["target"] == agent_to_validate:
            was_recently_transferred = True
            transfer_source = transfer.get("source_agent", "Unknown")
            break

    if len(transfer_chain) >= 3:
        for i in range(len(transfer_chain) - 2):
            if (
                transfer_chain[i] == transfer_chain[i + 2]
                and transfer_chain[i] != transfer_chain[i + 1]
            ):
                ping_pong_detected = True
                break

    transfer_context = ""
    if was_recently_transferred:
        transfer_context += f"\n\nTRANSFER CONTEXT: {agent_to_validate} was recently transferred to from {transfer_source}. Agent MUST execute their core function, not transfer back."

    if simultaneous_transfers:
        transfer_context += "\n\nSIMULTANEOUS TRANSFER ALERT: Detected multiple transfer calls in single response - this is INVALID."

    if ping_pong_detected:
        transfer_context += f"\n\nPING-PONG PATTERN DETECTED: Transfer chain shows back-and-forth pattern: {' → '.join(transfer_chain[-4:])}"

    if recent_transfers:
        transfer_context += f"\n\nRecent transfer history: {transfer_chain}"

    conversation_with_context = formatted_history + transfer_context

    immediate_failure_reason = None

    if last_ai_message and isinstance(last_ai_message, AIMessage):
        for i in range(max(0, len(messages) - 3), len(messages)):
            msg = messages[i]
            if isinstance(msg, AIMessage) and msg.tool_calls:
                msg_transfers = [
                    tc
                    for tc in msg.tool_calls
                    if tc.get("name", "").startswith("transfer_to_")
                ]
                if len(msg_transfers) > 1:
                    transfer_targets = [
                        tc.get("name", "").replace("transfer_to_", "")
                        for tc in msg_transfers
                    ]
                    immediate_failure_reason = f"Invalid simultaneous transfers detected: Agent attempted to transfer to multiple agents simultaneously: {', '.join(transfer_targets)}. Only ONE transfer per response is allowed."
                    break

    if immediate_failure_reason:
        guide_logger.debug(f"Validation Failed (Immediate): {immediate_failure_reason}")
        writer(
            {
                "event": "validation_failed",
                "data": {"feedback": immediate_failure_reason},
            }
        )
        return {
            "retry_context": {
                "failed_attempt": last_ai_message.content
                if last_ai_message
                else "No response found",
                "feedback": immediate_failure_reason,
                "retry_count": 0,
            }
        }

    guide_logger.debug("Proceeding with LLM validation for the final agent response.")

    try:
        response = await model.ainvoke(
            {
                "current_agent": agent_to_validate,
                "agent_system_prompt": agent_system_prompt,
                "conversation_history": conversation_with_context,
                "message_history": formatted_history,
                "user_question": last_user_message.content,
                "tool_call_info": tool_call_info_str,
                "tool_result_info": tool_result_info_str,
                "agent_answer": last_ai_message.content,
            }
        )

        # Log token consumption for validation
        log_token_consumption("validator", response, len(messages))

        if response is None:
            guide_logger.error("Validation model returned None - treating as valid")
            return {"retry_context": None}

        validation_result: ValidationResult = response
    except Exception as model_error:
        guide_logger.error(f"Error calling validation model: {model_error}")
        return {"retry_context": None}

    try:
        guide_logger.debug(f"Validation Result: {validation_result}")

        if validation_result.is_valid:
            guide_logger.debug("Validation Passed (LLM).")

            return {"retry_context": None}
        else:
            feedback_content = validation_result.reason or "Não especificado"

            if (
                "loop" in feedback_content.lower()
                or "transfer" in feedback_content.lower()
            ):
                if was_recently_transferred:
                    feedback_content += f" You were recently transferred to from {transfer_source}. Execute your core function instead of transferring back."

                if simultaneous_transfers:
                    feedback_content += " Detected simultaneous transfers - only make ONE transfer per response."

                if ping_pong_detected:
                    feedback_content += f" Ping-pong pattern detected in transfer chain: {' → '.join(transfer_chain[-3:])}. Break the loop by executing your primary function."

            guide_logger.debug(f"Validation Failed (LLM): {feedback_content}")

            guide_logger.debug("--- Emitting validation_failed (LLM) ---")
            writer(
                {"event": "validation_failed", "data": {"feedback": feedback_content}}
            )

            return {
                "retry_context": {
                    "failed_attempt": last_ai_message.content,
                    "feedback": feedback_content,
                    "retry_count": 0,
                }
            }

    except Exception as e:
        guide_logger.error(f"Error during LLM validation: {e}")

        guide_logger.debug("Proceeding to suggestions due to validation error.")
        return {}
