import os
import pandas as pd
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Папки для хранения файлов
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Функция обработки CSV
def process_csv(file_path):
    data = pd.read_csv(file_path, delimiter='\t', dtype=str)
    updated_columns = list(data.columns)

    for i in range(1, len(data.columns)):  # Начинаем со второго столбца
        date_col = data.columns[i]
        try:
            formatted_date = pd.to_datetime(date_col, format='%Y-%m-%d').strftime('%d.%m.%Y')
        except ValueError:
            formatted_date = date_col

        new_col_name = f"url_{formatted_date}"
        data[new_col_name] = ""
        updated_columns.insert(2 * i, new_col_name)

    data = data[updated_columns]
    output_file = file_path.replace(UPLOAD_FOLDER, PROCESSED_FOLDER).replace(".csv", "_processed.csv")
    data.to_csv(output_file, sep='\t', index=False)
    return output_file

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("files")
        processed_files = []

        for file in files:
            if file.filename.endswith(".csv"):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                processed_file = process_csv(file_path)
                processed_files.append(processed_file)

        return render_template("index.html", processed_files=processed_files)

    return render_template("index.html", processed_files=[])

@app.route("/download/<filename>")
def download_file(filename):
    return send_file(os.path.join(PROCESSED_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)