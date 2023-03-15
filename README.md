# Backend Services
### Introduction
This backend service serves as the DowellMail applications.
### DowellMail Service features
- Settings to send email
- Send email 
- Subscribe to newletters
- Unsubscribe to newsletter
### API Endpoints 
- Base URL : `https://100085.pythonanywhere.com/`

|HTTP Verbs| Endpoints| Action|
|------------|--------------------------------|------------------------------------------------------|
| GET | / | To check the server status |
| POST | /api/ mail-setting/ | To set the required details to send email|
| POST | /api/ send-mail/| To send mail using dowell mail API  |
| POST|/api/subscribe-newsletter/| To subscribe to newsletter|
|PUT|/api/subscribe-newsletter/| To unsubscribe to newsletter|
|POST|/api/signUp-otp-verification/|To send verification OTP|

### Endpoints Definition(Request - Response)
#### Server status
[Click here to check server status](https://100085.pythonanywhere.com/)

#### Settings to send email
_POST_ to `/api/mail-setting/`

Request Body 

```json
{
    "key" : "<YOUR_API_KEY>",
    "fromAddress" : "<Sender Email>",
    "fromName" : "<sender Name>",
    "templateName" : "<Template Name>",
    "subject" : "<Your subject>",
    "topic" : "<Your Topic>"
}
```
Response-201
```json
{
    "INFO":"Setting has been inserted!!"
}
```
Response-400
```json
{
    "INFO":"Something went wrong!!"
}
```
#### Send email
_POST_ to `/api/send-mail/`

Request Body 

```json
{
    "toEmail":"<Reciever Email>",
    "toName":"<Reciever Name>",
    "topic":"<Your Topic>"
}

```
Response-200
```json
{
    "INFO":"Mail has been sent!!",
    "INFO":"Response from the SendinBlue API"
}
```
Response-400
```json
{
    "error":"Exception when calling SMTPApi->send_transac_email"
}
```
#### Newsletter subscrtiptions
- _POST_ to `/api/subscribe-newsletter/`

    Request Body
    ```json
    {
        "topic":"<topic of newsletter>",
        "subscriberEmail":"<Subscriber Email>",
        "subscriberStatus":"<Subscriber Status>",
        "typeOfSubscriber":"<Public|Exsiting Client|Internal team|Prespetive Client|Sales agent>"
    }
    ```
    Response-200
    ```json
    {
        "INFO": "{typeOfSubscriber} has subscribed",
        "DATABASE_INFO":"<Response from database>"
    }
    ```
    Response-400
    ```json
    {
        "INFO":"Something went wrong!!"
    }
    ```
- _PUT_ to `/api/subscribe-newsletter/`

    Request Body
    ```json
    {
    "topic":"<Newsletter topic>",
    "subscriberEmail":"<Subscriber Email>"
    }
    ```
    Response-202
    ```json
    {
        "INFO":"User has unsubscribed" , 
        "DATABASE_INFO":"<Response from database>"
    }
    ```
    Response-406
    ```json
    {
        "INFO":"Already an unsubscribed!"
    }
    ```
#### Send Verification OTP in mail
_POST_ to `/api/signUp-otp-verification/`

Request Body
```json
{
    "toEmail":"<Reciever Email>",
    "toName":"<Reciever Name>",
    "topic":"OTPVerification",
    "otp":"<OTP>"
}
```
Response-200
```json
{
    "INFO":"Mail has been sent!!",
    "INFO":"Response from the SendinBlue API"
}
```
Response-400
```json
{
    "error":"Exception when calling SMTPApi->send_transac_email"
}
```
### Technologies Used

- Python is a programming language that lets you work more quickly and integrate your systems more effectively.
- Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.
- Django Rest Framework Django REST framework is a powerful and flexible toolkit for building Web APIs.
- MongoDB is a free open source NOSQL document database with scalability and flexibility. Data are stored in flexible JSON-like documents.
- SendinBlue mail servies , which helps to send email using their API.
### License
This project is available for use under [License](https://github.com/LL05-AI-Dowell/100085-dowellmailapi/blob/main/LICENSE).
