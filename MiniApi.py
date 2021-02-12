
class MiniApi:
    
    def __init__(self, headers):
        if not isinstance(headers, dict):
            raise Exception("The \"headers\" parameter must be a dict. Got \"{}\"".format(type(headers).__name__))
        self.custom_headers = headers


    def ret_error(self, message="Unexpected server error occurred.", code=200):
        
        return {
            "ok": False,
            "error_message": message
        }, code, self.custom_headers


    def ret_ok(self, title="response", result=[], code=200):
        
        return {
            "ok": True,
            "result": {title: result}
        }, code, self.custom_headers


    def ret_msg(self, message="Success", code=200):
        
        return {
            "ok": True,
            "message": message
        }, code, self.custom_headers


    @staticmethod
    def query_key_exists(query, key):
        
        return bool(query.get(key))

