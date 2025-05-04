import boto3
from jira import fetch_issues
from config import ACCESS_KEY, SECRET_ACCESS_KEY, REGION
import json
from github_file_content import generate_prompt_template
    
 
def analyse_ticket(input_from_user):
    
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_ACCESS_KEY)  # adjust region if needed


    prompt_template = """You are a bot used for tech support. You will be asked questions based on the provided information.
    
    The user will ask a question, based on the question, look through the codebase to see if you find similar code, and share a potential reason why the user is facing the issue; and if there is an existing ticket for it, based on the ones you remember.
    If you're not able to find code that is related to the specified issue, or if you're not able to find a similar existing support ticket, explicitly mention that. 
    
    The existing tickets and codebase will be provided as context in the first input.
    
    Existing Tickets will be provided with their ticket IDs followed by their title.
    The codebase will contain the name of the file and the code inside of it. 
    
    \n"""
    
    code = generate_prompt_template()
    
    all_tickets = '\n'.join([f"{i['key']}: {i['summary']}" for i in fetch_issues()])
    
    issues = f"""
    Existing Tickets:
    {all_tickets}
    """
    
    codebase = f"""\nCodebase: 
    {code}
    """   
    
    context= prompt_template+issues+codebase+"\n"+"User input: " + input_from_user
    
    
    body = {
    "inferenceConfig": {
        "max_new_tokens": 400,
        "temperature": 0.1,
        "top_p": 0.9
    },
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "text": context,
                },
                
                ]
            }
        ],
    
    }

    try:

        # Call the provisioned model (with inference ARN)
        response = bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId='amazon.nova-lite-v1:0',
            contentType='application/json',
            accept='application/json'
        )
        
        if response:
        
        
            return response['output']['message']['content'][0]['text']
            
    except Exception as e:
            
            return "ERROR from BEDROCK - " + str(e)
