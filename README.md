# CodeforgeAI 🚀🤖

Welcome to **CodeforgeAI** – your ultimate, emoji-powered coding assistant! 🎉 Whether you're refining commit messages, analyzing your project, or editing code on the fly, CodeforgeAI has you covered. 

## Features ✨
- **Prompt Processing:** Transform natural language prompts into precise code edits. 💡
- **Code Analysis:** Get detailed insights and explanations for your code. 🕵️‍♂️
- **Automatic Edits:** Quickly apply AI-driven modifications across your codebase. 🛠️
- **Commit Messages:** Generate concise commit messages paired with expressive gitmojis. 🎯
- **Modular & Extensible:** Easily integrate and customize to fit your workflow. 🔌

## Quick Start 🔥
1. **Install:**  
   Run `pip install .` or `pip install -e .` for editable mode.
2. **Configure:**  
   Update your `~/.codeforgeai.json` with custom prompts and settings. 📝
3. **Run:**  
   Execute the tool with commands like `analyze`, `prompt`, `edit`, or `commit-message`.

## Detailed Usage

### 1. Installation
- Run `pip install .` or `pip install -e .` after cloning the repository.
- Ensure you have a proper Python environment set up.

### 2. Configuration
- The configuration file is located at `~/.codeforgeai.json`.
- Edit this file to update prompts, model names, and other settings. Example:
```
{
  "prompts": {
    "commit_message": "Generate a commit message for the following changes:",
    "code_edit": "Refactor the following code for clarity:"
  },
  "model": "gpt-3.5-turbo"
}
```

### 3. CLI Commands

#### Generate a Commit Message
```sh
codeforgeai commit-message
```

#### Edit Code in a File
```sh
codeforgeai edit my_script.py --user_prompt "Refactor for clarity"
```

#### Analyze Your Directory
```sh
codeforgeai analyze --loop
```

## Usage Examples 🤩
- **Generate a Commit Message:**  
  ```sh
  codeforgeai commit-message
  ```
- **Edit Code in a File:**  
  ```sh
  codeforgeai edit my_script.py --user_prompt "Refactor for clarity"
  ```
- **Analyze Your Directory:**  
  ```sh
  codeforgeai analyze --loop
  ```

## Project Structure 📁
- **src/codeforgeai/**: Core engine, models, and CLI logic.
- **config**: JSON-based configuration for prompt tuning.
- **Utilities**: Modules to handle file management and directory analysis.

## Contributing 💖
We welcome your contributions!  
- Fork the repository.
- Create a feature branch.
- Commit with witty, emoji-laden messages.
- Open a pull request – let’s code together! 🤝

## License 📜
This project is MIT licensed. Enjoy, share, and innovate with CodeforgeAI! 🆓

---

Thank you for choosing CodeforgeAI – where creativity meets code. Happy coding! 🎊💫

## Troubleshooting 🛠️
- Ensure your configuration file at `~/.codeforgeai.json` is properly set up.
- If the commit-message subcommand returns "No changes found" unexpectedly, verify that there are staged, tracked, or untracked changes.
- Check your internet connectivity if AI model requests fail.
- Review the logs (if running in debug mode) for detailed error messages.

## FAQ ❓
- **Q:** How do I update the configuration?  
  **A:** Edit the `~/.codeforgeai.json` file to customize prompts and model settings.
- **Q:** Which models are used for AI tasks?  
  **A:** `general_model` is used for prompt rephrasing and initial processing, while `code_model` handles code-specific requests (e.g., commit messages, explanations).
- **Q:** How can I contribute to CodeforgeAI?  
  **A:** Fork the repository, make improvements, and submit a pull request with a clear commit message.
- **Q:** Where can I find more documentation?  
  **A:** Additional usage details can be found in the repository’s wiki and inline code documentation.
