# Scissor

<a name="readme-top"></a>

  ### Table of Contents
  <ul>
    <li><a href="#live-app-version">Live App Version</a></li>
    <li><a href="#about">About</a></li>
    <li><a href="#technologies-used">Technologies used</a></li>
    <li><a href="#libraries-used">Libraries used</a></li>    
    <li><a href="#to-run-on-your-local-machine">To run on your local machine</a></li>
    <li><a href="#contact">Contact</a></li>
    <li>
      <a href="#endpoints">Endpoints</a>
      <ol>
        <li><a href="#auth-endpoints">Authorization Endpoints</a></li>
        <li><a href="#url-endpoints">URL Endpoints</a></li>
        <li><a href="#user-endpoints">User Endpoints</a></li>
      </ol>
    </li>
  </ul>
 
### Live app version
.....
#### Super administrator auth details on live app
.......
 <p align="right"><a href="#readme-top">back to top</a></p>


### About
Brief is the new black, this is what inspires the team at Scissor. In today's world, it's important to keep things as short as possible, and this applies to more concepts than you may realize. From music, speeches, to wedding receptions, brief is the new black. Scissor is a simple tool which makes URLs as short as possible. Scissor thinks it can disrupt the URL shortening industry.
#### Implementations:
1.  URL Shortening
2.  Custom URLs
3.  QR Code Generation
4.  Analytics
5.  Link History
<p align="right"><a href="#readme-top">back to top</a></p>


### Technologies Used
- Python
- Flask
 <p align="right"><a href="#readme-top">back to top</a></p>


### Libraries Used
- [Flask restx](https://flask-restx.readthedocs.io/en/latest/) - framework for creating REST api
- [Flask migrate](https://flask-migrate.readthedocs.io/) - framework for tracking database modifications
- [Flask SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) - object relational mapper
- [Flask JWT extended](https://flask-jwt-extended.readthedocs.io/en/stable/) - authentication and authorization
- [Flask Mail](https://pythonhosted.org/Flask-Mail/) - sending emails
<p align="right"><a href="#readme-top">back to top</a></p>


## To run on your local machine
### To run the development environment on your local machine
.....
 <p align="right"><a href="#readme-top">back to top</a></p>

### To run the Test environment on your local machine
....
 <p align="right"><a href="#readme-top">back to top</a></p>

## Contact
Promise - promiseanuoluwa@gmail.com
 <p align="right"><a href="#readme-top">back to top</a></p>


## Endpoints

### Auth Endpoints
| ROUTE | METHOD | DESCRIPTION | AUTHORIZATION  | USER TYPE |  
| ------- | ----- | ------------ | ------|------- |
|  `/auth/signup` | _POST_ | To create an account   | ---- | Any | 
|  `/auth/login` |  _POST_  | To authenticate users   | ---- | Any | 
|  `/auth/refresh` |  _POST_  | Generate refresh token  | Authenticated | Any | 
|  `/auth/logout` |  _DELETE_  | Logout user and revoke JWT access token | Authenticated | Any | 
 <p align="right"><a href="#readme-top">back to top</a></p>


### URL Endpoints
| ROUTE | METHOD | DESCRIPTION | AUTHORIZATION  | USER TYPE |  VARIABLE RULE | 
| ------- | ----- | ------------ | ------|------- | ----- |
|  `/url` |  _POST_  | Shorten a URL  | Authenticated | Any | ---- |
|  `/url/<url_key>/qrcode` |  _POST_  | Generate qrcode for a shortened URL   | Authenticated | Any | URL key |
|  `/url/<url_key>` |  _GET_  | Redirect a short URL to target URL   | ---- | Any | URL key |
|  `/url/<url_key>` |  _DELETE_  | Delete a shortened URL   | Authenticated | Any | URL key |
 <p align="right"><a href="#readme-top">back to top</a></p>


### User Endpoints
| ROUTE | METHOD | DESCRIPTION | AUTHORIZATION  | USER TYPE |  PLACEHOLDER | 
| ------- | ----- | ------------ | ------|------- | ----- |
|  `/user` |  _GET_  | Retrieve all users  | Authenticated | Admin | ---- |
|  `/user/<user_id>` |  _GET_  | Retrieve user by unique identifier | Authenticated | Admin | User ID |
|  `/user/<user_id>` |  _DELETE_  | Delete a user by unique identifier | Authenticated | Admin | User ID |
|  `/user/<user_id>/<token>` |  _PUT_  | User password reset | ---- | Any | User ID, Token |
|  `/user/confirm/<token>` |  _PATCH_  | Confirm email  | ---- | Any | Token |
|  `/user/reset_password_request` |  _POST_  | Password Reset Email Request  | ---- | Any | ---- |
|  `/user/<user_id>/paid` |  _PATCH_  | Give user paid privileges  | Authenticated | Admin | User ID |
|  `/user/<user_id>/paid_remove` |  _PATCH_  | Revoke user paid privileges  | Authenticated | Admin | User ID |
|  `/user/<user_id>` |  _PATCH_  | Give or Revoke admin privileges  | Authenticated | Super-Admin | User ID |
 <p align="right"><a href="#readme-top">back to top</a></p>

