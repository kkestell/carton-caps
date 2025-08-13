# Carton Caps

## Documentation

* **[Deferred Deep Linking](docs/deferred-deep-linking.md)**
  
  Written overview and sequence diagram of the full deferred deep linking workflow, and notes on preventing abuse.


* **[API Documentation](docs/api.md)**
 
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

<small>A number of users are created automatically for testing. See "Initialize the database" below for the full listing.</small>

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

Tell Quart where to find the app:

```console
$ export QUART_APP=src.carton_caps.app:create_app
```

Initialize the database:

```console
$ quart init-db
id | name                | referral_code | referrals
----------------------------------------------------
1  | Fox Mulder          | TRUSTNO1      | 4
2  | Dana Scully         | SCULLYMD      | 0
3  | Walter Skinner      | SKINNERAD     | 2
4  | C.G.B. Spender      | CANCERMAN     | 1
5  | The Flukeman        | FLUKEMAN      | 0
6  | Eugene Victor Tooms | LIVERLVR      | 0
7  | The Great Mutato    | CHERFAN       | 0
8  | Leonard Betts       | REGENERATE    | 0
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
