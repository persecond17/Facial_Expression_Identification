import React, { useState } from 'react';

const App = () => {
  // State to store the uploaded image file
  const [image, setImage] = useState(null);
  const [data, setData] = useState({ songs: [], urls: [] });
  const [isLoading, setIsLoading] = useState(false);
  const [err, setErr] = useState('');

  // Function to handle image upload
  const handleImageUpload = (event) => {
    // Get the uploaded file
    let image = event.target.files[0];

    // Read the file and convert it to a data URL
    let reader = new FileReader();
    reader.onloadend = () => {
      // Check if reading was successful
      if (reader.result) {
        // Success: set the result to the image state variable
        setImage(reader.result);
      }
    };
    reader.readAsDataURL(image);
  };

  const handleClick = async () => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('image', image); // Append the image file to FormData
      console.log('image', image)

      const response = await fetch('http://18.119.0.164:5000/get_recommendations/', {
        method: 'POST',
        body: formData, // Set the FormData as the request body
      });

      if (response.ok) {
        const data = await response.json();
        // Update state with fetched data
        setData(data);
      } else {
        throw new Error('Failed to fetch data');
      }
    } catch (err) {
      setErr(err.message);
    } finally {
      setIsLoading(false);
    }
  };


  return (
      <div>
        <h1>Emotion-Based Playlist Creator</h1>
        <h2>Please upload a facial image, we would provide a customized playlist to make your day!<br />
          (We would not save your image and you can remove it at any time.)</h2>
        <label htmlFor="imageUpload">Upload Image:</label>
        <input id="imageUpload" type="file" onChange={handleImageUpload} />
        <br />
        <div>
          {image && (
              <div>
                <img alt="not found" width="500px" src={image} />
                <br />
                <button onClick={() => setImage(null)}>Remove</button>
              </div>
          )}
          <br />
          <button onClick={handleClick}>Create Playlist</button>
        </div>
        <div>
          {isLoading ? (
              <p>Loading...</p>
          ) : (
              <ul>
                {data.songs.map((song, index) => (
                    <li key={song}>
                      <a href={data.urls[index]}>{song}</a>
                    </li>
                ))}
              </ul>
          )}
        </div>
        {err && <p>Error: {err}</p>}
      </div>
  );
};

export default App;
