from model import whisperai_model as model
from whisper_service import generate_full_analysis

output = generate_full_analysis("test_audio/sample.mp3", model)

from pprint import pprint
pprint(output)