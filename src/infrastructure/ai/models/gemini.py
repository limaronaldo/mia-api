from decouple import config
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic.types import SecretStr

api_key_value = config("GCLOUD_API_KEY", default=None, cast=SecretStr)

gemini_2_5_pro = ChatGoogleGenerativeAI(
    # model="gemini-2.0-flash",
    model="gemini-2.5-pro",
    api_key=api_key_value,
    temperature=0.3,
)

gemini_2_5_flash = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=api_key_value,
    temperature=0.7,
)

gemini_2_5_flash_lite = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key=api_key_value,
    temperature=0.7,
)
