# 利用openai agent,获取南京当天的实时天气
import openai
import requests
from datetime import datetime

def get_nanjing_weather():
    # 构建 prompt
    prompt = """
    你是一个天气助手。请帮我获取南京市当前的实时天气信息，包括:
    1. 温度
    2. 天气状况(晴/阴/雨等)
    3. 空气质量
    4. 湿度
    只需返回这些基本信息,无需额外解释。
    """
    
    try:
        # 调用 OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个专业的天气助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        # 获取返回结果
        weather_info = response.choices[0].message.content
        return weather_info
        
    except Exception as e:
        return f"获取天气信息失败: {str(e)}"

if __name__ == "__main__":
    weather = get_nanjing_weather()
    print(f"南京实时天气:\n{weather}")


#  你上面获取不了实时的吧，查询过程中需要调用第三方agent

def get_realtime_weather():
    """获取南京实时天气信息"""
    try:
        # 调用和风天气API获取实时数据
        # 实际使用时需要替换为真实的API key
        API_KEY = "your_hefeng_api_key" 
        city_id = "101190101"  # 南京的城市ID
        url = f"https://devapi.qweather.com/v7/weather/now?location={city_id}&key={API_KEY}"
        
        response = requests.get(url)
        data = response.json()
        
        if data["code"] == "200":
            weather_data = data["now"]
            
            # 构建天气信息
            weather_info = {
                "temperature": weather_data["temp"],
                "condition": weather_data["text"],
                "humidity": weather_data["humidity"],
                "windSpeed": weather_data["windSpeed"]
            }
            
            # 获取空气质量数据
            air_url = f"https://devapi.qweather.com/v7/air/now?location={city_id}&key={API_KEY}"
            air_response = requests.get(air_url)
            air_data = air_response.json()
            
            if air_data["code"] == "200":
                weather_info["aqi"] = air_data["now"]["aqi"]
                weather_info["category"] = air_data["now"]["category"]
            
            return weather_info
        else:
            return {"error": "获取天气数据失败"}
            
    except Exception as e:
        return {"error": f"请求异常: {str(e)}"}

def get_nanjing_weather_with_api():
    """结合API和LLM的天气查询"""
    # 获取实时天气数据
    weather_data = get_realtime_weather()
    
    if "error" not in weather_data:
        # 构建带实时数据的prompt
        prompt = f"""
        基于以下南京实时天气数据生成天气报告:
        温度: {weather_data['temperature']}℃
        天气: {weather_data['condition']}
        湿度: {weather_data['humidity']}%
        空气质量指数: {weather_data.get('aqi', '未知')}
        空气质量等级: {weather_data.get('category', '未知')}
        
        请生成简洁的天气总结。
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的天气助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"生成天气报告失败: {str(e)}"
    else:
        return weather_data["error"]

# 更新主函数调用
if __name__ == "__main__":
    weather = get_nanjing_weather_with_api()
    print(f"南京实时天气:\n{weather}")
