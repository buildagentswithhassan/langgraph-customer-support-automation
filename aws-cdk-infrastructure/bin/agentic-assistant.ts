#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { AgenticAssistantStack } from "../lib/agentic-assistant-stack";
import { AgenticAssistantComputeStack } from "../lib/agentic-assistant-compute-stack";
import "dotenv/config";

const app = new cdk.App();

const infrastructureStack = new AgenticAssistantStack(
  app,
  "AgenticAssistantInfraStack",
  {
    env: {
      account: process.env.CDK_DEFAULT_ACCOUNT,
      region: process.env.CDK_DEFAULT_REGION,
    },
  }
);

new AgenticAssistantComputeStack(app, "AgenticAssistantComputeStack", {
  infrastructureOutputs: infrastructureStack.outputs,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
