# falcon-swagger
Build a swagger documentation from a Falcon app

## how to use
```
from flacon_swagger import swagger, swaggerify

class TestResource(object):
    @swagger(summary='test')
    def on_get(self, req, resp):
        pass

app = API()
swaggerify(app, 'test-api', '2.0.0', host="localhost")
app.add_route('/test/', TestResource()
```

Then visit `http://localhost/swagger.json`
