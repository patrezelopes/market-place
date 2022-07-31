from core.exceptions import ProductPackageIntegrity, ProductQuantityExceeded


def valid_quantity(product_inserted):
    if product_inserted.quantity > product_inserted.product.max_availability:
        raise ProductQuantityExceeded
    if not product_inserted.package_integrity:
        raise ProductPackageIntegrity
    return True
