
template_for_email_verification = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email Verification</title>
            <style>
                body { font-family: Arial, sans-serif; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; }
                .header { font-size: 24px; font-weight: bold; }
                .code { font-size: 32px; font-weight: bold; color: #4CAF50; }
                .footer { margin-top: 20px; font-size: 12px; color: #888; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">Email Verification</div>
                <p>Hi {{ first_name }},</p>
                <p>Thank you for registering with Teachers Assistant App. Please use the verification code below to verify your email address:</p>
                <p class="code">{{ verification_code }}</p>
                <p>If you did not register an account with us, please ignore this email or contact support if you have any questions.</p>
                <p>Sincerely yours,</p>
                <p>The Teachers Assistant App team</p>
                <div class="footer">
                    <p>This email can't receive replies. For more information, visit the Teachers Assistant Help Centre.</p>
                    <p>© Teachers Assistant App, Afedo Street, Ho Bankoe, Ghana</p>
                </div>
            </div>
        </body>
        </html>
        """

template_for_password_reset = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Password Reset Request</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; }
                    .header { font-size: 24px; font-weight: bold; }
                    .code { font-size: 32px; font-weight: bold; color: #4CAF50; }
                    .footer { margin-top: 20px; font-size: 12px; color: #888; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">Password Reset Request</div>
                    <p>Hi {{ first_name }},</p>
                    <p>We received a request to access your Teachers Assistant App account {{ email }} through your email address. Your verification code is:</p>
                    <p class="code">{{ reset_code }}</p>
                    <p>If you did not request this code, it is possible that someone else is trying to access the Teachers Assistant App account {{ email }}. Do not forward or give this code to anyone.</p>
                    <p>Sincerely yours,</p>
                    <p>The Teachers Assistant App team</p>
                    <div class="footer">
                        <p>This email can't receive replies. For more information, visit the Teachers Assistant Help Centre.</p>
                        <p>© Teachers Assistant App, Afedo Street, Ho Bankoe, Ghana</p>
                    </div>
                </div>
            </body>
            </html>
            """
