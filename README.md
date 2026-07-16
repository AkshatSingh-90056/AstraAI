# Astra - Local Offline AI Assistant

<p align="center">
  <img src="./src/img/Astra.png" alt="Astra Logo" width="200">
</p>

A fully localized, stateful artificial intelligence assistant built with Python. Designed to prioritize privacy and local system control, this application routes natural language processing through a locally hosted Llama 3.1 model while executing custom OS-level operations without relying on third-party cloud APIs.

## The Anatomy of Astra

* **Brain:** Locally hosted Llama 3.1 via Ollama (100% offline privacy).
* **Ears & Mouth:** `SpeechRecognition` and asynchronous `edge-tts` for hyper-realistic audio.
* **Hands:** A custom JSON tool-router bypassing LLM hallucination to execute local Python scripts and OS commands.
* **Face:** A non-blocking, multi-threaded GUI built with `CustomTkinter` and `pygame`.

## System Architecture

* **Stateful Conversational Memory:** Implements a rolling context window (FIFO buffer) that retains recent conversation history and dynamically injects real-time clock data into the system prompt for complete temporal awareness.
* **Whitelist Tool Router:** A custom failsafe mechanism that parses user intent for action keywords. It dynamically grants or revokes the LLM's access to local PC tools, preventing AI hallucination when executing system commands.
* **Asynchronous Neural Audio:** Utilizes edge-tts for hyper-realistic voice generation. Audio processing is threaded asynchronously to prevent GUI blocking, utilizing dynamic file generation to bypass Windows file-lock permissions during rapid multi-turn conversations.
* **Non-Blocking UI & Background Protocols:** Built with CustomTkinter for a modern visual interface. Intercepts standard Windows kill-signals to withdraw the application into a pystray system tray background process rather than terminating.

## Interface Preview

<p align="center">
  <img src="./src/img/astra_demo.gif" alt="Astra AI Demo" width="95%">
</p>

<p align="center">
  <img src="./src/img/Astra_UI_original_size.png" alt="Astra UI Preview" width="95%">
</p>

<p align="center">
  <img src="./src/img/Astra_timedate.gif" alt="Astra Temporal Awareness Demo" width="95%">
</p>

## Tech Stack

* **Language:** Python 3.12
* **AI Core:** Ollama (Llama 3.1)
* **GUI:** CustomTkinter, Pillow
* **Audio Engineering:** Pygame, Edge-TTS, SpeechRecognition
* **Thread Management:** Python threading, asyncio

## Installation & Usage

Step 1: Clone the repository:
```bash
git clone [https://github.com/AkshatSingh-90056/astra-desktop.git](https://github.com/AkshatSingh-90056/astra-desktop.git)
 ```

Step 2: Activate the virtual environment and install dependencies:
```bash
pip install -r requirements.txt
 ```

Step 3: Ensure Ollama is installed and running llama3.1 locally.

Step 4: Launch the application:
```bash
python src/AstraAI.py
 ```

## Engineering Focus

The primary goal of this project was to bridge the gap between heavy backend AI processing and responsive frontend GUI design. By managing custom execution threads and building a strict tool-routing protocol, Astra operates as a reliable, production-grade desktop utility rather than a simple API wrapper.