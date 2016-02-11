import time
import json

class JsExecutor():
    def __init__(self):
        self.driver = JsExecutor.driver

    def execute(self, url, js):
        self.driver.get(url)
        time.sleep(5)

        result = self.driver.execute_script(js)

        try:
            parsed_result = json.loads(result)
            return parsed_result
        except ValueError:
            raise ValueError('CONFIG is not a valid JSON')