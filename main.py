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
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('show_map'))
        else:
            return '''
                <h2 style="color:red;">Wrong password!</h2>
                <form method="post"><input type="password" name="password"/><input type="submit"/></form>
            '''
    return '''
        <h2>Enter password to view map:</h2>
        <form method="post"><input type="password" name="password"/><input type="submit"/></form>
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
    app.run(debug=True)