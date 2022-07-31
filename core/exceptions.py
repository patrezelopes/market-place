from rest_framework.exceptions import APIException


class ProductError(APIException):
    status_code = 400
    default_detail = "Product request fail"
    default_code = "product_request_fail"


class ProductWrongField(APIException):
    status_code = 400
    default_detail = "Product wrong field"
    default_code = "product_wrong_field"


class ProductQuantity(APIException):
    status_code = 400
    default_detail = "Product quantity less than minimum"
    default_code = "product_less_than_minimum"


class ProductPackageIntegrity(APIException):
    status_code = 400
    default_detail = "Product package could not be split"
    default_code = "product_package_split_error"


class ProductDoesNotExist(APIException):
    status_code = 400
    default_detail = "Product requested does not exist"
    default_code = "product_does_not_exist"


class ProductQuantityExceeded(APIException):
    status_code = 400
    default_detail = "Product quantity exceed"
    default_code = "product_quantity_exceed"
