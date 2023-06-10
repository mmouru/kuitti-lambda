import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as eventsources from 'aws-cdk-lib/aws-lambda-event-sources';
import {
  aws_lambda as lambda,
  aws_iam as iam,
  aws_s3 as s3
} from 'aws-cdk-lib';
import * as path from 'path';

export class KuittiprojektiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const bucket = new s3.Bucket(this, 'KuittiBucket');

    const principal = new iam.ServicePrincipal('my-service');

    const fn = new lambda.Function(this, 'MyLambda', {
      code: lambda.Code.fromAsset(path.join(__dirname, 'lambda-handler')),
      handler: 'lambda.main',
      runtime: lambda.Runtime.PYTHON_3_9,
    });

    const queue = new sqs.Queue(this, "imageQueue");

    fn.addEventSource(new eventsources.SqsEventSource(queue));

    const s3WritePolicy = new iam.PolicyStatement({
      actions: ['s3:PutObject'],
      resources: [`${bucket.bucketArn}/*`], // Use the bucket ARN
    });
    fn.addToRolePolicy(s3WritePolicy);
  }
}
