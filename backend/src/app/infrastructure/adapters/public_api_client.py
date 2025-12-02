"""
Клиент для работы с публичными API (API Ninjas для вопросов викторины)
"""

import logging

import httpx

logger = logging.getLogger(__name__)


class PublicApiClient:
    """Клиент для получения данных из API Ninjas"""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        from src.app.setup.config.settings import get_settings

        settings = get_settings()
        self.api_key = api_key or settings.API_NINJAS_KEY
        self.base_url = base_url or settings.API_NINJAS_BASE_URL
        self.timeout = 30.0

        if not self.api_key:
            raise ValueError("API_NINJAS_KEY должен быть установлен в переменных окружения")

    async def get_number_fact(self, number: int) -> dict:
        """Получение вопроса викторины через API Ninjas"""
        url = f"{self.base_url}/trivia"
        params = {"number": number}
        headers = {"X-Api-Key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                logger.info(f"Запрос к API Ninjas: {url}, число: {number}")
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

                logger.info(f"Ответ от API Ninjas (raw): {data}")
                logger.info(f"Тип ответа: {type(data)}")
                data_len = len(data) if isinstance(data, (list, dict)) else "N/A"
                logger.info(f"Длина данных: {data_len}")

                fact_text = ""
                number_value = number

                if isinstance(data, list):
                    if len(data) > 0:
                        fact_data = data[0]
                        logger.info(f"Первый элемент списка: {fact_data}")
                        if isinstance(fact_data, dict):
                            keys = list(fact_data.keys())
                            logger.info(f"Ключи первого элемента: {keys}")
                            question = fact_data.get("question", "")
                            answer = fact_data.get("answer", "")
                            category = fact_data.get("category", "")

                            if question and answer:
                                if category:
                                    fact_text = f"{category}: {question} Ответ: {answer}"
                                else:
                                    fact_text = f"{question} Ответ: {answer}"
                            elif question:
                                fact_text = question
                            elif answer:
                                fact_text = f"Ответ: {answer}"
                            else:
                                fact_text = (
                                    fact_data.get("fact")
                                    or fact_data.get("text")
                                    or fact_data.get("content")
                                    or ""
                                )

                            number_value = fact_data.get("number", number)
                        else:
                            logger.warning(f"Первый элемент не словарь: {type(fact_data)}")
                            fact_text = str(fact_data)
                        logger.info(f"Извлеченный факт: '{fact_text}', число: {number_value}")
                    else:
                        logger.warning(f"Список пуст: {data}")
                        fact_text = f"Вопрос викторины для числа {number} не найден"
                elif isinstance(data, dict):
                    keys = list(data.keys())
                    logger.info(f"Получен словарь, ключи: {keys}")
                    question = data.get("question", "")
                    answer = data.get("answer", "")
                    category = data.get("category", "")

                    if question and answer:
                        if category:
                            fact_text = f"{category}: {question} Ответ: {answer}"
                        else:
                            fact_text = f"{question} Ответ: {answer}"
                    elif question:
                        fact_text = question
                    elif answer:
                        fact_text = f"Ответ: {answer}"
                    else:
                        fact_text = (
                            data.get("fact") or data.get("text") or data.get("content") or ""
                        )

                    number_value = data.get("number", number)
                    logger.info(f"Извлеченный факт: '{fact_text}', число: {number_value}")
                else:
                    logger.warning(f"Неожиданный формат ответа от API: {data} (тип: {type(data)})")
                    fact_text = f"Не удалось обработать ответ: {data}"

                if not fact_text or not fact_text.strip():
                    logger.error(f"Получен пустой факт для числа {number}. Данные: {data}")
                    fact_text = f"Вопрос викторины для числа {number_value} не доступен"

                return {
                    "source": "apininjas",
                    "title": f"Вопрос викторины (число {number_value})",
                    "content": fact_text,
                    "external_id": str(number_value),
                }
        except httpx.ConnectError as e:
            logger.error(f"Ошибка подключения к {url}: {e}")
            raise ConnectionError(f"Не удалось подключиться к API: {e}") from e
        except httpx.TimeoutException as e:
            logger.error(f"Таймаут при запросе к {url}: {e}")
            raise TimeoutError(f"Превышено время ожидания ответа от API: {e}") from e
        except httpx.HTTPStatusError as e:
            error_text = ""
            try:
                error_data = e.response.json()
                error_text = error_data.get("error", str(error_data))
            except Exception:
                error_text = e.response.text

            logger.error(
                f"HTTP ошибка при запросе к {url}: {e.response.status_code} - {error_text}"
            )
            raise ValueError(f"API вернул ошибку {e.response.status_code}: {error_text}") from e
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к {url}: {e}")
            raise

    async def get_random_fact(self) -> dict:
        """Получение случайного вопроса викторины через API Ninjas"""
        url = f"{self.base_url}/facts"
        headers = {"X-Api-Key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                logger.info(f"Запрос к API Ninjas для случайного факта: {url}")
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                logger.info(f"Ответ от API Ninjas (raw): {data}")
                logger.info(f"Тип ответа: {type(data)}")

                fact_text = ""

                if isinstance(data, list) and len(data) > 0:
                    fact_data = data[0]
                    if isinstance(fact_data, dict):
                        question = fact_data.get("question", "")
                        answer = fact_data.get("answer", "")
                        category = fact_data.get("category", "")

                        if question and answer:
                            if category:
                                fact_text = f"{category}: {question} Ответ: {answer}"
                            else:
                                fact_text = f"{question} Ответ: {answer}"
                        elif question:
                            fact_text = question
                        elif answer:
                            fact_text = f"Ответ: {answer}"
                        else:
                            fact_text = fact_data.get("fact", "") or fact_data.get("text", "")
                elif isinstance(data, dict):
                    question = data.get("question", "")
                    answer = data.get("answer", "")
                    category = data.get("category", "")

                    if question and answer:
                        if category:
                            fact_text = f"{category}: {question} Ответ: {answer}"
                        else:
                            fact_text = f"{question} Ответ: {answer}"
                    elif question:
                        fact_text = question
                    elif answer:
                        fact_text = f"Ответ: {answer}"
                    else:
                        fact_text = data.get("fact", data.get("text", ""))
                else:
                    logger.warning(f"Неожиданный формат ответа от API: {data}")
                    fact_text = str(data) if data else "Не удалось получить вопрос"

                if not fact_text or not fact_text.strip():
                    logger.error(f"Получен пустой факт. Данные: {data}")
                    fact_text = "Вопрос викторины не доступен"

                return {
                    "source": "apininjas",
                    "title": "Случайный вопрос викторины",
                    "content": fact_text,
                    "external_id": None,
                }
        except httpx.ConnectError as e:
            logger.error(f"Ошибка подключения к {url}: {e}")
            raise ConnectionError(f"Не удалось подключиться к API: {e}") from e
        except httpx.TimeoutException as e:
            logger.error(f"Таймаут при запросе к {url}: {e}")
            raise TimeoutError(f"Превышено время ожидания ответа от API: {e}") from e
        except httpx.HTTPStatusError as e:
            error_text = ""
            try:
                error_data = e.response.json()
                error_text = error_data.get("error", str(error_data))
            except Exception:
                error_text = e.response.text

            logger.error(
                f"HTTP ошибка при запросе к {url}: {e.response.status_code} - {error_text}"
            )
            raise ValueError(f"API вернул ошибку {e.response.status_code}: {error_text}") from e
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к {url}: {e}")
            raise
