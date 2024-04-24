import os
import boto3
import requests

def copy_files_to_s3(contents, bucket_name, github_token, parent_folder=""):
    s3 = boto3.client('s3')
    headers = {'Authorization': f'token {github_token}'}
    
    for content in contents:
        if content['type'] == 'file':
            # If it's a file, copy it to S3
            file_content = requests.get(content['download_url'], headers=headers).content
            s3.put_object(Body=file_content, Bucket=bucket_name, Key=os.path.join(parent_folder, content['name']))
        elif content['type'] == 'dir':
            # If it's a directory, fetch its contents and recursively call copy_files_to_s3
            folder_url = content['url']
            folder_contents = requests.get(folder_url, headers=headers).json()
            copy_files_to_s3(folder_contents, bucket_name, github_token, os.path.join(parent_folder, content['name']))

def lambda_handler(event, context):
    # GitHub repository information
    github_owner = 'Devopsiac765'
    github_repo = 'devopsmdktech'
    github_branch = 'aws_devops'  # Replace with the desired branch
    github_base_url = f'https://api.github.com/repos/{github_owner}/{github_repo}/contents'

    # S3 bucket information
    bucket_name = 'gihub-deploy-890'

    # GitHub Personal Access Token update in envirment variables
    github_token = os.environ['GITHUB_TOKEN']

    # Fetch list of files and folders from GitHub repository
    headers = {'Authorization': f'token {github_token}'}
    response = requests.get(f'{github_base_url}?ref={github_branch}', headers=headers)
    contents = response.json()

    # Copy files and folders to S3
    copy_files_to_s3(contents, bucket_name, github_token)

    return {
        'statusCode': 200,
        'body': 'All files and folders copied from GitHub to S3 successfully'
    }
