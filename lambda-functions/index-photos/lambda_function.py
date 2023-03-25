import os
import json
import boto3
import inflect
from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

service = "es"
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    os.environ["AWS_REGION"],
    service,
    session_token=credentials.token,
)
search = OpenSearch(
    hosts=[{"host": os.environ["domainEndpoint"], "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
)

p = inflect.engine()
s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")


def lambda_handler(event, context):
    print(f"Received event: {event}")

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    photo = event["Records"][0]["s3"]["object"]["key"]

    detected_labels = detect_labels(bucket, photo)
    custom_labels = get_custom_labels(bucket, photo)
    all_labels = detected_labels + custom_labels

    print(f"All labels: {all_labels}")

    index_photo(bucket, photo, all_labels)

    return {"statusCode": 200, "body": json.dumps({"labels": all_labels})}


def detect_labels(bucket, photo):
    image_object = {"S3Object": {"Bucket": bucket, "Name": photo}}
    response = rekognition.detect_labels(Image=image_object, MaxLabels=5)
    print(f"DetectLabels response: {response}")
    labels = [process_label(label["Name"]) for label in response["Labels"]]
    return labels


def get_custom_labels(bucket, photo):
    metadata = s3.head_object(Bucket=bucket, Key=photo)["Metadata"]
    print(f"S3 metadata: {metadata}")
    if "customlabels" in metadata:
        return [process_label(label) for label in metadata["customlabels"].split(",")]
    return []


def process_label(word):
    word = word.lower().strip()
    return singular if (singular := p.singular_noun(word)) else word


def index_photo(bucket, photo, labels):
    body = {
        "objectKey": photo,
        "bucket": bucket,
        "createdTimestamp": datetime.now().strftime("%Y-%d-%mT%H:%M:%S"),
        "labels": labels,
    }
    search.index(index="photos", id=photo, body=body)
    print(f"Added photo to index: {body}")
