from flask import Flask, request, send_file, jsonify, render_template, make_response, g
from Identifier import IDPool

AiServer = Flask(__name__)
user_id_pool = IDPool
session_id_pool= IDPool



@AiServer.before_request
def RequestPreHandler():
    pass


@AiServer.route('/say', methods=['POST'])
def say():
    pass


@AiServer.route('/chat', methods=['POST'])
def chat():
    pass


@AiServer.after_request
def after_request(response):
    pass
