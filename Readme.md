
# User registration and token generation endpoints 

ROLE = ANYONE

POST  1) http://127.0.0.1:8000/auth/users/       
GET   2) http://127.0.0.1:8000/auth/users/me/
POST  3) http://127.0.0.1:8000/auth/token/login

# User group management endpoints

1) ADMIN -  GET - Return all managers 
 http://127.0.0.1:8000/api/groups/manager/users

2) ADMIN -  POST - Assigns the user in the payload to the manager group and returns 201-Created

 http://127.0.0.1:8000/api/groups/manager/users

3) ADMIN get view all user - token required
    
    http://127.0.0.1:8000/auth/users/

4) ADMIN - POST - Removes this particular user from the manager group and returns 200 – Success if everything is okay.
                  If the user is not found, returns 404 – Not found

    /api/groups/manager/users/{userId}