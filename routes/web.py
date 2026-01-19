from masonite.routes import Route

ROUTES = [
    Route.get("/", "WelcomeController@show"),
    Route.get('/db-test', 'DBTestController@test')
    ]
