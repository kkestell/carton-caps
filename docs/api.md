# API Reference

## Get User Referrals (`GET /users/:user_id/referrals`)

Retrieves a list of referrals for a user.

### Example Request

```console
$ curl -X GET \
  -H "Authorization: Bearer <TOKEN>" \
  http://127.0.0.1:5000/users/1/referrals
```

### Route Parameters

| Parameter | Type     | Description                        |
|:----------|:---------|:-----------------------------------|
| `user_id` | `int`    | The unique identifier of the user. |

### Authentication

This endpoint requires authentication. You must provide an `Authorization` header that includes a valid OAuth 2.0 Bearer Token. Unauthenticated requests will receive a `401 Unauthorized` response.

#### Token Claims & Authorization

The provided Bearer Token must be valid and contain a `sub` claim that matches the `:user_id` in the request URL. In other words, a user can only view their own referrals.

### Success Response (`200 OK`)

The response body contains a JSON-encoded array of referral objects, or an empty array if the user has not made any referrals. 

Each referral object in the array contains the following fields:

| Field        | Type     | Description                                              |
|:-------------|:---------|:---------------------------------------------------------|
| `id`         | `int`    | The unique identifier for the referral.                  |
| `user`       | `user`   | The referred user.                                       |
| `status`     | `string` | The status of the referral (`pending` or `complete`).    |
| `created_at` | `string` | The ISO 8601 timestamp of when the referral was created. |

Each user object contains the following fields:

| Field        | Type     | Description                                   |
|:-------------|:---------|:----------------------------------------------|
| `id`         | `int`    | The unique identifier of the referred user.   |
| `name`       | `string` | The name of the user who was referred.        |
| `avatar_url` | `string` | The URL for the referred user's avatar image. |

#### Example Response

```json
[
    {
        "id": 5,
        "user": {
            "id": 6,
            "name": "Eugene Victor Tooms",
            "avatar_url": "https://place-hold.it/64x64"
        },
        "status": "complete",
        "created_at": "2025-08-10T20:03:00.123456"
    },
    {
        "id": 6,
        "user": {
            "id": 7,
            "name": "The Great Mutato",
            "avatar_url": "https://place-hold.it/64x64"
        },
        "status": "pending",
        "created_at": "2025-08-10T20:03:00.123456"
    }
]
```

### Error Responses

#### `403 Forbidden`

The API returns a `403 Forbidden` status when the `sub` claim in the Bearer Token does not match the `:user_id` in the request URL.

##### Example Response

```json
{
    "error": "You do not have permission to access this resource."
}
```

#### `404 Not Found`

The API returns a `404 Not Found` status when the user specified by `:user_id` does not exist.

##### Example Response

```json
{
    "error": "User with ID 1222 not found"
}
```

#### `500 Internal Server Error`

The API returns a `500 Internal Server Error` when an unexpected error occurs.

##### Example Response

```json
{
    "error": "Internal server error"
}
```
