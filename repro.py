# /// script
# requires-python = ">=3.12"
# dependencies = ["langsmith==0.13.0"]
# ///
"""A dataset whose custom output renderer is an echo page, and two experiments to compare.

Then compare what the echo page receives on a run page and in the experiment compare pane.
"""

import argparse

from langsmith import Client, evaluate

DATASET = "renderer-echo-repro"


def target(inputs: dict) -> dict:
    # Differs from the reference ("4"), so each panel shows which data it was sent.
    return {"answer": "four"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--renderer-url", required=True, help="The echo page's https:// URL."
    )
    parser.add_argument("--dataset", default=DATASET)
    args = parser.parse_args()

    client = Client()
    if client.has_dataset(dataset_name=args.dataset):
        dataset = client.read_dataset(dataset_name=args.dataset)
    else:
        dataset = client.create_dataset(args.dataset)
        client.create_examples(
            dataset_id=dataset.id,
            examples=[
                {"inputs": {"question": "What is 2 + 2?"}, "outputs": {"answer": "4"}}
            ],
        )

    # What ⋮ → Custom Output Rendering saves. The SDK has no dataset update, so PATCH it.
    metadata = {
        **(dataset.metadata or {}),
        "iframe_config": {"enabled": True, "url": args.renderer_url},
    }
    client.request_with_retries(
        "PATCH",
        f"/datasets/{dataset.id}",
        request_kwargs={"json": {"metadata": metadata}},
    )

    experiments = [
        evaluate(target, data=args.dataset, experiment_prefix=prefix, client=client)
        for prefix in ("echo-a", "echo-b")
    ]
    ids = ",".join(str(e.experiment_id) for e in experiments)
    run = next(iter(experiments[0]))["run"]
    org = dataset.url.split("/datasets/")[0]

    print()
    print(f"Renderer:     {args.renderer_url}")
    print(f"Run page:     {org}/projects/p/{experiments[0].experiment_id}/r/{run.id}")
    print(f"Compare pane: {dataset.url}/compare?selectedSessions={ids}")


if __name__ == "__main__":
    main()
