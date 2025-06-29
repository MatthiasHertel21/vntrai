from app import create_app
from flask import send_from_directory
import os

app = create_app()

@app.route('/data/<path:filename>')
def serve_data(filename):
    data_dir = os.path.abspath(os.path.join(app.root_path, '..', 'data'))
    return send_from_directory(data_dir, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
