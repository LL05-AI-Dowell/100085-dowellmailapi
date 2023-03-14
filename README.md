# Backend Services
### Introduction
This backend service serves as the DowellMail applications.
### DowellMail Service features
- Settings to send email
- Send email 
### API Endpoints 
- Base URL : `https://100085.pythonanywhere.com/`

|HTTP Verbs| Endpoints| Action|
|------------|--------------------------------|------------------------------------------------------|
| GET | / | To check the server status |
| POST | /api/ mail-setting/ | To set the required details to send email|
| POST | /api/ send-mail/| To send mail using dowell mail API  |

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

### Technologies Used

- Python is a programming language that lets you work more quickly and integrate your systems more effectively.
- Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.
- Django Rest Framework Django REST framework is a powerful and flexible toolkit for building Web APIs.
- MongoDB is a free open source NOSQL document database with scalability and flexibility. Data are stored in flexible JSON-like documents.
- SendinBlue mail servies , which helps to send email using their API.
### License
This project is available for use under [License](https://github.com/LL05-AI-Dowell/100085-dowellmailapi/blob/main/LICENSE).