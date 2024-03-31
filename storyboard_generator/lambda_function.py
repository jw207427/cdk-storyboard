import json
import boto3
import base64
from PIL import Image
from helper import create_scene_images
import io

smr = boto3.client("sagemaker-runtime")
endpoint_name = "endpoint-SDXL-Storyboard-2024-03-16-23-30-53-696"

def _encode(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    img_byte_arr = base64.b64encode(img_byte_arr).decode()
    return img_byte_arr

def _decode(image):
    image = base64.b64decode(image)
    image = Image.open(io.BytesIO(image))
    return image

def lambda_handler(event, context):
    try:
        # Parse the input payload
        body = json.loads(event["body"])
        prompt = body.get("prompt")
        nprompt = body.get("nprompt")
        seed = body.get("seed", 0)
        steps = body.get("steps", 4)
        height = body.get("height", 1024)
        width = body.get("width", 1024)

        # Invoke the SageMaker endpoint
        response_model = smr.invoke_endpoint(
            EndpointName=endpoint_name,
            Body=json.dumps(
                {
                    "prompt": prompt,
                    "nprompt": nprompt,
                    "seed": seed,
                    "steps": steps,
                    "h": height,
                    "w": width,
                }
            ),
            ContentType="application/json",
        )

        # Process the response from the SageMaker endpoint
        output = json.loads(response_model["Body"].read().decode("utf8"))["outputs"]
        image = _decode(output)

        # Add close caption for the image
        caption_image = create_scene_images(prompt, image)
        
        image_base64 = _encode(caption_image)
        # Return the generated image as the response
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "image/png",
            },
            "body": image_base64,
            "isBase64Encoded": True,
        }

    except Exception as e:
        # Handle exceptions
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": str(e)}),
        }