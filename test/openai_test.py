from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())#加载环境变量
client = OpenAI(base_url="https://api.siliconflow.cn/v1")
response = client.chat.completions.create(
    model='alibaba/Qwen1.5-110B-Chat',
    messages=[
        {'role': 'user', 'content': "抛砖引玉是什么意思呀"}
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content)