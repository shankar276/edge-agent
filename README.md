# 🚀 EdgeAgent: On-Device AI Assistant

[![Qwen Cloud AI Hackathon](https://img.shields.io/badge/Hackathon-Qwen%20Cloud%20AI%20Hackathon-blue)](https://www.qwencloud.com/challenge/hackathon)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)

## 🌟 Overview

**EdgeAgent** is a lightweight, on-device AI assistant built for the **Qwen Cloud Global AI Hackathon** in the **EdgeAgent track**. It leverages a small-scale Large Language Model (LLM) from the Qwen series (Qwen2.5-0.5B-Instruct) to provide intelligent responses and interact with local tools directly on your machine, minimizing cloud dependency and ensuring privacy.

### Key Features:
- **On-Device Inference**: Runs a small Qwen model locally on CPU.
- **Tool Calling**: Executes local system commands and file operations.
- **Modular Architecture**: Easy to extend with new tools and models.
- **Privacy-Focused**: All processing happens locally, no data leaves your device.

## 💡 Why EdgeAgent?

Edge computing is crucial for AI applications requiring low latency, privacy, and reduced reliance on constant cloud connectivity. EdgeAgent demonstrates a practical approach to bringing powerful AI capabilities directly to end-user devices, enabling use cases like:

- **Offline Personal Assistants**: Responding to queries without internet.
- **Local Data Analysis**: Summarizing documents or logs stored locally.
- **Privacy-Preserving AI**: Ensuring sensitive data never leaves your machine.
- **Resource-Constrained Environments**: Deploying AI in settings with limited bandwidth or unstable internet.

## 🛠️ Tech Stack

- **Language Model**: Qwen2.5-0.5B-Instruct (from Hugging Face)
- **Inference**: Hugging Face `transformers` library (PyTorch on CPU)
- **Tools**: Python-based local system interaction (file I/O, subprocess, system info)
- **Configuration**: YAML for easy model and agent settings

## 🚀 Quick Start

Follow these steps to set up and run your EdgeAgent.

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/edge-agent.git # Replace with your repo
cd edge-agent
```

### 2. Set Up Python Environment

EdgeAgent requires Python 3.11 or later. It's recommended to use a virtual environment.

```bash
python -m venv venv
.\venv\Scripts\activate # On Windows
# source venv/bin/activate # On Linux/macOS
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the Model

The Qwen2.5-0.5B-Instruct model will be downloaded from Hugging Face. This might take a few minutes depending on your internet connection.

```bash
python scripts/download_model.py
```

### 5. Run EdgeAgent

```bash
python main.py
```

Now you can chat with the agent in your terminal. Try asking it to use its tools:

- `Hello`
- `Check my system info`
- `List files in .` (lists current directory contents)
- `Read file config.yaml`

Type `exit` to quit or `reset` to clear the conversation history.

## 📦 Project Structure

```
edge-agent/
├── main.py              # Main entry point for the CLI agent
├── config.yaml          # Agent and model configuration
├── requirements.txt     # Python dependencies
├── models/              # Downloaded LLM model files (Qwen2.5-0.5B-Instruct)
├── src/
│   ├── agent/
│   │   ├── __init__.py  # Makes 'agent' a Python package
│   │   ├── agent.py     # Core agent logic, message handling, tool orchestration
│   │   └── inference.py # LLM loading and generation (using transformers)
│   └── tools/
│       ├── __init__.py  # Makes 'tools' a Python package, defines tool functions
├── scripts/
│   └── download_model.py # Script to download the Qwen model
├── tests/               # Unit tests (not yet implemented)
└── docs/                # Documentation and submission artifacts
```

## 🏆 Qwen Cloud AI Hackathon Submission

### EdgeAgent Track

This project addresses the **EdgeAgent** track by focusing on optimizing AI agents for local deployment, minimizing latency, and operating in resource-constrained environments. By running the Qwen2.5-0.5B-Instruct model entirely on the device (CPU), we demonstrate a solution that is private, responsive, and less dependent on cloud infrastructure.

### Judging Criteria Alignment:

- **Innovation & AI Creativity (30%)**: The agent's ability to run a powerful LLM locally and interact with the local environment via tool calling showcases innovative deployment for AI agents. The modular design allows for easy extension and adaptation.
- **Technical Depth & Engineering (30%)**: Utilizing `transformers` for efficient local inference, a structured agent loop, and robust tool integration demonstrates solid engineering. The configuration-driven approach and clear separation of concerns (agent, inference, tools) contribute to technical depth.
- **Problem Value & Impact (25%)**: EdgeAgent solves the critical problems of data privacy and latency for AI applications. It has real-world relevance for scenarios where sensitive data cannot leave the device or where internet connectivity is unreliable, enabling broader adoption of AI.
- **Presentation & Documentation (15%)**: This `README.md` serves as a comprehensive overview. (Further documentation, video demo, and architecture diagrams will be added in `docs/` for final submission).

### Proof of Alibaba Cloud Deployment (Placeholder)

*(For final submission, screenshots demonstrating the backend running on Alibaba Cloud will be provided here, as per hackathon guidelines. As EdgeAgent is client-side, this would typically involve showcasing a basic service or monitoring on an Alibaba Cloud ECS/SAS instance, if a server component were added for specific use cases like model updates or centralized logging. For this pure on-device demo, it primarily focuses on local execution.)*

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## 📜 License

This project is licensed under the MIT License.

## 📞 Contact

For questions or feedback, please open an issue on the GitHub repository.