# pkg_llm

Local LLM for the planner of the task manager (plan P6). The planner only knows an
OpenAI-compatible HTTP endpoint (`GEORG_LLM_URL`), so model and hardware stay exchangeable.

| | |
| --- | --- |
| server | llama.cpp `llama-server`, `POST /v1/chat/completions` |
| default model | Qwen2.5-1.5B-Instruct, GGUF Q4_K_M (~1 GB), runs on a laptop |
| on the robot | Jetson Thor; a bigger model is a configuration change (`GEORG_LLM_MODEL_FILE`) |

```bash
# model to ~/georg-llm (once)
mkdir -p ~/georg-llm && curl -sSL --fail -o ~/georg-llm/qwen2.5-1.5b-instruct-q4_k_m.gguf \
  https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf

GEORG_WITH_LLM=1 ./projectctl.bash up mock      # adds the llm service

# Mac without Docker (dev/macos)
pixi run -e llm llm_model && pixi run -e llm llm_server
```

The planner sends a JSON schema built from the catalog with every request
(constrained decoding): the model can only answer with catalog names, allowed arguments
and places of the map. The validator in the task manager checks every answer again.

The LLM acts only after the operator switched to an LLM mode in Lichtblick
(`task_manager/set_mode`). On the real robot (`profile real`) LLM modes are refused unless
`GEORG_LLM_REAL_APPROVED=1` is set, i.e. after the replay and simulation tests passed.
