import json
import os

import langextract as lx
from dotenv import load_dotenv

from poligrapher.utils import parse_results_from_response, write_jsonl


class Extractor:
    def __init__(self, llm):
        self.llm = llm

        prompt_path = "data/instructions/privacy_policy_extraction_prompt.md"
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.privacy_policy_extraction_prompt = f.read()

        self.response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "policy_extraction_output",
                "schema": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "category": {"type": "string"},
                                    "label": {"type": "string"},
                                    "purpose": {"type": "string"},
                                    "situation": {"type": "string"},
                                    "subject": {"type": "string"},
                                },
                                "required": [
                                    "name",
                                    "category",
                                    "label",
                                    "purpose",
                                    "situation",
                                    "subject",
                                ],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["entities"],
                    "additionalProperties": False
                }
            }
        }

    def extract(self, input_text: str):
        system_prompt = self.privacy_policy_extraction_prompt
        user_prompt = f"# Privacy Policy:\n{input_text}"
        response, _ = self.llm.generate_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=self.response_format
        )
        result = parse_results_from_response(response)
        write_jsonl(result, "output/llm_extracted_results.jsonl")
        return result

    @DeprecationWarning
    def extract_by_lang(self, input_text: str):
        system_prompt = """
        请从隐私政策文本中解析所有可能被采集或者使用的个人相关信息，包括但不限于个人基础信息、个人身份信息、个人行为数据、个人设备信息等
        """
        prompt_path = "data/instructions/another_prompt.md"
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        text = """
        1. 账号注册登录
        1）功能描述：为了使用本应用的基本业务功能，您需要先注册账号并登录。
        2）必要个人信息： 为了注册账号以使用我们的基本业务功能， 
        您至少需要提供手机号码 （是为了履行国家法律法规关于网络实名制 （真实身份信息认证） 义务所必需）， 
        我们将通过向该手机号码发送短信验证码的方式来验证您的身份是否有效。 
        我们采取了统一账号体系， 即您在贝壳旗下任一产品（包含贝壳找房、链家、贝壳租房、贝壳美家商城、被窝家装、圣都整装、 
        设牛 AI、 贝壳团装 Lite、 贝壳家庭服务 App （如有） 和/或小程序 （如有） ） 通过上述方式注册后， 
        将生成统一的贝壳账号（我们内部使用账号ID 来标识您的网络身份， 该账号 ID 与您注册时提供的手机号码相关联） ，
        您可凭借该账号登录访问和使用其他贝壳旗下产品。 请您知悉， 为向您提供一致的用户体验和安全认证，
        一方面您基于注册该账号向我们提供的（如手机号码）、和与该账号相关的信息（如账号 ID）由贝壳统一存储管理； 
        另一方面您的贝壳账号信息可能会在贝壳旗下产品内共享使用， 详情请见《第三方共享信息清单》中的《关联方共享信息清单》。
        为了登录账号以使用我们的基本业务功能， 您需选择手机快捷登录或账号密码登录， 
        同时根据您选择的登录方式自主提供手机号码、 短信验证码或手机号码、 账号密码， 以完成身份核验。 短信验证码、 账号密码可能属于
        您的敏感个人信息， 我们收集该信息以验证您的身份使得您可以使用手机快捷登录或账号密码登录。
        若您拒绝提供上述个人信息， 您将无法注册成为我们的用户或登录本应用并使用基本业务功能，但您还可以使用浏览及搜索服务。
        2. 信息浏览及搜索
       （1） 功能描述： 我们通过该功能为您提供全部二手房房源、 商铺房源、 新房楼盘、租赁房源、新房地块等信息，
        并为您提供房源、装修等信息的筛选、搜索服务。
       （2） 必要个人信息：当您浏览、点击、搜索、查看本产品内的房源、装修等信息时， 
        我们会自动根据您的基本设备信息 （设备型号、 设备信息、品牌名称、屏幕参数、操作系统版本、设备设置、设备指纹、电池状态、内存容量、
        存储容量、系统类型、系统版本）、WIFI 信息（WIFI 列表）为您展示与您使用设备相适配的房源、 装修等信息样式； 
        在您浏览、 点击、 搜索、查看过程中， 我们会收集您的使用情况 （浏览、点击、 搜索、查看记录），作为服务网络日志保存。
       （3） 其他相关个人信息： 如您未登录账号， 我们会收集您的设备标识符 （IDFA、IDFV、Android OAID、HarmonyOS OAID、Android ID，我们根据您的设备类型获取上述部分设备信息）
        来记录您的使用情况。如您已登录账号，我们会通过您的账号 ID 来记录您的使用情况。
       （4） 其他相关权限： 我们会调用您的电话权限（部分机型） ， 以获取您的设备标识符。 我们不会主动调用上述权限， 仅在您使用本应用过程中并授予上述权限后，
        我们会使用上述信息以记录您在本应用的使用情况。请您注意， 如您的搜索关键词信息无法识别您的身份， 其将不属于您的个人信息， 
        我们有权在法律法规允许的范围内对其进行自主使用； 只有当您的搜索关键词信息单独或与您的其他信息相互结合使用并可以识别您的身份时， 
        则在单独或结合使用期间， 我们会将您的搜索关键词信息作为您的个人信息，与您的搜索历史记录一同按照本声明对其进行处理与保护。
        """

        examples = [
            lx.data.ExampleData(
                text=text,
                extractions=[
                    lx.data.Extraction(
                        extraction_class="PersonalBasicInformation",
                        extraction_text="手机号码",
                        attributes={"name": "手机号码", "category": "个人基本资料/个人基本资料", "label": "L4", "purpose": "账号注册登录",
                                    "situation": "发送短信验证码", "subject": "用户"}
                    ),
                    lx.data.Extraction(
                        extraction_class="PersonalBehaviorInformation",
                        extraction_text="浏览、点击、 搜索、查看记录",
                        attributes={"name": "浏览、点击、 搜索、查看记录", "category": "个人标签信息/个人标签信息", "label": "L3", "purpose": "服务网络日志保存",
                                    "situation": "浏览、点击、搜索、查看本产品内的房源、装修等信息时", "subject": "用户"}
                    ),
                    lx.data.Extraction(
                        extraction_class="PersonalDeviceInformation",
                        extraction_text="Android ID",
                        attributes={"name": "Android ID", "category": "个人设备信息/可变更的唯一设备识别码", "label": "L3",
                                    "purpose": "展示与使用设备相适配的房源、 装修等信息样式", "situation": "浏览、点击、搜索、查看本产品内的房源、装修等信息时",
                                    "subject": "用户"}
                    ),
                ]
            )
        ]

        result = lx.extract(
            text_or_documents=input_text,
            prompt_description=system_prompt,
            examples=examples,
            model_id="gpt-4o-mini",
            api_key=os.environ.get('OPENAI_API_KEY'),
            fence_output=True,
            use_schema_constraints=False
        )

        entities = {}

        for extraction in result.extractions:
            print(f"\n🏢 Personal Information:")
            print(f"   Class: {extraction.extraction_class}")
            print(f"   Text: {extraction.extraction_text}")
            print(f"   Attributes: {json.dumps(extraction.attributes, indent=2)}")
            if extraction.attributes and 'name' in extraction.attributes:
                entities[extraction.attributes['name']] = extraction.attributes

        temp = []
        for key, value in entities.items():
            temp.append(value)

        write_jsonl(temp, "output/entities.jsonl")
        return result