import boto3
import botocore.config
import json
import response
from datetime import datetime 

#function to generate the blog 

def blog_generate_bedrock(blogtopic:str) -> str:
    prompt=f"""<s>[INST]Human: write a 200 words blog on the topic {blogtopic}
    Assistant:[/INST]
    """

    body={
        "prompt":prompt,
        "max_gen_len":512,
        "temperature":0.5,
        "top_p":0.9,

    }

    try:
        # calling foundational model
        bedrock=boto3.client("bedrock-runitme",region_name="us-east-1",
                             config=botocore.config.Config(read_timeout=300,retries={'max_attempt':3}))
        response=bedrock.invoke_model(body=json.dumps(body),modelID="mistral.mistral-7b-instruct-v0:2")

        response_content=response.get('body').read() # reading the data
        response_data=json.loads(response_content)
        print(response_data)
        
        # the response generated is will bestored in the keyvariable that is 'generation'
        blog_details=response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error generating the blog:{e}")
        return " "

# to save details in s3_bucket
def save_blog_details_s3(s3_key,s3_bucket,generate_blog): 
    s3=boto3.client('s3')

    try:
        s3.put_object(Bucket=s3_bucket,Key=s3_key,Body=generate_blog)
        print("code saved to s3")

    except Exception as e:
        print("Error when saving the code to s3")

# function for aws lambda using lambda handler

def lambda_handler(event,context):
    # Implementation
    event=json.loads(event['body'])
    blogtopic=event['blog_topic']

    generate_blog=blog_generate_bedrock(blogtopic=blog_generate_bedrock)

    if generate_blog:
        current_time=datetime.now().strftime('%H%M%S')
        # creating s3 bucket key
        s3_key=f"blog_output/{current_time}.txt"
        # s3 bucket name
        s3_bucket='aws_bedrock_course1'
        save_blog_details_s3(s3_key,s3_bucket,generate_blog=)
    else:
        print("No blog is generated")


    return{
        'statusCode':200,
        'body':json.dumps('Blog Generation is completed')
    }