# Backend Services
### Introduction
This backend service serves as the DowellMail applications.
### DowellMail Service features
- Settings to send email
- Send email 
- Subscribe to newletters
- Unsubscribe to newsletter
- Signup otp verification
- feedback survey mail
- Signup feedback mail
- Send SMS
- Send Editor email
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
|POST|/api/feedback-survey/|To send feedback-survey|
|POST|/api/signup-feedback/|To send sign up feedback mail|
|POST|/api/sms/|To send sms|
|POST|/api/editor-component/| To send mail from editor|
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
    "topic" : "<Your Topic>",
    "apiKey": "<API Key>"
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
    "topic":"<given while mail setting>",
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
#### Send feedback Survey
_POST_ to `/api/feedback-survey/`

Request Body
```json
{   
    "toEmail":"<Reciever Email>",
    "toName":"<Reciever Name>",
    "topic":"<given while mail setting>",
    "qr_code_src":"<Qr code src>",
    "data_survey_id":"<data_survey_id>",
    "survey_title": "<survey_title>",
    "user_name": "<user_name>"
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
#### Signup feedback email
_POST_ to `/api/signup-feedback/`

Request Body
```json
{   

    "topic" : "Signupfeedback",
    "toEmail":"<Reciever Email>",
    "toName":"<Reciever Name>",
    "firstname" : "<Firstname>",
    "lastname" : "<lastname>",
    "username" : "<username>",
    "phoneCode" : "<code>",
    "phoneNumber" : "<Phone number>",
    "usertype" : "<usertype>",
    "country" : "<country>",
    "verified_phone": "<message>",
    "verified_email": "<message>",

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
#### Send Newsletters 
_POST_ to `/api/send-newsletter/`

Request Body
```json
{
    "toEmail": [
        {
            "email": "jimmy98@example.com",
            "name": "Jimmy"
        },
        {
            "email": "jimmy98@example.com",
            "name": "Jimmy"
        }
    ],
    "topic":"<topic name you have register>"
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
#### Send SMS
_POST_ to `/api/sms/`

Request Body
```json
{
    "sender" : "<sender>",
    "recipient" : "<mobile number with country code>",
    "content" : "<Message>",
    "created_by" : "Manish"
}
```
Response-200
```json
{
    "INFO":"SMS has been sent!!",
    "INFO":"Response from the SendinBlue API"
}
```
Response-400
```json
{
    "error":"Exception when calling SMTPApi->send_transac_email"
}
```
#### Send Editor Mail
_POST_ to `/api/editor-component/`

Request Body
```json
{
    "topic" : "EditorMailComponent",
    "toEmail":"<Reciever Email>",
    "toName":"<Reciever Name>",
    "fromName":"<Sender name>",
    "fromEmail" : "<Sender email>",
    "subject" : "<subject>",
    "email_body" : "<email body>"
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

