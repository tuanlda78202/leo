# installation
~pwd = app/offline_sys

# uv init --bare --python 3.12
# source activate .venv/bin/activate

UV_PROJECT_ENVIRONMENT=.venv_offline uv sync # if you have a pyproject.toml
uv pip install -e . # offline package inside src
# NOTE: export UV_PROJECT_ENVIRONMENT to make sure uv commands use the right environment

craw4ai-setup
craw4ai-doctor

# infrastructure
make local-infra-up # docker container only start port 27017, if u want UI, download mongo-compass
make local-infra-down

# project structure
```bash
.
├── configs/                   # ZenML configuration files
├── pipelines/                 # ZenML ML pipeline definitions
├── src/second_brain_offline/  # Main package directory
│   ├── application/           # Application layer
│   ├── domain/                # Domain layer
│   ├── infrastructure/        # Infrastructure layer
│   ├── config.py              # Configuration settings
│   └── utils.py               # Utility functions
├── steps/                     # ZenML pipeline steps
├── tests/                     # Test files
├── tools/                     # Entrypoint scripts that use the Python package
├── .env.example               # Environment variables template
├── .python-version            # Python version specification
├── Makefile                   # Project commands
└── pyproject.toml             # Project dependencies
```

# notion db 
* https://valiant-topaz-669.notion.site/llm-sys-research-1f455100bf0180f5b20cde1de067978e?pvs=4

# serving 
wget https://huggingface.co/unsloth/Qwen3-8B-GGUF/resolve/main/Qwen3-8B-Q4_K_M.gguf
vllm serve gguf/Qwen3-8B-Q4_K_M.gguf --tokenizer Qwen/Qwen3-8B

or raw bf16
vllm serve Qwen/Qwen3-1.7B

```python
from litellm import completion

SYSTEM_PROMPT_TEMPLATE = """You are an expert judge tasked with evaluating the quality of a given DOCUMENT. Your goal is to identify documents with substantive and valuable information.

Guidelines:
1.  Evaluate the DOCUMENT based on generally accepted facts and reliable information. The content should be accurate and trustworthy.
2.  The DOCUMENT must contain relevant, specific information related to a clear topic. It should not primarily consist of:
    *   Links, navigation menus, or boilerplate website elements (headers, footers, sidebars).
    *   Error messages (e.g., 404 Not Found, 503 Service Unavailable, access denied).
    *   Security block pages, CAPTCHAs, or login/registration forms.
    *   Pages dominated by advertisements, promotional content, or cookie consent banners with little to no original content.
    *   Placeholder text or content that is clearly auto-generated and lacks meaning.
3.  Check that the DOCUMENT doesn't oversimplify, misrepresent, or generalize information in a way that changes its meaning or accuracy. It should offer some depth or insight.
4.  The language should be coherent, well-structured, and understandable.

Analyze the text thoroughly and assign a quality score between 0.0 and 1.0, where:
- **0.0**: The DOCUMENT is completely irrelevant or unusable. It contains only noise, such as those listed in Guideline 2 (e.g., a security block page, a list of links, an error message, a page full of ads with no real content).
- **0.1 - 0.3**: The DOCUMENT has minimal relevance or utility. It might contain a small amount of potentially useful information but is heavily overshadowed by irrelevant content, is poorly written, or lacks any substantive insight. It may partially meet some guidelines but fails significantly on others.
- **0.4 - 0.7**: The DOCUMENT is partially relevant and useful. It contains some valuable information and generally follows the guidelines but may have noticeable flaws, such as some irrelevant sections, minor inaccuracies, or a lack of depth.
- **0.8 - 1.0**: The DOCUMENT is highly relevant, accurate, well-structured, and provides substantial, valuable information. It clearly follows all guidelines and represents a high-quality source.

It is crucial that you return only the score in the following JSON format:
{{
    "score": <your score between 0.0 and 1.0>
}}
"""

content = "AlgoExpert | Ace the Coding Interviews\nSearch\nWatch later\nShare\nCopy link\nInfo\nShopping\nTap to unmute\n2x\nIf playback doesn't begin shortly, try restarting your device.\n•\nYou're signed out\nVideos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.\nCancelConfirm\nShare\nInclude playlist\nAn error occurred while retrieving sharing information. Please try again later.\n0:00\n0:00 / 0:34\n•Watch full videoLive\n•\n•\nScroll for details\n[](https://www.youtube.com/ \"YouTube\")[](https://www.youtube.com/ \"YouTube\")\n[About](https://www.youtube.com/about/)[Press](https://www.youtube.com/about/press/)[Copyright](https://www.youtube.com/about/copyright/)[Contact us](https://www.youtube.com/t/contact_us/)[Creators](https://www.youtube.com/creators/)[Advertise](https://www.youtube.com/ads/)[Developers](https://developers.google.com/youtube)[Terms](https://www.youtube.com/t/terms)[Privacy](https://www.youtube.com/t/privacy)[Policy & Safety](https://www.youtube.com/about/policies/)[How YouTube works](https://www.youtube.com/howyoutubeworks?utm_campaign=ytgen&utm_source=ythp&utm_medium=LeftNav&utm_content=txt&u=https%3A%2F%2Fwww.youtube.com%2Fhowyoutubeworks%3Futm_source%3Dythp%26utm_medium%3DLeftNav%26utm_campaign%3Dytgen)[Test new features](https://www.youtube.com/new)\n© 2025 Google LLC\n"

messages = [
    {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE},
    {
        "role": "user",
        "content": content,
    },
]

# hosted_vllm is prefix key word and necessary
response = completion(
    model="hosted_vllm/Qwen/Qwen3-1.7B",
    messages=messages,
    api_base="http://localhost:8000/v1",
    temperature=0.6,
    top_p=0.95,
    top_k=20,
    max_tokens=8196,
    stream=True,
)

for part in response:
    print(part.choices[0].delta.content or "", end="", flush=True)
```

```bash
curl http://localhost:8000/v1/chat/completions -H "Content-Type: application/json" -d '{
  "model": "Qwen/Qwen3-1.7B",
  "messages": [
    {"role": "user", "content": "Give me a short introduction to large language models."}
  ],
  "temperature": 0.6,
  "top_p": 0.95,
  "top_k": 20,
  "max_tokens": 32768
}'
```