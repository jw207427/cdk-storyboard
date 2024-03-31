import json
from templates import PromptTemplate
import boto3
from botocore.config import Config

# initialize bedrock runtime
boto_config = Config(
    connect_timeout=1,
    read_timeout=300,
    retries={'max_attempts': 1}
)

boto_session = boto3.Session()

bedrock_runtime = boto_session.client(
    service_name="bedrock-runtime", 
    config=boto_config
)

# model id
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

# initialize the PromptTemplate
prompt_template = PromptTemplate()

# invoke claude3 to scene generation
def invoke_claude3(image_base64=None, text_query="What is in this image?"):

    content = []

    img_obj = dict()
    query_obj = {"type": "text", "text": text_query}

    if image_base64:
        img_obj["type"] = "image"
        img_obj["source"] = {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": image_base64,
        }
        content.append(img_obj)

    content.append(query_obj)

    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
        }
    )

    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=body)

    response_body = json.loads(response.get("body").read())

    return response_body

# main lambda function
def lambda_handler(event, context):

    usages = []

    story_idea = event.get('story_idea')
    number_of_scenes = event.get('number_of_scenes', 1)
    themes = event.get('themes', 'comedy')

    scenes_template = prompt_template.get_scenes_template()

    prompt = scenes_template.replace("{idea}", story_idea)
    prompt = prompt.replace("{theme}", themes)
    prompt = prompt.replace("{number}", str(number_of_scenes))

    # Call the Amazon Bedrock Claude3 Sonnet model here and get the response
    model_response = invoke_claude3(text_query=prompt)

    output = model_response["content"][0]['text']
    usages.append(model_response['usage'])

    try:
        scenes = json.loads(output)
    except json.JSONDecodeError:
        # If the model response is not a valid JSON, try again
        retries = 3
        for _ in range(retries):
            model_response = invoke_claude3(text_query=prompt)

            output = model_response["content"][0]['text']
            usages.append(model_response['usage'])

            try:
                scenes = json.loads(output)
                break
            except json.JSONDecodeError:
                pass
        else:
            # If all retries fail, return an error message
            return {'error': 'Failed to generate a valid storyboard'}

    return {
            "statusCode": 200,
            "scenes": scenes,
            "usages": usages
        }