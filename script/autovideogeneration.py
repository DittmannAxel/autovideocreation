import os
import imageio
import requests
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment
import openai
from elevenlabs import generate, play, set_api_key

# Set API keys
openai.api_key = "Set-your-OpenAI-API-Key-Here"
set_api_key("Set-Your-Elevenlabs-API-KEy Here")

# Set the creation of the phrase or word
creation = "sunset on the beach"
seconds_array = []

def get_chat_response(creation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        #Just use your onw prompt here - maybe much more creative than mine
        messages=[
            {"role": "system", "content": "I want you to act as a brainstorm helper. your ideas are bright and creative and you can bring one idea to the next level. When I bring a keyword, your will respond with only 2 keywords, which belong together. Please use no bullet points"},
            {"role": "user", "content": creation},
        ],
        temperature=0,
    )
    return response

# removing numbers from the answer string -> sometimes there are numbers as part of an enumaration
def process_text(response):
    text = response['choices'][0]['message']['content']
    creativity = re.sub('[0-9.]', '', text)
    creativity_array = creativity.split()
    creativity_array.insert(0, creation)
    return creativity_array

#generate a dallee prompt for each element in the creativity array -> waiting for midjourney, so there might be more choices

def generate_dalle_prompt(element):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        #Just use your onw prompt here - maybe much more creative than mine
        messages=[
            {"role": "system", "content": "I want you to create a dalle prompt that will accurately create an image for Dell-E"},
            {"role": "user", "content": "Can you generate a prompt for " + element},
        ],
        temperature=0,
    )
    return response

# creating the image from the dalle prompt
def generate_image(response):
    image_response = openai.Image.create(
        prompt=response['choices'][0]['message']['content'],
        n=1,
        size="1024x1024"
    )
    image_url = image_response['data'][0]['url']
    return image_url

# download the image for the video processing
def download_image(image_url, element):
    try:
        url_response = requests.get(image_url, stream=True)
    except requests.exceptions.RequestException as e:
        print(e)

    filename = element + "_image.png"
    if url_response.status_code == 200:
        with open(filename, 'wb') as file:
            for chunk in url_response.iter_content(chunk_size=8192):
                file.write(chunk)
    else:
        print(f"Error downloading image: {e.status_code}")
    return filename

# generate voice text from the brainstorm summary and write it to a file
def generate_voice(element, creation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "I want you to act as an explainer and explain the phrase: " + element + " in only 20 words"},
            {"role": "user", "content": creation},
        ],
        temperature=0,
    )
# generate the voice
    voicetextanswer = response['choices'][0]['message']['content']
    voicetext = element + "  " + voicetextanswer
    #change the value "Bella" to one of the other voices
    audio = generate(voicetext, voice="Bella")
    output_file = element + "_audio.mp3"
    with open(output_file, 'wb') as f:
                f.write(audio)
    return output_file

def concatenate_mp3_files(input_files, output_file):
    combined_audio = AudioSegment.empty()

    for input_file in input_files:
        audio = AudioSegment.from_mp3(input_file)
        combined_audio += audio

    combined_audio.export(output_file, format="mp3")

def create_video_from_images_and_audio(images, audio_file, output_file, fps=24, duration_per_image=3, text=None):
    image_frames = []

    for idx, img_path in enumerate(images):
        img = Image.open(img_path)

        if text:
            width, height = img.size
            pixels = img.load()
            total_luminance = 0
            num_pixels = width * height
            #calculate the overall grade - more dark or more white
            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    luminance = (0.299 * r) + (0.587 * g) + (0.114 * b)
                    total_luminance += luminance

            average_luminance = total_luminance / num_pixels
            #change the color of the text to vaid white on white or black on black
            fontcolor = "black" if average_luminance > 128 else "white"

            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 48)
            draw.text((img.width // 4, img.height // 2), text[idx], font=font, fill=fontcolor)
        # I try to be as long as the voice will take
        duration_multiplier = int(seconds_array[idx] + 0.5)
        # zoom as long as the voice duration for that segment
        for t in range(fps * duration_multiplier):
            img_resized = img.resize((int(img.width * (1 + 0.05 * t / fps)), int(img.height * (1 + 0.05 * t / fps))))
            img_cropped = img_resized.crop((img_resized.width // 2 - img.width // 2, img_resized.height // 2 - img.height // 2, img_resized.width // 2 + img.width // 2, img_resized.height // 2 + img.height // 2))
            image_frames.append(img_cropped)

    with imageio.get_writer(output_file, fps=fps, format='FFMPEG', codec='libx264', bitrate='16M', pixelformat='yuv420p', ffmpeg_params=['-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', '-shortest']) as writer:
        for frame in image_frames:
            writer.append_data(imageio.core.util.asarray(frame))

    cmd = f'ffmpeg -i {output_file} -i {audio_file} -c:v copy -c:a copy -shortest {output_file[:-4]}_with_audio.mp4'
    subprocess.run(cmd, shell=True, check=True)


def main():
    response = get_chat_response(creation)
    creativity_array = process_text(response)

    print(creativity_array)
    seconds_totallenght = 0
    images = []
    text = []
    audiofiles = []


    for element in creativity_array:
        # Generate Dall-E prompt and image
        response = generate_dalle_prompt(element)
        image_url = generate_image(response)
        image_filename = download_image(image_url, element)
        images.append(image_filename)

        audio_filename = generate_voice(element, creation)
        audio = AudioSegment.from_mp3(element+"_audio.mp3")
        seconds_array.append(len(audio)/1000)
        seconds_totallenght = seconds_totallenght + len(audio)/1000
        audiofiles.append(audio_filename)
        text.append(element)

    # Combine images and audio
    output_audio_file ='aufnahme.mp3'
    output_file = 'video.mp4'
    concatenate_mp3_files(audiofiles, output_audio_file)
    create_video_from_images_and_audio(images, output_audio_file, output_file, text=text)

if __name__ == "__main__":
    main()

