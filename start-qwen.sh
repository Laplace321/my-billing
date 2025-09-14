#!/bin/bash
# 读取 QWEN.md 的内容作为 system prompt
SYSTEM_PROMPT=$(cat QWEN.md)
qwen-coder --system "$SYSTEM_PROMPT"
