import React, { useState } from 'react';

const App = () => {
  // State to store the uploaded image file
  const [image, setImage] = useState(null);
  const [data, setData] = useState({songs: [], urls: []});
  const [isLoading, setIsLoading] = useState(false);
  const [err, setErr] = useState('');

  // Function to handle image upload
  const handleImageUpload = (event) => {
    // Get the uploaded file
    const file = event.target.files[0];
    // Set the image file state
    setImage(file)
  };


  const handleClick = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/get_recommendations/', {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Error! status: ${response.status}`);
      }

      const result = await response.json();

      console.log('result is: ', JSON.stringify(result, null, 4));

      setData({songs: result[0], urls: result[1]});
    } catch (err) {
      setErr(err.message);
    } finally {
      setIsLoading(false);
    }
  };


  return (
      <div>
        <h1>Emotion-Based Playlist Creator</h1>
        <input type="file" onChange={handleImageUpload} />
        <br />
            <div>
              <button onClick={handleClick}>Create Playlist</button>
            </div>
        <div>
          <ul>
            {data.songs.map((song, index) => (
                <li key={index}>
                  <a href={data.urls[index]}>{song}</a>
                </li>
            ))}
          </ul>
        </div>
      </div>
  );
};

export default App;
