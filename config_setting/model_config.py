model_platform_ls={
    '百度云平台':["ERNIE-Lite-8K","ERNIE-speed-128k"],
    'Groq平台':["gemma-7b-it","llama3-70b-8192","llama3-8b-8192","mixtral-8x7b-32768"],
    'Siliconflow平台':['Qwen/Qwen2-7B-Instruct','THUDM/glm-4-9b-chat','01-ai/Yi-1.5-9B-Chat-16K']
    # 'Google':["gemini-1.5-flash-latest"]
}
model_description_ls = {
    "ERNIE-Lite-8K": {"tokens": 8192, "developer": "Baidu"},
    "ERNIE-speed-128k": {"tokens": 128000, "developer": "Baidu"},
    "gemma-7b-it": {"tokens": 8192, "developer": "Google"},
    "gemini-1.5-flash-latest":{"tokens": 8192, "developer": "Google"},
    "llama3-70b-8192": {"tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"tokens": 8192, "developer": "Meta"},
    "mixtral-8x7b-32768": {"tokens": 32768, "developer": "Mistral"},
    "Qwen/Qwen2-7B-Instruct": {"tokens": 32000, "developer": "Alibaba"},
    "THUDM/glm-4-9b-chat": {"tokens": 32000, "developer": "智谱AI"},
    "01-ai/Yi-1.5-9B-Chat-16K": {"tokens": 16000, "developer": "零一万物"},
}