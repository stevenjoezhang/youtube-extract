from flask import Flask
from flask import render_template
from flask import request
import youtube_dl

ytoptions = {'quiet': 'opts.quiet',
             'no_warnings': 'opts.no_warnings',
             'format': 'bestvideo+bestaudio/best',
             'outtmpl': '%(title)s',
             'merge_output_format': 'mkv'}

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/extract")
def extract():
    url = request.args.get('url')
    with youtube_dl.YoutubeDL(ytoptions) as ydl:
        ie = ydl.get_info_extractor('Youtube')
        if not ie.suitable(url):
            return render_template('index.html', error='Unsupported URL', url=url)
        return render_template('index.html', results=ie.extract(url), human_readable_size=human_readable_size, url=url)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
