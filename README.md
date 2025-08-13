# Carton Caps

## Documentation

* **[Deferred Deep Linking](docs/deferred-deep-linking.md)**
  
  An overview of the full deferred deep linking workflow and notes on preventing abuse.


* **[API Documentation](docs/deferred-deep-linking.md)**
 
  API documentation for frontend and backend developers for the new Carton Caps referral feature.


* **[Architecture](docs/architecture.md)**
 
  Architectural overview of the included mock-API.

## Quick Start 

### Docker

Build the container:

```console
$ docker build -t carton-caps .
```

Run the server:

```console
$ docker run -p 5000:5000 carton-caps
```

Make a request:

```console
$ curl http://127.0.0.1:5000/users/1/referrals
```

### Local Development

Create and activate a virtual environment:

```console
$ python -m venv .venv
$ source .venv/bin/activate
```

Install dependencies:

```console
$ pip install -r requirements.txt
$ pip install -e .
```

Tell Quart where to find the app.

```console
$ export QUART_APP=src.carton_caps.app:create_app
```

Initialize the database:

```console
$ quart init-db
```

Run the API:

```console
$ quart run
```

Make a request:

```console
$ curl http://127.0.0.1:5000/users/1/referrals
```

Run the tests:

```console
$ pytest
```
