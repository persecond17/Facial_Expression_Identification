from backend.models_src.load_model import *
import random
import streamlit as st
import pandas as pd


model_path = 'backend/models/fer_cnn_v03.pth'
df = pd.read_csv('backend/song_list.csv')
output_path = 'image.jpg'


def generate_playlist(image):
    predicted_emotion = predict(model_path, image)
    print("Emotion: ", predicted_emotion)
    target = df[df['category'] == predicted_emotion]
    song_pool = target['name'].tolist()
    song_url_dict = target[['name', 'urls']].set_index('name').to_dict()['urls']
    song_artist_dict = target[['name', 'artist']].set_index('name').to_dict()['artist']
    song_pool = list(set(song_pool))
    random.shuffle(song_pool)
    song_names = random.sample(song_pool, 10)  # sampling without duplicate
    song_urls = [song_url_dict[song] for song in song_names]
    artists = [song_artist_dict[song] for song in song_names]


    # Create list of playlist items with song name and artist hyperlink
    playlist_items = []
    for i in range(len(song_names)):
        song_name = song_names[i]
        artist = artists[i]
        song_url = song_urls[i]
        item = f"[{song_name}]({song_url}) by {artist}"
        playlist_items.append(item)

    # Return playlist items as a string with newlines between each item
    return playlist_items#"\n".join(playlist_items)


# Define Streamlit app
def app():
    # Set page title and favicon
    st.set_page_config(page_icon=":musical_note:")
    st.header("Facial Image Song Playlist Generator")

    # Add file uploader for facial image
    uploaded_file = st.file_uploader("Upload facial image", type=["jpg", "jpeg", "png"])

    # Add "Upload" button to generate playlist
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, width=500, caption='Uploaded image')

        tmp_file_path = f"/tmp/{uploaded_file.name}"
        with open(tmp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Add "Generate Playlist" button to generate playlist
        if st.button("Generate Playlist"):
            # Generate playlist from image
            playlist = generate_playlist(uploaded_file)

            # Display playlist
            st.success("Here's your customized playlist!")
            # st.markdown(playlist, unsafe_allow_html=True)
            for item in playlist:
                st.write(item)

            # Add "Try New Playlist" button to generate new playlist
            if st.button("Try New Playlist"):
                st.experimental_rerun()

        # Add "Remove" button to remove image and start over
        if st.button("Remove"):
            uploaded_file = None
            st.experimental_rerun()


# Run Streamlit app
if __name__ == "__main__":
    app()