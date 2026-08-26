# garak against the lab

[garak](https://github.com/NVIDIA/garak) (NVIDIA's LLM vulnerability scanner,
120+ probes) is pointed at the lab's `/chat` endpoint through its generic REST
generator, the config in [`rest_chat.json`](./rest_chat.json) maps garak's
`$INPUT` into `{"message": ...}` and reads the model's answer back from the
`reply` field.

## Run

```bash
# 1. start the target (insecure to see findings, secure to see them disappear)
make lab                      # or: LAB_MODE=insecure uvicorn app.main:app --port 8000

# 2. scan it
garak --model_type rest -G attacks/garak/rest_chat.json \
      --probes promptinject,dan,latentinjection,leakreplay,encoding \
      --report_prefix results/garak
```

## What each probe exercises here

| garak probe      | Taxonomy / OWASP                         |
|------------------|------------------------------------------|
| `promptinject`   | Direct injection, LLM01                 |
| `latentinjection`| Indirect / latent injection, LLM01      |
| `leakreplay`     | Training/context replay & leak, LLM02   |
| `dan`            | Jailbreak personas, LLM01               |
| `encoding`       | Token-smuggling (base64/rot13), LLM01   |

> The lab's default backend is a deterministic simulator, so garak's
> probabilistic detectors are most meaningful against the **Ollama** backend
> (`LAB_BACKEND=ollama`). Against the simulator, use garak to validate the
> wiring and to compare `insecure` vs `secure` runs.
