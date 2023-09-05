import os
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import ssl
import websocket
import langchain
import logging
# from Config import config
from urllib.parse import urlparse
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from typing import Optional, List, Dict, Mapping, Any
from langchain.llms.base import LLM
from langchain.cache import InMemoryCache
import gradio as gr

logging.basicConfig(level=logging.INFO)
# 启动llm的缓存
langchain.llm_cache = InMemoryCache()
result_list = []
# SPARK_APPID = config.SPARK_APPID
# SPARK_API_KEY = config.SPARK_API_KEY
# SPARK_API_SECRET = config.SPARK_API_SECRET

SPARK_APPID = os.environ.get('SPARK_APPID')
SPARK_API_KEY = os.environ.get('SPARK_API_KEY')
SPARK_API_SECRET = os.environ.get('SPARK_API_SECRET')

def _construct_query(prompt, temperature, max_tokens):
    data = {
        "header": {
            "app_id": SPARK_APPID,
            "uid": "1234"
        },
        "parameter": {
            "chat": {
                "domain": "general",
                "random_threshold": temperature,
                "max_tokens": max_tokens,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": [
                    {'role':'system', 'content':"你是一名专业精神病医生，你的任务是使用用户的语言执行以下操作: \
                    1. 详细说明用户询问的精神病。 \
                    2，根据用户询问的疾病，给出了精神病院最常用的诊断量表。\
                    3，根据用户对结果进行评分和解读，最终提供有用的治疗建议。"},
                    {'role': 'user', 'content': '请为我科普并介绍一下抑郁症' },
                    {'role': 'assistant','content': '抑郁症是一种常见的心理疾病，以连续且长期的心情低落为主要的临床特征，\
                    是现代人心理疾病最重要的类型之一。全球约有3.8%的人口受到影响，其中5.0%为成年人，5.7%为60岁以上成年人。\
                    抑郁症不同于通常的情绪波动和对日常生活中挑战产生的短暂情绪反应。尤其是当抑郁症反复发病，并达到中度或重度时，可能成为一个严重的健康疾患。\
                    抑郁症的症状包括：心情低落、失去兴趣、缺乏活力、睡眠障碍、食欲改变、注意力不集中、自我评价过低等。如果您感到自己有以上症状，请及时就医。'},
                    {'role': 'user', 'content': '如果可以的话，请准确打印精神病院最常用的抑郁症量表之一，包括全部内容'},
                    {'role': 'assistant', 'content': "以下是常用的抑郁症量表之一：汉密尔顿抑郁量表（Hamilton Depression Rating Scale，简称HDRS或HAMD）。\
                     该量表通常包括以下17项问题：\
                     1.您感到非常沮丧或苦闷吗？（0分表示“没有”，1分表示“有一点”，2分表示“中等程度”，3分表示“有点严重”，4分表示“很严重”）\
                     2.您感到一般兴趣减退了吗？（0分表示“完全没兴趣”，1分表示“有点没兴趣”，2分表示“中等程度”，3分表示“有点感兴趣”，4分表示“非常感兴趣”）\
                     3.您感到自己是个失败者吗？（0分表示“不是”，1分表示“有一点”，2分表示“中等程度”，3分表示“有点”，4分表示“完全是”）\
                     4.您感到失落、没希望吗？（0分表示“完全不是”，1分表示“有一点”，2分表示“中等程度”，3分表示“有点”，4分表示“非常”）\
                     5.您感到自己没有价值吗？（0分表示“完全不是”，1分表示“有一点”，2分表示“中等程度”，3分表示“有点”，4分表示“非常”）\
                     6.您感到疲乏吗？（0分表示“完全不疲乏”，1分表示“有一点”，2分表示“中等程度”，3分表示“有点”，4分表示“非常”）\
                     7.您感到自责吗？（0分表示“完全没有”，1分表示“有一点”，2分表示“中等程度”，3分表示“有点”，4分表示“非常”）\
                     8.您感到自卑吗？（0分表示“完全没有”，1分表示“有一点”，2分表示“中等程度”，3分表示“有点”，4分表示“非常”）\
                     9.您感到不安、焦虑吗？（0分表示“完全没这感觉”，1分表示“有一点”，2分表示“中等程度”，3分表示“有点”，4分表示“非常”）\
                     10.您对未来感到悲观吗？（0分表示“完全不是”，1分表示“有一点”，2分表示“中等程度”，3分表示“有点”，4分表示“非常”）\
                     11.您睡眠不好吗？（0分表示“睡得很好”，1分表示“睡得一般般”，2分表示“睡得不太好”，3分表示“睡得很差劲”, 4分 表示“完全失眠”）\
                     12.您食欲有变化吗？（0分表示 “完全正常”，1 分代表 “有些变化”、2 分代表 “变化明显”、3 分代表 “变化非常大”、4 分为 “非常多变化”)\
                     13.您感到急躁吗？（0 分代表 “完全没这感觉”、1 代表 “有一点”、2 代表 “中等程度”、3 代表 “有点”、4 代表 “非常明显”)\
                     14.您动作缓慢吗？（0 代表 “完全没这感觉”、1 代表 “有一点”、2 代表 “中等程度”、3 代表 “有点”、4 代表 “非常明显”)\
                     15.您注意力难以集中吗？（0 代表 “完全没问题”、1 代表 “有时候会分散注意力”、2 代表 “经常无法集中注意力”、3 代表 “非常难以集中注意力”)\
                     16.您做决定的能力下降了吗？（0 代表 “完全没这感觉”、1 代表 “有时候会这样”、2 代表 “经常如此”、3 代表 “非常频繁”)\
                     17.您因病情影响到了工作和日常生活吗？（0 代表 “完全没有影响”、1 代表 “有时候会这样”、2 代表 “经常如此”、3 代表 “非常有影响”)"},
                    {'role': 'user', 'content': '用户量表填写：1. 1; 2. 2; 3. 2; 4. 1; 5. 3; 6. 2; 7.1; 8. 2; 9. 2; 10. 0; 11. 1; 12. 2; 13. 2; 14.1; 15. 2; 16. 1; 17. 2。请根据填写的选项打印出正确的总分并进行分析，最后给出专业的治疗建议。'},
                    {'role': 'assistant', 'content': '根据您填写的汉密尔顿抑郁量表得分，您的总分为：1+2+2+1+3+2+1+2+2+0+1+2+2+1+2+1+2 = 27分。这个得分在17-30分之间被认为是轻度抑郁症，需要进一步关注和治疗。\
                     您的分数分布比较均匀，但有少数几个问题得分较高。建议您寻求专业心理医生的帮助，进行详细的评估和诊断。\
                     对于轻度抑郁症的治疗，可以尝试以下方法：\
                     心理治疗：认知行为疗法、解决问题疗法、人际治疗等都可以有效缓解轻度抑郁症的症状。\
                     药物治疗：医生可能会考虑给您开一些抗抑郁药物，如选择性5-羟色胺再摄取抑制剂（SSRI）。\
                     生活方式调整：适当的运动、规律的作息、均衡的饮食、保持社交活动等都有助于缓解抑郁症状。\
                     需要注意的是，抑郁症是一种严重的疾病，需要得到专业的诊断和治疗。如果您感到情绪低落、失去兴趣等症状持续时间较长，建议尽快就医寻求帮助。'},
                    {"role": "user", "content": prompt}
                ]
            }
        }
    }
    return data
