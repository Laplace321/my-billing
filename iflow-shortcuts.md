Basics:                                                                                               │
│ Add context: Use @ to specify files for context (e.g., @src/myFile.ts) to target specific files or    │
│ folders.                                                                                              │
│ Shell mode: Execute shell commands via ! (e.g., !npm run start) or use natural language (e.g. start   │
│ server).                                                                                              │
│                                                                                                       │
│ Commands:                                                                                             │
│  /about - show version info                                                                           │
│  /agents - Commands for interacting with agents.                                                      │
│    list - List available agents.                                                                      │
│    refresh - Refresh agents from source files.                                                        │
│    online - Browse and install agents from online repository                                          │
│    install - Install a new agent with guided setup                                                    │
│  /auth - change the auth method                                                                       │
│  /bug - submit a bug report                                                                           │
│  /chat - Manage conversation history.                                                                 │
│    list - List saved conversation checkpoints                                                         │
│    save - Save the current conversation as a checkpoint. Usage: /chat save <tag>                      │
│    resume - Resume a conversation from a checkpoint. Usage: /chat resume <tag>                        │
│    delete - Delete a conversation checkpoint. Usage: /chat delete <tag>                               │
│  /clear - clear the screen and conversation history                                                   │
│  /commands - Manage marketplace commands: list local, browse online, get details, add/remove from CLI │
│ (project/global scope)                                                                                │
│    list - List locally installed commands from project and global scopes                              │
│    online - Browse available commands from online marketplace in an interactive dialog                │
│    get - Get details about a specific command by ID                                                   │
│    add - Add a specific command by ID to local CLI (use --scope global for system-wide install)       │
│    remove - Remove a locally installed command (use --scope global to remove from global)             │
│  /compress - Compresses the context by replacing it with a summary. (aliases: /compact, /summarize)   │
│  /copy - Copy the last result or code snippet to clipboard                                            │
│  /corgi - Toggles corgi mode.                                                                         │
│  /demo - Interactive task for research and brainstorming workflows                                    │
│  /docs - open full iFlow CLI documentation in your browser                                            │
│  /directory - Manage workspace directories                                                            │
│    add - Add directories to the workspace. Use comma to separate multiple paths                       │
│    show - Show all directories in the workspace                                                       │
│  /editor - set external editor preference                                                             │
│  /export - Export conversation history                                                                │
│    clipboard - Copy the conversation to your system clipboard                                         │
│    file - Save the conversation to a file in the current directory                                    │
│  /extensions - list active extensions                                                                 │
│  /help - for help on iflow-cli                                                                        │
│  /init - Analyzes the project and creates or updates a tailored IFLOW.md file.                        │
│  /ide - Manage IDE integrations and show status                                                       │
│  /ide-tool - IDE integration tools                                                                    │
│    active-file - get currently active file in IDE                                                     │
│    file-content - get content of active file or specified file                                        │
│    selected-text - get currently selected text in IDE                                                 │
│    show-diff - show diff in IDE between original and modified text                                    │
│  /log - show current session log storage location                                                     │
│  /mcp - list configured MCP servers and tools, browse online repository, or authenticate with         │
│ OAuth-enabled servers                                                                                 │
│    list - Interactive list of configured MCP servers and tools                                        │
│    auth - Authenticate with an OAuth-enabled MCP server                                               │
│    refresh - Refresh the list of MCP servers and tools, and reload settings files                     │
│    online - Browse and install MCP servers from online repository                                     │
│  /memory - Commands for interacting with memory.                                                      │
│    show - Show the current memory contents.                                                           │
│    add - Add content to the memory.                                                                   │
│    refresh - Refresh the memory from the source.                                                      │
│  /model - change the model                                                                            │
│  /quit - exit the cli                                                                                 │
│  /stats - check session stats. Usage: /stats [model|tools]                                            │
│    model - Show model-specific usage statistics.                                                      │
│    tools - Show tool-specific usage statistics.                                                       │
│  /theme - change the theme                                                                            │
│  /tools - list available iFlow CLI tools                                                              │
│  /vim - toggle vim mode on/off                                                                        │
│  /setup-github - Set up GitHub Actions                                                                │
│  ! - shell command                                                                                    │
│                                                                                                       │
│ Keyboard Shortcuts:                                                                                   │
│ Alt+Left/Right - Jump through words in the input                                                      │
│ Ctrl+C - Quit application                                                                             │
│ Ctrl+J - New line                                                                                     │
│ Ctrl+L - Clear the screen                                                                             │
│ Ctrl+X / Meta+Enter - Open input in external editor                                                   │
│ Ctrl+Y - Toggle YOLO mode                                                                             │
│ Enter - Send message                                                                                  │
│ Esc - Cancel operation                                                                                │
│ Shift+Tab / Alt+M - Toggle mode                                                                       │
│ Up/Down - Cycle through your prompt history                                                           │
│                                                                                                       │
│ For a full list of shortcuts, see docs/keyboard-shortcuts.md   