import io
import base64

from gtts import gTTS, gTTSError

import streamlit as st

def autoplay_audio(audio_base64: str):
    """ https://discuss.streamlit.io/t/how-to-play-an-audio-file-automatically-generated-using-text-to-speech-in-streamlit/33201 """

    md = f"""
        <audio id="myAudio" controls autoplay="true">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        <script>
            document.getElementById('myAudio').playbackRate = 1.5;
        </script>
        """

    # if st.session_state.user_preferences["tts"] == TTS_OPTIONS.GOOGLE:
    #     with st.sidebar:
    #         with st.expander(".", expanded=False):
    #             st.components.v1.html(md)
    # else:
        # st.write(md, unsafe_allow_html=True) # won't speed up the playback



    # st.components.v1.html(md)
    st.write(md, unsafe_allow_html=True) # won't speed up the playback





def TTS(text, language='en', slow=False):
    try:
        tts = gTTS(text=text, lang=language, slow=slow)

        with io.BytesIO() as file_stream:
            tts.write_to_fp(file_stream) # Write the speech data to the file stream
            file_stream.seek(0) # Move to the beginning of the file stream
            audio_base64 = base64.b64encode(file_stream.read()).decode('utf-8') # Read the audio data and encode it in base64
        autoplay_audio(audio_base64)
    except gTTSError as e:
        st.error(e)
        st.exception(e)
