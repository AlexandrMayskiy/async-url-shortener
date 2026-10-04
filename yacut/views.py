import asyncio
from http import HTTPStatus
from urllib.parse import urljoin

import aiohttp
from flask import (
    current_app, flash, redirect, render_template, request
)
from werkzeug.utils import secure_filename
from wtforms import ValidationError

from . import app
from .constants import DEFAULT_API_URL
from .forms import FileUploadForm, URLMapForm
from .models import URLMap


async def upload_single_file(session, token, file_storage, base_url):
    """Асинхронно загружает один файл на Яндекс Диск."""
    headers = {'Authorization': f'OAuth {token}'}
    filename = secure_filename(file_storage.filename)
    if not filename:
        return None

    api_url = urljoin(base_url, 'v1/disk/resources/upload')
    disk_path = f'app:/{filename}'
    params = {'path': disk_path, 'overwrite': 'true'}

    try:
        async with session.get(
            api_url, headers=headers, params=params
        ) as resp:
            if resp.status != HTTPStatus.OK:
                return None
            data = await resp.json()
            upload_url = data.get('href')

        if hasattr(file_storage, 'seek'):
            file_storage.seek(0)
        elif (hasattr(file_storage, 'stream') and
              hasattr(file_storage.stream, 'seek')):
            file_storage.stream.seek(0)

        file_data = file_storage.read()
        async with session.put(upload_url, data=file_data) as put_resp:
            if put_resp.status not in (HTTPStatus.OK, HTTPStatus.CREATED):
                return None

        download_url = urljoin(base_url, 'v1/disk/resources/download')
        async with session.get(
            download_url,
            headers=headers,
            params={'path': disk_path}
        ) as down_resp:
            if down_resp.status not in (HTTPStatus.OK, HTTPStatus.CREATED):
                return None
            meta_data = await down_resp.json()
            return meta_data.get('href') or meta_data.get('public_url')

    except aiohttp.ClientError:
        return None


async def upload_files_to_disk_async(token, files, base_url):
    """Параллельно запускает загрузку списка файлов на Яндекс Диск."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            upload_single_file(session, token, f, base_url)
            for f in files if f.filename
        ]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница: сокращение длинных ссылок."""
    form = URLMapForm()
    if form.validate_on_submit():
        try:
            url_map = URLMap.create(
                original=form.original_link.data,
                custom_id=form.custom_id.data,
                is_api=False
            )
            return render_template(
                'index.html',
                form=form,
                short_url=url_map.to_dict()['short_link']
            )
        except ValidationError as error:
            flash(str(error), 'danger')

    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
def upload_view():
    """Загрузка файлов на Яндекс Диск и создание коротких ссылок."""
    form = FileUploadForm()

    if request.method == 'POST':
        token = current_app.config.get('DISK_TOKEN')
        base_url = current_app.config.get(
            'YADISK_API_BASE_URL',
            DEFAULT_API_URL
        )

        if not token:
            flash(
                'Ошибка конфигурации: отсутствует токен Яндекс Диска.',
                'danger'
            )
            return render_template('upload.html', form=form)

        uploaded_files_list = request.files.getlist('files')

        if (not uploaded_files_list or
                len(uploaded_files_list) == 0 or
                not uploaded_files_list[0].filename):
            flash('Выберите хотя бы один файл', 'danger')
            return render_template('upload.html', form=form)

        original_filenames = [
            f.filename for f in uploaded_files_list if f.filename
        ]

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            long_links = loop.run_until_complete(
                upload_files_to_disk_async(
                    token,
                    uploaded_files_list,
                    base_url
                )
            )
        finally:
            loop.close()

        if not long_links:
            flash('Не удалось загрузить ни одного файла на Диск.', 'danger')
            return render_template('upload.html', form=form)

        short_urls = []
        for filename, long_link in zip(original_filenames, long_links):
            url_map = URLMap.create(original=long_link, is_api=False)
            short_urls.append({
                'name': filename,
                'url': url_map.to_dict()['short_link']
            })

        flash('Файлы успешно загружены и сокращены!', 'success')
        return render_template(
            'upload.html',
            form=form,
            short_urls=short_urls
        )

    return render_template('upload.html', form=form)


@app.route('/<short_id>', methods=['GET'])
def redirect_view(short_id):
    """Перенаправление с короткого ID на оригинальный URL."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
