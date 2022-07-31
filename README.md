# bank

use this examples on your .env file
```
POSTGRES_HOST=market-db
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432

```

### Up all container using docker compose
```
make up-all
```

### Check api logs
```
make logs-api
```

### Run unit tests
```
make test
```

### Create superuser
```
make bash
python manage.py createsuperuser
```

### Get access token
```
curl --request POST \
  --url http://127.0.0.1:8000/api/token/ \
  --header 'Content-Type: application/json' \
  --data '{
	"username": "your-username",
	"password": "your-password"
}'
```

### Insert products
```
curl --request POST \
  --url http://127.0.0.1:8000/products/ \
  --header 'Authorization: Bearer <access token>>' \
  --header 'Content-Type: application/json' \
  --data '{
	"name": "Ração para cachorro",
	"price": "50.00",
	"minimum": 10,
	"amount_per_package": 2,
	"max_availability": 50000
}'
```

### Get products
```
curl --request GET \
  --url 'http://127.0.0.1:8000/products/?name=cach' \
  --header 'Authorization: Bearer <access token>'
  --header 'Content-Type: application/json'
```


### Insert products on user shopping cart
```
curl --request POST \
  --url http://127.0.0.1:8000/shopping_cart/ \
  --header 'Authorization: Bearer <access token>'
  --header 'Content-Type: application/json' \
  --data '{
	"product": 1,
	"quantity": 12
}'
```

### Update shopping cart product
```
curl --request PATCH \
  --url http://127.0.0.1:8000/shopping_cart/1/ \
  --header 'Authorization: Bearer <access token>'
  --header 'Content-Type: application/json' \
  --data '{
	"quantity": 24
}'
```

### Get shopping cart products
```
curl --request GET \
  --url 'http://127.0.0.1:8000/shopping_cart/' \
  --header 'Authorization: Bearer <access token>'
  --header 'Content-Type: application/json'
```

### Deleting shopping cart product
```
curl --request DELETE \
  --url http://127.0.0.1:8000/shopping_cart/1/ \
  --header 'Authorization: Bearer <access token>'
  --header 'Content-Type: application/json'
```


### Checkout shopping products
```
curl --request POST \
  --url http://127.0.0.1:8000/checkout/ \
  --header 'Authorization: Bearer <access token>'
  --header 'Content-Type: application/json'
```


### Access Django admin address on your browser
```
    http://127.0.0.1:8000/admin/
```

### Access api documentation on your browser
```
    http://127.0.0.1:8000/admin/
```

### Access api documentation on your browser
```
    http://127.0.0.1:8000/docs/
    or
    http://127.0.0.1:8000/redoc/
```
