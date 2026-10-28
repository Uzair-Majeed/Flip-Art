"""Integration checks against the actual locally running Flask server and weights.
Start backend/run.py first, then run pytest backend/tests.
"""
import base64
import io
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flipart.services.image_detection import detect_image_type

BASE = 'http://127.0.0.1:5000'
SAMPLES = Path(__file__).resolve().parents[2] / 'frontend' / 'public' / 'samples'


def post(path, payload):
    req = Request(BASE + path, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=180) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def image_url(kind='photo'):
    data = (SAMPLES / f'{kind}.png').read_bytes()
    return 'data:image/png;base64,' + base64.b64encode(data).decode()


def test_health_and_react():
    with urlopen(BASE + '/health') as response:
        assert json.load(response)['models_loaded'] is True
    with urlopen(BASE) as response:
        page = response.read().decode()
        assert 'id="root"' in page and '/assets/' in page
        assert '<title>FlipArt' in page


@pytest.mark.parametrize('kind', ['photo', 'sketch'])
def test_bundled_samples(kind):
    with urlopen(BASE + f'/samples/{kind}.png') as response:
        assert response.headers.get_content_type() == 'image/png'
        assert response.read() == (SAMPLES / f'{kind}.png').read_bytes()


def test_detector():
    assert detect_image_type(Image.new('RGB', (128, 128), 'white'))['detected_type'] == 'sketch'
    assert detect_image_type(Image.new('RGB', (128, 128), 'red'))['detected_type'] == 'photo'


@pytest.mark.parametrize('kind,direction', [('photo', 'photo->sketch'), ('sketch', 'sketch->photo')])
def test_real_model_conversion(kind, direction):
    status, result = post('/api/convert', {'image': image_url(kind), 'mode': kind, 'face_crop': False})
    assert status == 200, result
    assert result['direction'] == direction
    for field in ('input_preview', 'output_image'):
        image = Image.open(io.BytesIO(base64.b64decode(result[field].split(',')[1])))
        assert image.size == (512, 512)
        assert image.mode == 'RGB'
    assert result['inference_ms'] >= 0
    if kind == 'photo':
        arr = np.asarray(image)
        np.testing.assert_array_equal(arr[:, :, 0], arr[:, :, 1])


def test_cleanup_only_for_sketch_and_detection_unchanged():
    for mode in ('photo', 'sketch', 'auto'):
        payload = {'image': image_url('sketch'), 'mode': mode}
        status, baseline = post('/api/preview', payload)
        assert status == 200
        status, cleaned = post('/api/preview', dict(payload, clean_sketch=True))
        assert status == 200
        assert cleaned['detected_type'] == baseline['detected_type']
        assert cleaned['detection_confidence'] == baseline['detection_confidence']
        assert cleaned['cleanup_applied'] == (cleaned['direction'] == 'sketch->photo')
        if mode == 'photo':
            assert cleaned['input_preview'] == baseline['input_preview']


@pytest.mark.parametrize('payload', [{}, [], {'image': 'not base64'}, {'image': 'data:image/png;base64,' + base64.b64encode(b'not an image').decode()}, {'image': image_url(), 'mode': 'invalid'}])
def test_bad_requests(payload):
    status, result = post('/api/convert', payload)
    assert status == 400
    assert 'error' in result


def test_oversized():
    status, result = post('/api/convert', {'image': base64.b64encode(b'x' * (10 * 1024 * 1024 + 1)).decode()})
    assert status == 413 and 'error' in result


def test_tensorflow_preprocessing():
    from flipart.services.image_processing import prepare_model_input
    import tensorflow as tf
    image = Image.fromarray(np.random.default_rng(42).integers(0, 256, (191, 237, 3), dtype=np.uint8))
    tensor, preview = prepare_model_input(image)
    expected = tf.image.resize(np.asarray(image, dtype=np.float32), (128, 128), antialias=True) / 127.5 - 1
    np.testing.assert_allclose(tensor[0], expected, atol=1e-6)
    assert tensor.shape == (1, 128, 128, 3)
    assert tensor.dtype == tf.float32
    assert np.isfinite(tensor.numpy()).all()
    assert float(tf.reduce_min(tensor)) >= -1 and float(tf.reduce_max(tensor)) <= 1
    assert preview.size == (128, 128)


def test_multipart_preview():
    boundary = 'FlipArtTestBoundary'
    data = (SAMPLES / 'photo.png').read_bytes()
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="mode"\r\n\r\nphoto\r\n--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="face.png"\r\nContent-Type: image/png\r\n\r\n'.encode() + data + f'\r\n--{boundary}--\r\n'.encode())
    request = Request(BASE + '/api/preview', data=body, headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    with urlopen(request, timeout=60) as response:
        assert response.status == 200
        assert json.load(response)['direction'] == 'photo->sketch'


def test_cleanup_tensor_and_corrupt_decoder():
    from flipart.services.image_processing import apply_sketch_cleanup, prepare_model_input
    from flipart.services.image_io import decode_image_bytes
    cleaned = apply_sketch_cleanup(Image.open(SAMPLES / 'sketch.png').convert('RGB'))
    tensor, _ = prepare_model_input(cleaned)
    assert tensor.shape == (1, 128, 128, 3)
    assert np.isfinite(tensor.numpy()).all()
    # Antialiased float32 resize can overshoot by a few ULPs on white pixels.
    assert tensor.numpy().min() >= -1 - 1e-6 and tensor.numpy().max() <= 1 + 1e-6
    with pytest.raises(ValueError):
        decode_image_bytes((SAMPLES / 'photo.png').read_bytes()[:100])
