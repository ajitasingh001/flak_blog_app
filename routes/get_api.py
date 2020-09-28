from flask import Blueprint
get_api_blueprint = Blueprint('get_api_blueprint',__name__)
@get_api_blueprint.route('/getapitest',methods=['GET'])
def get_test():
    """
    :return: get message
    """
    return "this is get test api"