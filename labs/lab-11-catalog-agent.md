# Lab 11 — Build the `CatalogAgent`

**Duration:** ~80 min · **Day:** 4 · **Module:** 2 (Tools as Functions + Agent Loop)

## Goal
Wire up a real agent: an LLM that can **call your `APIClient` methods as
tools**. The agent loop is *plan → act → observe → repeat*. Tools are
just Python functions, registered with a decorator (Day 1 returns).
By the end, asking `agent.ask("what's our most expensive product?")`
makes the LLM call `list_products`, reason over the result, and answer.

## You start with
- Lab 10 end-state — `CatalogQuery` + `parse_nl_query` working.

## You'll end with
- `ToolSpec`, `ToolRegistry`, and a `@registry.tool(...)` decorator
- `CatalogAgent.ask(prompt) -> AgentResult` running a real loop
- Four registered tools: `list_products`, `search_products`, `count_by_category`, `update_price`
- A demo run answering a free-form question end-to-end

## Steps

1. **Define the tool plumbing.** Each tool is a `ToolSpec` (name + JSON schema + Python callable). A `ToolRegistry` holds them and renders them in OpenAI's `tools=[...]` format:

   ```python
   @dataclass
   class ToolSpec:
       name: str
       description: str
       parameters_schema: dict
       fn: Callable[..., Any]

       def to_openai_schema(self) -> dict:
           return {"type": "function",
                   "function": {"name": self.name,
                                "description": self.description,
                                "parameters": self.parameters_schema}}
   ```

2. **Register tools with a decorator.** Same shape as Day 1's `@log_calls`, this time stamping metadata onto a registry:

   ```python
   @registry.tool(
       name="search_products",
       description="Find products whose name contains the given substring (case-insensitive).",
       parameters={
           "type": "object",
           "properties": {"term": {"type": "string"}},
           "required": ["term"],
           "additionalProperties": False,
       },
   )
   def search_products(term: str) -> list[dict]:
       return [p.model_dump() for p in self.api.list_products()
               if term.lower() in p.name.lower()]
   ```

3. **Inject the LLM client.** Same pattern as the Day-3 `APIClient`:

   ```python
   class CatalogAgent:
       def __init__(self, api_client: APIClient,
                    llm_client=None, *, model="gpt-4o-mini", max_steps=5):
           self.api = api_client
           self.llm = llm_client or OpenAI()
           self.model = model
           self.max_steps = max_steps
           self.registry = self._build_registry()
   ```

   Tomorrow's tests will swap `llm_client` for a `MagicMock`. The seam is there from day one.

4. **Write the loop.** Plan/act/observe in code:

   ```python
   def ask(self, user_prompt: str) -> AgentResult:
       messages = [{"role": "system", "content": SYSTEM_PROMPT},
                   {"role": "user",   "content": user_prompt}]
       log = []
       for step in range(1, self.max_steps + 1):
           resp = self.llm.chat.completions.create(
               model=self.model, messages=messages,
               tools=self.registry.openai_schemas(),
           )
           msg = resp.choices[0].message
           if not msg.tool_calls:
               return AgentResult(answer=msg.content, tool_calls=log, steps=step)

           messages.append({"role": "assistant", "content": msg.content,
                            "tool_calls": _serialise_calls(msg.tool_calls)})
           for call in msg.tool_calls:
               result = self._invoke_tool(call.function.name,
                                          call.function.arguments)
               log.append(ToolCallRecord(call.function.name,
                                         json.loads(call.function.arguments),
                                         result))
               messages.append({"role": "tool",
                                "tool_call_id": call.id,
                                "name": call.function.name,
                                "content": json.dumps(result, default=str)})

       raise AgentError(f"did not converge in {self.max_steps} steps")
   ```

5. **Demo it** (with the server up):

   ```bash
   uvicorn catalog.server:app --reload  # terminal 1
   ```

   ```python
   from catalog.agent import CatalogAgent
   from catalog.client import APIClient

   agent = CatalogAgent(APIClient())
   r = agent.ask("what is our most expensive product and its price?")
   print(r.answer)
   for c in r.tool_calls:
       print("  →", c.tool, c.arguments)
   ```

6. **Watch the loop walk.** The model will call `list_products`, see the
   data, then either answer directly or call another tool. Both are valid.

## Expected output

```
$ python -c "from catalog.agent import CatalogAgent; from catalog.client import APIClient; \
            r = CatalogAgent(APIClient()).ask('most expensive product?'); \
            print(r.answer); print([(c.tool, c.arguments) for c in r.tool_calls])"

The most expensive product in your catalog is the Mechanical Keyboard, priced at ₹5,499.
[('list_products', {})]
```

## Common pitfalls
- Returning Pydantic `Product` objects from a tool. OpenAI's tool-message
  body must be a string. Always `model_dump()` first, then `json.dumps(...)`.
- Forgetting `tool_call_id` on the tool-result message — the next LLM call rejects the conversation.
- Re-creating the OpenAI client on every `ask()` call — leaks file handles. Build it once in `__init__`.
- A `max_steps` that's too small (3) makes the agent give up mid-task; too large (50) means a runaway loop on bugs. **5** is a good default for this lab.
- Silently catching `Exception` inside `_invoke_tool` and returning an empty dict — the model will get confused and loop. Return a `{"error": "..."}` observation instead so the LLM can react.

## Stretch (optional)
- Add a `delete_product` tool, then add a confirmation step (the LLM proposes, your code asks the user, then executes).
- Persist agent conversation history per session in a SQLite file.
- Swap OpenAI for Anthropic — only `default_openai_client()` and the message format change; the registry + loop stay identical.
