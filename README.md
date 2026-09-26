# LangSmith custom output renderer: echo repro

The [custom output rendering docs](https://docs.langchain.com/langsmith/custom-output-rendering)'
own example page (`index.html`, unchanged) as a dataset's renderer. It prints every message
LangSmith posts, so you can compare the run page with the experiment compare pane.

## Run it

Needs [mise](https://mise.jdx.dev) (it installs `cloudflared` and `uv`) and a LangSmith API key.

```sh
mise install
echo "LANGSMITH_API_KEY=lsv2_..." > .env
mise exec -- ./run.sh
```

`run.sh` serves `index.html` on localhost, opens a Cloudflare quick tunnel to it (LangSmith
embeds only `https://` pages), then runs `repro.py`. That creates a `renderer-echo-repro`
dataset with one example, sets its custom output renderer to the tunnel URL, runs two
experiments and prints a run page URL and a compare pane URL. The tunnel stays up until
Ctrl-C; its URL changes on every run, and `repro.py` re-points the dataset each time.

## Check

1. **Run page:** open it and switch the output format to Custom.
2. **Compare pane:** open it, expand the row, switch Outputs and Reference Outputs to Custom.

Per the docs, each message is `{type: "output" | "reference", data, metadata: {inputs}}`,
with `metadata.inputs` holding the example's inputs (`{"question": "What is 2 + 2?"}`) and
`type` telling a run's outputs from the reference outputs.
