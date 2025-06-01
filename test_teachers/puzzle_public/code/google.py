import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image

# 配置项
SCOPES = ['https://www.googleapis.com/auth/drive.file']  # 权限范围
PARENT_FOLDER_ID = '1jBIlw9rucyRCsvUgN_5uJJt6mA4hzElL'  # 留空则上传到根目录
INPUT_FOLDER = '../data/dev/figures'  # 例如：'./images'
OUTPUT_JSON = '../data/dev/image_urls.json'  # 保存URL的JSON文件
CREDENTIALS_FILE = 'siiimages-95b89fa1f4ae.json'  # 下载的凭证文件

def get_credentials():
    """获取或刷新访问令牌"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 若没有有效令牌，发起认证流程
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        # 保存令牌到文件
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def upload_image(service, file_path, parent_folder_id):
    """上传单个图片并返回公开URL"""
    file_name = os.path.basename(file_path)
    mime_type = Image.open(file_path).mime_type  # 自动检测MIME类型
    
    # 创建文件元数据
    file_metadata = {
        'name': file_name,
        'mimeType': mime_type,
        'parents': [parent_folder_id] if parent_folder_id else []
    }
    
    # 上传文件
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    # 获取公开URL（需手动设置为“任何人可查看”）
    file_id = file['id']
    service.files().update(
        fileId=file_id,
        body={'permissions': [{'type': 'anyone', 'role': 'reader'}]}
    ).execute()
    
    # 生成直接下载链接（更适合API访问）
    public_url = f'https://drive.google.com/uc?id={file_id}'
    return {
        'file_name': file_name,
        'file_id': file_id,
        'public_url': public_url
    }

def main():
    # 初始化Google Drive API服务
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    # 创建输出目录
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    
    # 遍历本地图片文件
    image_urls = []
    for root, _, files in os.walk(INPUT_FOLDER):
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
                file_path = os.path.join(root, file)
                print(f'上传文件: {file_path}')
                
                try:
                    result = upload_image(service, file_path, PARENT_FOLDER_ID)
                    image_urls.append(result)
                except Exception as e:
                    print(f'上传失败: {file_path}, 错误: {str(e)}')
    
    # 保存URL到JSON文件
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(image_urls, f, ensure_ascii=False, indent=2)
    
    print(f'上传完成，保存{len(image_urls)}个文件的URL到{OUTPUT_JSON}')

if __name__ == '__main__':
    main()