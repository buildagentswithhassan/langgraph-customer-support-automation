import { Construct } from "constructs";
import {
  Vpc,
  SubnetType,
  InstanceType,
  InstanceClass,
  InstanceSize,
  Peer,
  Port,
} from "aws-cdk-lib/aws-ec2";
import { StackProps } from "aws-cdk-lib";
import { FckNatInstanceProvider } from "cdk-fck-nat";

export interface VpcResourceProps extends StackProps {
  maxAzs?: number;
}

export class VpcResource extends Construct {
  public readonly vpc: Vpc;

  constructor(scope: Construct, id: string, props: VpcResourceProps) {
    super(scope, id);

    const natGatewayProvider = new FckNatInstanceProvider({
      instanceType: InstanceType.of(InstanceClass.T4G, InstanceSize.NANO),
    });

    this.vpc = new Vpc(this, "McpServerVpc", {
      vpcName: "McpServerVpc",
      maxAzs: props.maxAzs ?? 2,
      natGatewayProvider: natGatewayProvider,
      subnetConfiguration: [
        {
          name: "PublicSubnet",
          subnetType: SubnetType.PUBLIC,
          cidrMask: 24,
        },
        {
          name: "PrivateSubnet",
          subnetType: SubnetType.PRIVATE_WITH_EGRESS,
          cidrMask: 24,
        },
      ],
    });

    natGatewayProvider.securityGroup.addIngressRule(
      Peer.ipv4(this.vpc.vpcCidrBlock),
      Port.allTraffic()
    );
  }
}
