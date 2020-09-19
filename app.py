from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import boto3
import os
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

UPLOAD_DIRECTORY = "/tmp"
ALLOWED_EXTENSIONS = {'pdf'}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_companies', methods=['GET'])
def get_companies():
    return jsonify({'result': ['bytedance', 'grab']})


@app.route('/ask_refer/bytedance', methods=['POST'])
def ask_refer_bytedance():
    # request.args.to_dict() get parameters
    # records = request.data
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No selected file'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            app.logger.info('load file {}'.format(filename))
            filepath = os.path.join(UPLOAD_DIRECTORY, filename)
            file.save(filepath)
            app.logger.info('file saved to {}'.format(filepath))
            upload2s3(filepath, 'bytedance')
            return 'Your request for bytedance referral has been successfully processed. ' \
                   'We will get back to you through email in 48 hours'
        else:
            return jsonify({'error': 'File format wrong, allowed formats are {}'.format(ALLOWED_EXTENSIONS)})


@app.route('/ask_refer/grab', methods=['POST'])
def ask_refer_grab():
    # request.args.to_dict() get parameters
    # records = request.data
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No selected file'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            app.logger.info('load file {}'.format(filename))
            filepath = os.path.join(UPLOAD_DIRECTORY, filename)
            file.save(filepath)
            app.logger.info('file saved to {}'.format(filepath))
            upload2s3(filepath, 'grab')
            return 'Your request for grab referral has been successfully processed. ' \
                   'We will get back to you through email in 48 hours'
        else:
            return jsonify({'error': 'File format wrong, allowed formats are {}'.format(ALLOWED_EXTENSIONS)})


def upload2s3(filepath, company):
    bucket = 'zappa-referral-api-eu2hzy8sf'
    date_utc = datetime.utcfromtimestamp(int(time.time()))
    appendix = str(date_utc.hour).zfill(2) + str(date_utc.minute).zfill(2) + str(date_utc.second).zfill(2)
    key = 'referral/' + company + '/{}/{}/{}/'.format(date_utc.year,
                                                      str(date_utc.month).zfill(2),
                                                      str(date_utc.day).zfill(2)) + 'candidate_' + appendix
    app.logger.info('s3 saved file key {}'.format(key))
    s3 = boto3.client('s3')
    with open(filepath, "rb") as f:
        s3.upload_fileobj(f, bucket, key)


def valid_input(records):
    keys = records.keys()
    if 'name' not in keys:
        return jsonify({'input_error': 'Please input your name!'})
    if 'email' not in keys:
        return jsonify({'input_error': 'Please input your email!'})
    if 'file' not in keys:
        return jsonify({'input_error': 'Please input upload your file of resume!'})
    return 1


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def remove_file(filepath):
    os.remove(filepath)
    app.logger.info('removed file {}'.format(filepath))
