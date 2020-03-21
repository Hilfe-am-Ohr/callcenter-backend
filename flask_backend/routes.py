from flask_backend import app
from flask import render_template, request
import time


def get_params_dict(request):

    try:
        params_dict = request.get_json(force=True)
    except:
        params_dict = {}

    if not isinstance(params_dict, dict):
        params_dict = {}

    params_dict.update(dict(request.form))
    params_dict.update(dict(request.files))

    if "email" not in params_dict:
        params_dict["email"] = None

    if "api_key" not in params_dict:
        params_dict["api_key"] = None

    if "password" not in params_dict:
        params_dict["password"] = None

    params_dict["method"] = request.method

    query_string_list = request.query_string.decode().split("&")

    for query_string_element in query_string_list:

        element_list = query_string_element.split("=")

        if len(element_list) != 2:
            continue

        element_list[0] = element_list[0].strip()
        element_list[1] = element_list[1].strip()
        if len(element_list[0]) == 0 or len(element_list[1]) == 0:
            continue

        if "," in element_list[1]:
            element_list[1] = list(filter(lambda x: len(x) != 0, element_list[1].split(",")))

        params_dict[element_list[0]] = element_list[1]

    print("\n\n")
    # time.sleep(0.00001)
    print(params_dict)
    return params_dict


@app.errorhandler(404)
def page_not_found(e):
    # Every url not associated with the backend is directly
    # routed to the frontend (which will also handle 404's)

    return render_template("index.html")


@app.route("/robots.txt", methods=["GET"])
def robots():
    return render_template("robots.txt")


@app.route("/backend", methods=["GET"])
def index():
    return "<h1>Welcome to Flask!</h1>"


# Actually flask-cors should take care of this but somehow it doesn't always...
@app.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origi"] = "*"
    return response
