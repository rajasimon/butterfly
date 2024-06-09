# Butterfly

An API for the Social Network

## Assignment 

    https://drive.google.com/file/d/1zjNqjpcvJG843RnJk9Y_CqPLb5tVBuL1/view

## Docker 

    docker compose up

    # Note: Run migrations command to populate tables into the db.
    docker compose run web python manage.py migrate


## Testing
    
There is a testcase for each API in the tests.py file. Can be able to run the tests
with this command. 

    docker compose run web python manage.py test


## Explanation

### Butterfly
All the API available for the social network. These API will make the complete list of API's that are available for the butterfly project. User can send a friend request and user can search a friend request.

*Authentication*
/register/ - User can able to register the user here with just an email address. This will return id along with passed email address.
/login/ - I have used token based authentication so passing the email will return a token that you can add into "services" collection authentication section. And that token will used to all the services API.

*Services*

/status/ - Do note that in a "friend" context the "owner" is the logged in user or the user first initiated the friend request and the "profile" is the one owner send the friend request to.
For the post method you can send a "SEND" request but use the patch methoed to update the status from SEND to ACCEPT or REJECT.
/friends/ - List API to list all the friends who are accepted
/pending/ - User can see all the pending requests.
/search/ - Search all the users in the database.


