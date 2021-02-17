from typing import Dict, Tuple, Any


class MiniApi:

    """
    Simple and small api class for returning responses in a pre-prepared JSON form

    """

    def __init__(self, headers: dict) -> None:
        if not isinstance(headers, dict):
            raise Exception(
                "The \"headers\" arg must be a dict. Got \"{}\"".format(type(headers).__name__)
                )
        self.custom_headers = headers


    def ret_error(self,
                message: str = "Unexpected server error occurred.",
                code: int = 200
                ) -> Tuple[Dict[str, object], int, Dict[object, object]]:

        return {
            "ok": False,
            "error_message": message
        }, code, self.custom_headers


    def ret_ok(self,
                title: str = "response",
                result: object = None,
                code: int = 200
                ) -> Tuple[Dict[str, object], int, Dict[Any, Any]]:

        return {
            "ok": True,
            "result": {title: result}
        }, code, self.custom_headers


    def ret_msg(self,
                message: str = "Success",
                code: int = 200
                ) -> Tuple[Dict[str, object], int, Dict[Any, Any]]:

        return {
            "ok": True,
            "message": message
        }, code, self.custom_headers


    @staticmethod
    def query_key_exists(query, key: str) -> bool:

        return bool(query.get(key))
