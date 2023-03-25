import os
import time
import json
import boto3
import inflect
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
lex = boto3.client("lexv2-runtime")
s3 = boto3.client("s3")


def lambda_handler(event, context):
    print(f"Received event: {event}")
    response_body = {"results": get_photo_urls(event)}
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET",
        },
        "body": json.dumps(response_body),
    }


def get_photo_urls(event):
    if (params := event.get("queryStringParameters")) and (query := params.get("q")):
        query_terms = get_query_terms(query)
        print(f"Query terms: {query_terms}")
        photo_urls = search_photos(query_terms)
        print(f"Photo URLs: {photo_urls}")
        return photo_urls
    return []


def get_query_terms(query):
    response = lex.recognize_text(
        botId=os.environ["lexBotId"],
        botAliasId=os.environ["lexBotAliasId"],
        localeId="en_US",
        sessionId=str(time.time_ns()),
        text=query,
    )
    print(response)

    slots = response["sessionState"]["intent"]["slots"]
    query_term_1 = process_query_term(try_ex(slots.get("query_term_1")))
    query_term_2 = process_query_term(try_ex(slots.get("query_term_2")))
    return list(filter(lambda t: t, [query_term_1, query_term_2]))


def try_ex(value):
    if value is not None:
        return value["value"].get("interpretedValue", None)
    return None


def process_query_term(word):
    if word is not None:
        word = word.lower().strip()
        return singular if (singular := p.singular_noun(word)) else word
    return None


def search_photos(query_terms):
    search_results = []
    included_object_keys = set()
    for query_term in query_terms:
        response = search.search({"query": {"match": {"labels": query_term}}})
        print(f"Search for {query_term}: {response}")
        for hit in response["hits"]["hits"]:
            bucket = hit["_source"]["bucket"]
            object_key = hit["_source"]["objectKey"]
            labels = hit["_source"]["labels"]
            photo_url = s3.generate_presigned_url(
                ClientMethod="get_object", Params={"Bucket": bucket, "Key": object_key}
            )
            if object_key not in included_object_keys:
                included_object_keys.add(object_key)
                search_results.append({"url": photo_url, "labels": labels})
    return search_results
