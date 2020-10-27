# Offline Messaging API

It is an API of a messaging service. It supports the following cases:
* The user can create an account and login to the system.
* Users can message each other as long as they know each other's username.
* Users can access their messaging history.
* One user can block another user if he/she does not want to receive messages. Messages of a blocked user are not forwarded.
* Users' activity (login, invalid login, sending messages, etc.) logs are kept in the database.
* Details of some critical errors are not sent to users, and all errors are recorded.
* Pagination is used in old messages.

## Installed Apps
This API contains several apps in it. It is defined in *settings.py*. These installed apps are: **'rest_framework', 'authentication', 'messaging', 'user_logging'**.
I used simple_jwt for authentication. You can check out the [documentation](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html)
for more information about simple jwt.


## End-points

end-points | Descriptions
--- | ---
api/authentication/register/ | A new user register the system.
api/authentication/login/ | A registered user login to the system with his/her credentials.
api/authentication/token/ | Returns to token and refresh-token of the user.
api/authentication/token/refresh/ | Refreshes the token of the user.
api/authentication/block-user/ | One user blocks the another one.
api/messaging/get-inbox/ | Get inbox of the user
api/messaging/get-outbox/ | Get send messages of the user
api/messaging/send/ | A user send message to another user
api-auth/ | It contains the rest-framework urls.
admin/ | Admin panel

## Optional challenges:
* The user who sends the message can see when the message was delivered and read.
* Date/person categorization can be done in retrospective messages.
* API usage can be provided with user interfaces in preferred client platforms and languages.
* Dependency Injection can be used.
