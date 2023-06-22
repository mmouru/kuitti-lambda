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
    const env = {
      'BUCKET_NAME': process.env.BUCKET_NAME ? process.env.BUCKET_NAME : "kuittiprojektistack-kuittibucket47c27659-19ii9u03nrnse"
    }
    const bucket = new s3.Bucket(this, 'KuittiBucket');

    const layerArn = 'arn:aws:lambda:eu-north-1:670964593823:layer:opencv:3';

    const fn = new lambda.Function(this, 'MyLambda', {
      code: lambda.Code.fromAsset(path.join(__dirname, 'lambda-handler')),
      handler: 'lambda.main',
      runtime: lambda.Runtime.PYTHON_3_9,
      environment: env,
      layers: [lambda.LayerVersion.fromLayerVersionArn(this, 'MyLayer', layerArn)],
    });

    const queue = new sqs.Queue(this, "imageQueue");

    fn.addEventSource(new eventsources.SqsEventSource(queue));

    const s3WritePolicy = new iam.PolicyStatement({
      actions: ['*'],
      resources: [`${bucket.bucketArn}/*`], // Use the bucket ARN
    });

    fn.addToRolePolicy(s3WritePolicy);
  }
}
