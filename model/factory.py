import os
from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from utils.config_handler import rag_conf

# ============================================================
# API 调用区域配置
# domestic  = 国内版 dashscope（推荐，使用原生封装）
# international = 新加坡地域 OpenAI 兼容端
# ============================================================
API_REGION = rag_conf.get("api_region", "domestic")

# 检查环境变量
api_key = os.getenv("DASHSCOPE_API_KEY") or ""
if not api_key:
    raise ValueError("DASHSCOPE_API_KEY 未设置，请在环境变量中配置")


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    """聊天模型工厂 - 根据 api_region 配置选择调用方式"""

    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        if API_REGION == "domestic":
            # ============================================
            # 国内版 dashscope API（原生调用）
            # ============================================
            from langchain_community.chat_models.tongyi import ChatTongyi
            return ChatTongyi(model=rag_conf["chat_model_name"])

        elif API_REGION == "international":
            # ============================================
            # 新加坡地域 OpenAI 兼容端
            # ============================================
            from langchain_openai import ChatOpenAI
            DASHSCOPE_COMPAT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
            return ChatOpenAI(
                model=rag_conf["chat_model_name"],
                api_key=lambda: api_key,
                base_url=DASHSCOPE_COMPAT_BASE_URL,
                temperature=0.7,
            )
        else:
            raise ValueError(f"未知的 api_region: {API_REGION}，可选值: domestic, international")


class EmbeddingsFactory(BaseModelFactory):
    """Embeddings 模型工厂 - 根据 api_region 配置选择调用方式"""

    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        if API_REGION == "domestic":
            # ============================================
            # 国内版 dashscope API（原生调用）
            # ============================================
            from langchain_community.embeddings import DashScopeEmbeddings
            return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])

        elif API_REGION == "international":
            # ============================================
            # 新加坡地域 OpenAI 兼容端
            # ============================================
            from openai import OpenAI

            DASHSCOPE_COMPAT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

            class DashscopeCompatEmbeddings(Embeddings):
                """直接用 OpenAI 客户端调用兼容端，避免 contents 结构错误。"""

                def __init__(self, model: str, api_key: str, base_url: str):
                    self.model = model
                    self.client = OpenAI(api_key=api_key, base_url=base_url)

                def embed_documents(self, texts: list[str]) -> list[list[float]]:
                    safe_texts = [str(t) for t in texts]
                    resp = self.client.embeddings.create(model=self.model, input=safe_texts)
                    return [item.embedding for item in resp.data]

                def embed_query(self, text: str) -> list[float]:
                    return self.embed_documents([str(text)])[0]

            return DashscopeCompatEmbeddings(
                model=rag_conf["embedding_model_name"],
                api_key=api_key,
                base_url=DASHSCOPE_COMPAT_BASE_URL,
            )
        else:
            raise ValueError(f"未知的 api_region: {API_REGION}，可选值: domestic, international")


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()