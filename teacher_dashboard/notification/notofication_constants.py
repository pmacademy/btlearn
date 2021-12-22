from enum import Enum


class NotificationServiceTypesEnum(str, Enum):
    EMAIL = "email"


class EmailNoticationServiceConstants:
    TEAMPLATE_BODY = {
        "StudentAccountCreateEmail":
            """ 
Hi $student_first_name $student_last_name,

Your teacher, $teacher_name, has created an account for you on ByteLearn.ai ($bytelearn_sign_in_url).

Email: $student_email
Password: $student_password

If $student_email is a Google account, you can also sign in to ByteLearn with Google and don't need to use the password listed above.

Sign in to ByteLearn($bytelearn_sign_in_url).

Thank You,
The ByteLearn Team
            """,
        "StudentAlreadyExistsAddedToClass":
            """
Hi $student_first_name $student_last_name,

Your teacher, $teacher_name, has added you to their class on ByteLearn.ai($bytelearn_sign_in_url).

Email: $student_email

Sign in to ByteLearn($bytelearn_sign_in_url).

Thank You!
The ByteLearn Team
            """,
            "test": """test message""",
            "FogotPasswordEmail":"""
We just received a request to reset the password for your Bytelearn.ai account. If you didn’t request this, please ignore this email.
Reset Password Link:- $reset_password_link
If you have any questions, please contact us.            
            """
    }

    TEAMPLATE_HTML = {
        "StudentAccountCreateEmail":
            """
<!DOCTYPE html>
<html lang="en">
    <body>
        Hi $student_first_name $student_last_name, <br/>
        <br/>
        Your teacher, $teacher_name, has created an account for you on <a href='$bytelearn_sign_in_url'>ByteLearn.ai</a> . <br/>
        <br/>
        Email: $student_email <br/>
        Password: $student_password <br/>
        <br/>
        If $student_email is a Google account, you can also sign in to ByteLearn with Google and don't need to use the password listed above. <br/>
        <br/>
        Sign in to ByteLearn $bytelearn_sign_in_url. <br/>
        <br/>
        Thank You, <br/>
        The ByteLearn Team <br/>
    </body>
</html>
            """,
        "StudentAlreadyExistsAddedToClass":
            """
<!DOCTYPE html>
<html lang="en">
    <body>
        Hi $student_first_name $student_last_name, <br/>
        <br/>
        Your teacher, $teacher_name, has added you to their class on <a href="$bytelearn_sign_in_url">ByteLearn.ai</a>.<br/>
        <br/>
        Email: $student_email <br/>
        <br/>
        If $student_email is a Google account, you can also sign in to ByteLearn with Google and don't need to use the password listed above. <br/>
        <br/>
        Sign in to <a href="$bytelearn_sign_in_url">ByteLearn</a>. <br/>
        <br/>
        Thank You, <br/>
        The ByteLearn Team <br/>
    </body>
</html>
            """,
        "test": """
<!DOCTYPE html>
<html lang="en">
    <body>
        test message
    </body>
</html>

        """,
        "FogotPasswordEmail": """
<!DOCTYPE html>
<html lang=\"en\">
  <body>
    <div style=\"width: 100%; height: 400px; text-align: center\">
      <div style=\"position: relative; top: 50%; transform: translateY(-50%)\">
        <img
          style=\"margin-top: 25px; width: 88px; height: 88px\"
          src=\"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/285/locked-with-key_1f510.png\"
        />
        <h1>Reset password</h1>
        <h3 style=\"font-weight: 400\">
          We just received a request to reset the password for your Bytelearn.ai
          account. If you didn't request this, please ignore this email.
        </h3>
        <a href=\"$reset_password_link\" style=\"cursor: pointer; text-decoration: none\">
        <button
          style=\"
            width: 250px;
            height: 48px;
            border-radius: 24px;
            color: white;
            border: none;
            font-weight: 600;
            cursor: pointer;
            background-color: #377CF6;
          \"
        >
          Reset your password
        </button>
        </a>
        <h3 style=\"font-weight: 400\">
          If you have any questions, please
          <a
            style=\"color: #377CF6; cursor: pointer; text-decoration: none\"
            href=\"https://mail.google.com/mail/?view=cm&to=support@bytelearn.ai\"
            target=\"_self\">contact us.</a>
        </h3>
      </div>
    </div>
    <script>
      function resetPassword() {
        window.open(\"$reset_password_link\", \"_self\");
      }
    </script>
  </body>
</html>
        """

    }

    TEMPLATE_SUBJECT = {
        "StudentAccountCreateEmail": "Your teacher created a ByteLearn account for you",
        "StudentAlreadyExistsAddedToClass": "Your teacher added you to their class on ByteLearn",
        "test": "test header",
        "FogotPasswordEmail": "Password Reset Request for ByteLearn",
    }

    SOURCE_EMAIL_ADDRESS = {
        "StudentAccountCreateEmail": "noreply@bytelearn.ai",
        "StudentAlreadyExistsAddedToClass": "noreply@bytelearn.ai",
        "test": "noreply@bytelearn.ai",
        "FogotPasswordEmail": "noreply@bytelearn.ai",
    }

    BASE_TEMPLATE = {
        'Body': {
            'Text': {
                'Charset': 'UTF-8',
                'Data': None
            },
            'Html': {
                'Charset': 'UTF-8',
                'Data': None
            }
        },
        'Subject': {
            'Charset': 'UTF-8',
            'Data': None,
        }
    }


# class NotificationServiceTypes:
#     EMAIL = "email"

# class StudentAccountCreateEmailConstant:
#     TEAMPLATE_NAME = "StudentAccountCreateEmail"

#     class Fields:
#         class Body:
#             STUDENT_FIRST_NAME = "student_first_name"
#             STUDENT_LAST_NAME = "student_last_name"
#             TEACHER_NAME = "teacher_name"
#             BYETELEARN_SIGN_IN_URL = "bytelearn_sign_in_url"
#             STUDENT_EMAIL = "student_email"
#             STUDENT_PASSWORD = "student_password"

#         class Subject:
#             pass
