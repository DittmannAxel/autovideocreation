# Autovideocreation
## a short test to combine the creativity of context, picture and video creation with ready build tools!


The offered code exemplifies an original method for producing a video with visuals and narration from a given key-word or short sentence. To come up with suggestions for keywords and ideas from **DALL-E** API calls, it makes also use of **OpenAI's GPT-3.5-turbo API**. The **ElevenLabs API** is than used to record narration to go along with the video scenes. After that, the photos and voiceovers are combined in a movie using a zoom effect. Using this method, you may easily generate interesting material for your blog entries, lessons, or presentations.

This code is **purely for testing** - you need to manually cleanup your directory for the next run. I just want to keep all the old files.

[![My Example of a sunset on the beach](https://i.vimeocdn.com/video/1659513300-739c6b0acfb239cab10f1d6430d246c85b084eecd3831285b15f9a43cc00a741-d_640)](https://vimeo.com/820110435 "A small sample of an autogenerated video")

How to use the Python script:

1. Install [ffmpeg](https://ffmpeg.org/) on your system first - I am using a python module which makes use of ffmpeg.


2. Install Python libraries: 

```python
pip install imageio pillow requests pydub openai elevenlabs
```
3. in line 12+13 provide your keys:
```python
openai.api_key = "Set-your-OpenAI-API-Key-Here"
set_api_key("Set-Your-Elevenlabs-API-KEy Here")
```
4. And do not forget to change you key-word or small phrase:
```python
# Set the creation of the phrase or word
creation = "sunset on the beach"
```
5. You may alter the OpenAPI Prompts as you wish :-) - I did a comment in the code. I did not spent too much time in highly sphisticated prompt engineering - it is just a PoC
6. And than: you are ready to start :-)


## Enjoy!!