exp = [['prompt示例1：请为我科普并介绍一下抑郁症'],
    ['prompt示例2：如果可以的话，请准确打印精神病院最常用的抑郁症量表之一，包括全部内容'],
    ['prompt示例3：用户量表填写：1. 1; 2. 2; 3. 2; 4. 1; 5. 3; 6. 2; 7.1; 8. 2; 9. 2; 10. 0; 11. 1; 12. 2; 13. 2; 14.1; 15. 2; 16. 1; 17. 2。请根据填写的选项打印出正确的总分并进行分析，最后给出专业的治疗建议。']
]

def _run(ws, *args):
    data = json.dumps(
        _construct_query(prompt=ws.question, temperature=ws.temperature, max_tokens=ws.max_tokens))
    # print (data)
    ws.send(data)


def on_error(ws, error):
    print("error:", error)


def on_close(ws):
    print("closed...")


def on_open(ws):
    thread.start_new_thread(_run, (ws,))


def on_message(ws, message):
    data = json.loads(message)
    code = data['header']['code']
    # print(data)
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        result_list.append(content)
        if status == 2:
            ws.close()
            setattr(ws, "content", "".join(result_list))
            print(result_list)
            result_list.clear()


class Spark(LLM):
    '''
    根据源码解析在通过LLMS包装的时候主要重构两个部分的代码
    _call 模型调用主要逻辑,输入问题，输出模型相应结果
    _identifying_params 返回模型描述信息，通常返回一个字典，字典中包括模型的主要参数
    '''

    gpt_url = "ws://spark-api.xf-yun.com/v1.1/chat"  # spark官方模型提供api接口
    host = urlparse(gpt_url).netloc  # host目标机器解析
    path = urlparse(gpt_url).path  # 路径目标解析
    max_tokens = 2048
    temperature = 0.5

    # ws = websocket.WebSocketApp(url='')

    @property
    def _llm_type(self) -> str:
        # 模型简介
        return "Spark"

    def _get_url(self):
        # 获取请求路径
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        signature_sha = hmac.new(SPARK_API_SECRET.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{SPARK_API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        url = self.gpt_url + '?' + urlencode(v)
        return url

    def _post(self, prompt):
        #模型请求响应
        websocket.enableTrace(False)
        wsUrl = self._get_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error,
                                    on_close=on_close, on_open=on_open)
        ws.question = prompt
        setattr(ws, "temperature", self.temperature)
        setattr(ws, "max_tokens", self.max_tokens)
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return ws.content if hasattr(ws, "content") else ""

    def _call(self, prompt: str,
              stop: Optional[List[str]] = None) -> str:
        # 启动关键的函数
        content = self._post(prompt)
        # content = "这是一个测试"
        return content

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """
        Get the identifying parameters.
        """
        _param_dict = {
            "url": self.gpt_url
        }
        return _param_dict




if __name__ == "__main__":
    llm = Spark(temperature=0.5)
    # result = llm("如果可以的话，请准确打印精神病院最常用的抑郁症量表之一，包括全部内容")
    # print(result)
    # print(type(result))
    input_text = gr.inputs.Textbox(label="请输入您想咨询的精神相关疾病（如：抑郁症、焦虑症、自闭症、精神分裂症等）")

    output_text = gr.outputs.Textbox(label="参考性诊断回答")

    interface = gr.Interface(fn=llm, inputs=[input_text], outputs=[output_text],
                             examples= exp,
                             title="ChatPSY-精神诊疗",
                             description="1）. 首先，我们需要了解您所询问的精神病具体是什么。请您详细描述一下这种症状，包括出现的时间、持续时间、严重程度以及是否伴随其他相关症状（如焦虑、抑郁等）\n\
                                        2）. 针对您提到的疾病，我为您推荐以下几种常用的精神病诊断量表：\n\
                                        - 汉密尔顿抑郁量表（HAMD）：评估抑郁症状的严重程度。\n\
                                        - 汉密尔顿焦虑量表（HAMA）：评估焦虑症状的严重程度。\n\
                                        - 明尼苏达多相个性问卷（MMPI）：评估个体的心理状况和人格特征。\n\
                                        - 阳性和阴性症状评定量表（PANSS）：评估精神分裂症状的严重程度。\n\
                                        3）. 根据您对结果的评分和解读，我们可以初步判断您可能患有某种精神疾病。具体的诊断和治疗建议需要结合您的病史、家族史以及临床表现来制定。以下是一些建议供您参考：\n\
                                        - 如果您的评分较高或超过某个阈值，建议您尽快前往医院就诊，接受专业医生的面对面评估。\n\
                                        - 在确诊后，医生会根据您的具体情况制定个性化的治疗方案，可能包括药物治疗、心理治疗或其他综合治疗方法。\n\
                                        - 请务必按照医生的建议定期复查和调整治疗方案，以确保病情得到有效控制。\n\
                                        - 同时，保持良好的生活习惯和心理状态对精神病的治疗和康复也非常重要。请注意保持充足的睡眠、均衡的饮食、适当的运动以及积极的心态。",
                             css="body {background-color: red; font-size: large}",
                             article="以上是demo的描述和一些prompt的使用，示例1，2，3按顺序输入。\n\
                             注意：在填写量表环节请勿直接点击示例3，而是复制它进行改写：\n\
                             （更改为对应的精神疾病名称）抑郁症量表填写：1. 1; 2. 2; 3. 2; 4. 1; 5. 3; 6. 2; 7.1; 8. 2; 9. 2; 10. 0; 11. 1; 12. 2; 13. 2; 14.1; 15. 2; 16. 1; 17. 2。请根据填写的选项打印出正确的总分并进行分析，最后给出专业的治疗建议。")
    interface.launch()
