from datetime import timedelta
from jwt import encode , decode , exceptions
from datetime import datetime , timedelta
from flask import jsonify

def expire_date(days:int):
    now = datetime.now()
    new_date = now + timedelta(days)
    return new_date



def write_token(data: dict):
    token = encode(payload={**data, "exp" : expire_date(32)},key='xd',algorithm="HS256")
    return token.encode



def valida_token (token,output=False):
    try:
        if output:
            return decode(token ,key='xd', algorithms=['HS256'] )
        decode(token ,key='xd', algorithms=['HS256'])
    except exceptions.DecodeError:
        response = jsonify({"message" : 'Invalid Token'})
        response.status_code = 401
        return response
    except exceptions.ExpiredSignatureError:
        response = jsonify({"message" : 'Token Expired'})
        response.status_code = 401
        return response