# input: 找美团，饿了么总监以上级别专家
# output： 找美团（北京三块），饿了么总监以上级别专家
# 那么要使用openai的function call， 把'美团'这类的公司信息拿去调用天眼查api 拿到关联的公司名称 补充进原文, 请你实现这个input -> output
import os
import openai
import requests
from typing import List, Dict

# 配置OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# 配置天眼查API
TIANYANCHA_API_KEY = os.getenv("TIANYANCHA_API_KEY")
TIANYANCHA_API_URL = "https://open.api.tianyancha.com/services/v4/search/company"

def get_company_info(company_name: str) -> Dict:
    """调用天眼查API获取公司信息"""
    headers = {
        "Authorization": TIANYANCHA_API_KEY
    }
    params = {
        "keyword": company_name,
        "pageNum": 1,
        "pageSize": 5
    }
    
    try:
        response = requests.get(TIANYANCHA_API_URL, headers=headers, params=params)
        data = response.json()
        if data["error_code"] == 0:
            return data["result"]["items"][0]
        return None
    except Exception as e:
        print(f"天眼查API调用失败: {str(e)}")
        return None

def expand_company_names(query: str) -> str:
    """使用OpenAI function calling提取和扩展公司名称"""
    
    functions = [
        {
            "name": "get_company_info",
            "description": "获取公司的详细信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "公司名称"
                    }
                },
                "required": ["company_name"]
            }
        }
    ]

    try:
        # 1. 调用OpenAI识别查询中的公司名称
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": "你是一个帮助识别文本中公司名称的助手"},
                {"role": "user", "content": f"请识别以下文本中的公司名称并调用API获取详细信息: {query}"}
            ],
            functions=functions,
            function_call="auto"
        )

        # 2. 处理每个识别出的公司
        expanded_query = query
        if response.choices[0].message.get("function_call"):
            company_name = eval(response.choices[0].message.function_call.arguments)["company_name"]
            company_info = get_company_info(company_name)
            
            if company_info:
                # 替换原文中的公司名称为扩展后的形式
                alias = company_info.get("alias", "")
                if alias:
                    expanded_query = expanded_query.replace(
                        company_name, 
                        f"{company_name}（{alias}）"
                    )

        return expanded_query

    except Exception as e:
        print(f"处理失败: {str(e)}")
        return query

if __name__ == "__main__":
    test_query = "找美团，饿了么总监以上级别专家"
    result = expand_company_names(test_query)
    print(f"原始查询: {test_query}")
    print(f"扩展后查询: {result}")


