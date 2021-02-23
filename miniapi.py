from typing import Dict, Tuple, Any


class MiniApi:

    """
    Simple and small api class for returning responses in a pre-prepared JSON form

    """

    DefaultResponseFormat = Tuple[Dict[str, object], int, Dict[Any, Any]]

    def __init__(this, headers: dict) -> None:
        if not isinstance(headers, dict):
            raise Exception(
                "The \"headers\" arg must be a dict. Got \"{}\"".format(type(headers).__name__)
                )
        this.custom_headers = headers


    def ret_error(this,
                message: str = "Unexpected server error occurred.",
                description: str = "no description",
                code: int = 200
                ) -> DefaultResponseFormat:

        return {
            "ok": False,
            "error_message": message,
            "description": description
        }, code, this.custom_headers


    def ret_ok(this,
                title: str = "response",
                result: object = None,
                code: int = 200
                ) -> DefaultResponseFormat:

        return {
            "ok": True,
            "result": {title: result}
        }, code, this.custom_headers


    def ret_msg(this,
                message: str = "Success",
                code: int = 200
                ) -> DefaultResponseFormat:

        return {
            "ok": True,
            "message": message
        }, code, this.custom_headers


    @staticmethod
    def query_key_exists(query, key: str) -> bool:

        return bool(query.get(key))
