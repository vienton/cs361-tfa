from flask import Flask, request, render_template
import tfa, encrypted
import json

# Instantiate Flask app
app = Flask(__name__)

bad_method_error = {'Error': 'Only HTTP GET method is allowed.'}
bad_headers_error = {'Error': 'Please specify application/json in Accept headers field.'}
cannot_retrieve_error = {'Error': 'Cannot retrieve articles from Wikipedia'}

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        # Get articles from Wikipedia, then reverse order to get newest pub date first
        try:
            articles = tfa.get_articles()[::-1]
        except:
            return render_template('503.html'), 503

        # Get first article from list
        art = articles[0]

        # 'Encrypt' the title with Chan Seung's API; If API not up, reverse title
        try:
            encrypted_title = encrypted.get_encrypted(art.title)
        except:
            encrypted_title = art.title[::-1]

        context = {
            "img_alt": art.img_alt,
            "img_hotlink": art.img_hotlink,
            "img_hotlink_full": art.img_hotlink_full,
            "img_url": art.img_url,
            "title": art.title,
            "date": art.date,
            "text": art.text,
            "url": art.url,
            "encrypted_title": encrypted_title
        }

        return render_template('index.html', **context)
    else:
        return bad_method_error, 405

@app.route('/articles', methods=['GET'])
def articles():
    if request.method == 'GET':
        # Get articles from Wikipedia, then reverse order to get newest pub date first
        try:
            articles = tfa.get_articles()[::-1]
        except:
            return render_template('503.html')

        # Iterate through articles and add new properties
        modal_id = 0
        for art in articles:
            modal_id = modal_id + 1
            art.img_modal_id = 'img_modal_' + str(modal_id)
            try:
                art.encrypted_title = encrypted.get_encrypted(art.title)
            except:
                art.encrypted_title = art.title[::-1]

        return render_template('articles.html', title='Previous Articles', articles=articles[1:])
    else:
        return bad_method_error, 405

@app.route('/api', methods=['GET'])
def api():
    if request.method == 'GET':
        return render_template('api.html', title='API Reference')
    else:
        return bad_method_error, 405

@app.route('/api/article', methods=['GET'])
def api_get_article():
    if request.method == 'GET':
        try:
            # Get articles from Wikipedia, then reverse order to get newest pub date first
            articles = tfa.get_articles()[::-1]
        except:
            return cannot_retrieve_error, 503

        if 'application/json' in request.accept_mimetypes:
            # Get first article from list
            art = articles[0]
            response = json.dumps(art.__dict__)
            return response
        else:
            return bad_headers_error, 406
    else:
        return bad_method_error, 405

@app.route('/api/articles', methods=['GET'])
def api_get_articles():
    if request.method == 'GET':
        # Get articles from Wikipedia, then reverse order to get newest pub date first
        try:
            articles = tfa.get_articles()[::-1]
        except:
            return cannot_retrieve_error, 503

        if 'application/json' in request.accept_mimetypes:
            response = []
            for art in articles:
                art_data = {}
                art_data['title'] = art.title
                art_data['date'] = art.date
                art_data['img_url'] = art.img_url
                art_data['img_hotlink'] = art.img_hotlink
                art_data['img_hotlink_full'] = art.img_hotlink_full
                art_data['img_alt'] = art.img_alt
                art_data['text'] = art.text
                art_data['url'] = art.url
                response.append(art_data)
            return json.dumps(response)
        else:
            return bad_headers_error, 406
    else:
        return bad_method_error, 405

# Launch app
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)