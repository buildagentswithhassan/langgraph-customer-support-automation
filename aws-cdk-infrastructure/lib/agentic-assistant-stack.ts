import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as ecr from "aws-cdk-lib/aws-ecr";
import { VpcResource } from "./constructs/shared/networking/vpc";

export interface AgenticAssistantStackOutputs {
  vpc: VpcResource;
  orderTrackingTable: dynamodb.Table;
  ecrRepository: ecr.Repository;
}

export class AgenticAssistantStack extends cdk.Stack {
  public readonly outputs: AgenticAssistantStackOutputs;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB Table
    const orderTrackingInfo = new dynamodb.Table(this, "OrderTrackingInfo", {
      tableName: "OrderTrackingInfo",
      partitionKey: {
        name: "tracking_number",
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.DEFAULT,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    /**
     * VPC Setup
     **/
    const vpcResource = new VpcResource(this, "McpServerVpc", {
      maxAzs: 2,
    });

    // ECR Repository
    const repository = new ecr.Repository(this, "McpServerRepo", {
      repositoryName: "mcp-server",
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    this.outputs = {
      vpc: vpcResource,
      orderTrackingTable: orderTrackingInfo,
      ecrRepository: repository,
    };

    // Outputs
    new cdk.CfnOutput(this, "ECRRepositoryURI", {
      value: repository.repositoryUri,
    });
  }
}
