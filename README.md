# LangGraph Customer Support Automation

## Project Overview

An intelligent customer support automation system built with LangGraph that processes incoming emails and provides automated responses using AI agents. The system integrates Gmail API, Google Cloud Pub/Sub, and AWS services to create a complete end-to-end solution.

## Business Use Case

Customer support operations often become a significant overhead for businesses, requiring manual intervention for routine inquiries. This project addresses that challenge by:

- **Automating Email Processing**: Automatically receives and processes customer emails through Gmail API integration
- **Intelligent Response Generation**: Uses AI agents to analyze customer problems and generate appropriate responses
- **Knowledge Base Integration**: Leverages company policies and documentation through RAG (Retrieval-Augmented Generation)
- **Order Tracking**: Provides real-time order status updates from integrated systems
- **Scalable Architecture**: Built on AWS infrastructure for enterprise-scale deployment

## Architecture

<img width="1671" height="969" alt="langgraph-agent-customer-support-automation" src="https://github.com/user-attachments/assets/b91df27b-2f00-4be6-b7f1-bf7a86226278" />

### Core Components

#### LangGraph Workflow (`langgraph-workflow/`)
- **FastAPI Server**: Handles Gmail webhook events at `/gmail-webhook` endpoint
- **Agent Workflow**: Multi-step LangGraph workflow for email processing
- **State Management**: Tracks email processing state through the workflow
- **Tool Integration**: Connects to MCP server for external tool access

#### MCP Server (`mcp-server/`)
Dockerized Model Context Protocol server deployed on AWS ECS Fargate providing:
- **Knowledge Base Tool**: RAG solution using Pinecone for company policy search
- **Tracking Tool**: DynamoDB integration for order tracking information

#### AWS Infrastructure (`aws-cdk-infrastructure/`)
- **ECS Fargate**: Hosts the containerized MCP server
- **DynamoDB**: Stores order tracking data
- **ECR**: Container registry for MCP server images
- **VPC**: Secure networking setup
