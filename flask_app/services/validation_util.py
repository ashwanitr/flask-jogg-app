
def validate(required_attributes):
    """
    Utility function to check validity of the given input.
    Just checks if all the required parameters exits. Throws appropriate error message otherwise.
    :param required_attributes:
    :return: None if input is valid and Error Otherwise
    """
    missing_attributes = []
    for name, attribute in required_attributes.items():
        if not attribute:
            missing_attributes.append(name)

    if missing_attributes:
        return error_message(f"some required attributes are missing : {missing_attributes}")


def success_message(message=None, data=None):
    """
    Utility function to properly format success response message
    :param message:
    :param data:
    :return: Success Response
    """
    return {"error": False, "message": message, "data": data, "exception": None}


def error_message(message=None, exception=None):
    """
    Utility function to properly format error response message
    :param message:
    :param exception:
    :return: Error Response
    """
    return {"error": True, "message": message, "data": None, "exception": exception}
