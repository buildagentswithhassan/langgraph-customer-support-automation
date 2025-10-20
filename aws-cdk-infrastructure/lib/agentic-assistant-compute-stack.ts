import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as elbv2 from "aws-cdk-lib/aws-elasticloadbalancingv2";
import * as iam from "aws-cdk-lib/aws-iam";
import * as logs from "aws-cdk-lib/aws-logs";
import { AgenticAssistantStackOutputs } from "./agentic-assistant-stack";

export interface AgenticAssistantComputeStackProps extends cdk.StackProps {
  infrastructureOutputs: AgenticAssistantStackOutputs;
}

export class AgenticAssistantComputeStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: AgenticAssistantComputeStackProps) {
    super(scope, id, props);

    const { vpc, orderTrackingTable, ecrRepository } = props.infrastructureOutputs;

    // ECS Cluster
    const cluster = new ecs.Cluster(this, "McpServerCluster", {
      vpc: vpc.vpc,
      clusterName: "mcp-server-cluster",
    });

    // Task Role
    const taskRole = new iam.Role(this, "McpServerTaskRole", {
      assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
      inlinePolicies: {
        DynamoDBAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:Scan"],
              resources: [orderTrackingTable.tableArn],
            }),
          ],
        }),
      },
    });

    // Task Definition
    const taskDefinition = new ecs.FargateTaskDefinition(
      this,
      "McpServerTaskDef",
      {
        memoryLimitMiB: 512,
        cpu: 256,
        taskRole,
      }
    );

    // Container
    const container = taskDefinition.addContainer("McpServerContainer", {
      image: ecs.ContainerImage.fromEcrRepository(ecrRepository, "latest"),
      environment: {
        AWS_REGION: this.region,
        DYNAMODB_TABLE: orderTrackingTable.tableName,
        PINECONE_API_KEY: process.env.PINECONE_API_KEY!,
        COHERE_API_KEY: process.env.COHERE_API_KEY!,
      },
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: "mcp-server",
        logGroup: new logs.LogGroup(this, "McpServerLogGroup", {
          logGroupName: "/ecs/mcp-server",
          removalPolicy: cdk.RemovalPolicy.DESTROY,
        }),
      }),
      healthCheck: {
        command: [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1",
        ],
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        retries: 3,
      },
    });

    container.addPortMappings({
      containerPort: 8000,
      protocol: ecs.Protocol.TCP,
    });

    // Application Load Balancer
    const alb = new elbv2.ApplicationLoadBalancer(this, "McpServerALB", {
      vpc: vpc.vpc,
      internetFacing: true,
    });

    const listener = alb.addListener("McpServerListener", {
      port: 80,
      open: true,
    });

    // ECS Service
    const service = new ecs.FargateService(this, "McpServerService", {
      cluster,
      taskDefinition,
      desiredCount: 0,
      assignPublicIp: false,
    });

    // Target Group
    listener.addTargets("McpServerTargets", {
      port: 8000,
      targets: [service],
    });

    // Outputs
    new cdk.CfnOutput(this, "LoadBalancerDNS", {
      value: alb.loadBalancerDnsName,
    });
  }
}
