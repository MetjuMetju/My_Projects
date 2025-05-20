#!/bin/bash

# File: generic_gitlab_creator.sh

# Check if required env vars are set
if [ -z "$GITLAB_TOKEN" ]; then
  echo "❌ GITLAB_TOKEN is not set."
  echo "➡️  Export your GitLab Personal Access Token like this:"
  echo "    export GITLAB_TOKEN='your_token_here'"
  exit 1
fi

if [ -z "$GITLAB_NAMESPACE" ]; then
  echo "❌ GITLAB_NAMESPACE is not set."
  echo "➡️  This should be your GitLab username or group name."
  echo "    export GITLAB_NAMESPACE='your_gitlab_username'"
  exit 1
fi

# Check for project name argument
if [ -z "$1" ]; then
  echo "❌ Usage: $0 <project-name>"
  exit 1
fi

PROJECT_NAME="$1"

echo "🚀 Creating project '$PROJECT_NAME' under namespace '$GITLAB_NAMESPACE'..."

# Create the project using GitLab API
response=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --data "name=$PROJECT_NAME&namespace_id=$GITLAB_NAMESPACE" \
  https://gitlab.com/api/v4/projects)

# Check if the project was created
if echo "$response" | grep -q "\"id\":"; then
  web_url=$(echo "$response" | grep -o '"web_url":"[^"]*' | cut -d':' -f2- | tr -d '"')
  echo "✅ Project created: $web_url"
else
  echo "❌ Failed to create project. Response:"
  echo "$response"
fi

