import boto3
from flask import Flask, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'some-secret-key'

# Load values from .env
PASSWORD = os.getenv('PASSWORD')
BUCKET_NAME = os.getenv('BUCKET_NAME')
OBJECT_KEY = os.getenv('OBJECT_KEY')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('show_map'))
        else:
            error = '<p style="color:red;">Wrong password!</p>'

    return f'''
        <html>
        <head>
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background: #f3f4f6;
                    font-family: Arial, sans-serif;
                }}
                .login-container {{
                    background: white;
                    padding: 2rem 2.5rem;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    width: 100%;
                    max-width: 400px;
                }}
                input[type="password"] {{
                    padding: 0.5rem;
                    width: 80%;
                    margin: 0.5rem 0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }}
                input[type="submit"] {{
                    padding: 0.5rem 1rem;
                    border: none;
                    background-color: #2563eb;
                    color: white;
                    font-weight: bold;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                input[type="submit"]:hover {{
                    background-color: #1d4ed8;
                }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <h2>Enter password to view map:</h2>
                {error}
                <form method="post">
                    <input type="password" name="password" placeholder="Password" required/>
                    <br/>
                    <input type="submit" value="Login"/>
                </form>
            </div>
        </body>
        </html>
    '''


@app.route('/map')
def show_map():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    # Pass credentials directly to boto3.client
    s3 = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': OBJECT_KEY},
        ExpiresIn=600  # 10 minutes
    )
    return redirect(presigned_url)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port='5000')
