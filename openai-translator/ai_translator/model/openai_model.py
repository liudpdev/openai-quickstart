import os
import time

import openai
from model import Model
from openai import OpenAI
from utils import LOG


class OpenAIModel(Model):
    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.__default_model = os.getenv("OPENAI_DEFAULT_MODEL") or "gpt-3.5-turbo"

        self.model = model or os.getenv("OPENAI_MODEL")
        self.client = OpenAI(
            api_key=(api_key or os.getenv("OPENAI_API_KEY")),
            base_url=base_url,
        )

    def make_request(self, prompt):
        attempts = 0
        while attempts < 3:
            try:
                if self.model == self.__default_model:
                    response = self.client.chat.completions.create(
                        model=self.model, messages=[{"role": "user", "content": prompt}]
                    )
                    translation = response.choices[0].message.content.strip()
                else:
                    response = self.client.completions.create(
                        model=self.model, prompt=prompt, max_tokens=150, temperature=0
                    )
                    translation = response.choices[0].text.strip()

                return translation, True
            except openai.RateLimitError:
                attempts += 1
                if attempts < 3:
                    LOG.warning(
                        "Rate limit reached. Waiting for 60 seconds before retrying."
                    )
                    time.sleep(60)
                else:
                    raise Exception("Rate limit reached. Maximum attempts exceeded.")
            except openai.APIConnectionError as e:
                attempts += 1
                if attempts < 3:
                    print("The server could not be reached")
                    print(
                        e.__cause__
                    )  # an underlying Exception, likely raised within httpx.            except requests.exceptions.Timeout as e:
                else:
                    raise Exception(
                        "The server could not be reached, Maximum attempts exceeded."
                    )
            except openai.APIStatusError as e:
                print("Another non-200-range status code was received")
                print(e.status_code)
                print(e.response)
            except Exception as e:
                raise Exception(f"发生了未知错误：{e}")
        return "", False
