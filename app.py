from flask import Flask, render_template, request
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from langdetect import detect, lang_detect_exception
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)

def is_hindi_translation_available(url):
    try:
        response = requests.get(url)
        html = response.text
        lang = detect(html)
        return lang == 'hi'
    except lang_detect_exception.LangDetectException:
        return False
    except requests.exceptions.RequestException:
        return False

def is_dropdowns_work(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        navbar = soup.select_one('nav.cmpt-nav')
        if navbar is None:
            return False
        navbar_button = navbar.select_one('button.navbar-toggler')
        if navbar_button is None:
            return False
        navbar_items = navbar.select('a.nav-link')
        for item in navbar_items:
            if item['href'] == '#' or item['href'] == '':
                return False
        return True
    except:
        return False

def is_image_high_quality(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        width, height = img.size
        dpi = img.info.get('dpi', (72, 72))
        if width >= 1024 and height >= 1024 and dpi[0] >= 300 and dpi[1] >= 300:
            return True
        else:
            return False
    except UnidentifiedImageError:
        return False
    except requests.exceptions.RequestException:
        return False

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result', methods=['POST'])
def result():
    results =[]
    urls = request.form.get('urls')
    url_list = urls.strip().split('\n')
    is_hindi = True
    is_high_quality = True
    is_dropdowns_work = True

    for url in url_list:
        try:
            is_hindi = is_hindi_translation_available(url)

            is_high_quality = is_image_high_quality(url)

            is_dropdowns_work = False

            results.append({
                'url': url,
                'is_hindi': is_hindi,
                'is_high_quality': is_high_quality,
                'is_dropdowns_work': is_dropdowns_work
            })
        except:
            pass

    return render_template('result.html', results=results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
