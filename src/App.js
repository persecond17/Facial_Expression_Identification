import React, { useState } from 'react';
import Paper from '@mui/material/Paper';
import './App.css';
import logo from './logo.jpg';
import background from './background.jpg';
import { Button, Stack, Grid, Box, List, ListItem, ListItemText, Link } from '@mui/material';


const App = () => {
  // State to store the uploaded image file
  const [image, setImage] = useState(null);
  const [data, setData] = useState({ songs: [], artists: [], urls: [], imgs:[] });
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
      <Paper
          sx={{
            backgroundImage: `url(${background})`,
            backgroundRepeat: 'no-repeat',
            backgroundSize: 'cover',
            minHeight: '100vh',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            flexDirection: 'column',
          }}
      >
        <div style={{
          background: '#fff',
          padding: '40px',
          borderRadius: '10px',
          boxShadow: '0px 0px 10px rgba(0, 0, 0, 0.1)',
          position: 'relative',
        }}>
        <div style={{
          position: 'absolute',
          top: '5px',
          left: '10%',
          transform: 'translateX(-50%)',
          zIndex: 1,
        }}>
            <img src={logo} alt="logo" style={{ width: '190px' }} />
          </div>
          <h1 style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '20px' }}>InMood Emotion-Based Recommendation Engine</h1>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
          <h4 style={{ fontSize: '18px', lineHeight: '1.5', marginBottom: '20px' }}>
            Please upload a facial image (JPG or PNG), we would provide a customized playlist to make your day!
            <br/>
            We would not save your image and you can remove it at any time.
          </h4>
          </Box>
          <br/>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
            <Stack direction="row" spacing={5}>
              <label htmlFor="imageUpload">
                <Button variant="contained" size="medium" component="label" sx={{ marginRight: '16px' }} onClick={() => document.getElementById('imageUpload').click()}>
                  Upload Image
                </Button>
                <input id="imageUpload" type="file" onChange={handleImageUpload} style={{ display: 'none' }} />
              </label>
              <Button variant="contained" size="medium" sx={{ marginRight: '16px' }} onClick={handleClick} disabled={!image}>
                Create Playlist
              </Button>
            </Stack>
          </Box>
        <br />

        <div>
          <Grid container spacing={0}>
            <Grid item xs={5.5} >
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh'}} >
                {image && (
                    <div>
                      <img alt="not found" width="500px" src={image} />
                      <br />
                      <Button size="small" onClick={() => setImage(null) & setData({ songs: [], artists: [], urls: [], imgs:[] })} style={{ opacity: 0.5 }}>
                        Remove
                      </Button>
                    </div>
                )}
              </Box>
            </Grid>
            <Grid item xs={5.5}>
              <br />
              {isLoading ? (
                  <p>Loading...</p>
              ) : (
                  <Grid container sx={{ justifyContent: 'center', alignItems: 'center' }}>
                    <Grid item xs={8.5}>
                      <List>
                        {data.songs.map((song, index) => (
                            <ListItem key={song}>
                              <ListItemText
                                  primary={
                                    <Link href={data.urls[index]} target="_blank">
                                      {song}
                                    </Link>
                                  }
                                  secondary={data.artists[index]}
                              />
                            </ListItem>
                        ))}
                      </List>
                    </Grid>
                  </Grid>
              )}
            </Grid>
          </Grid>

          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center'}} >
            <Stack direction="row" spacing={5}>
              {data.songs && data.songs.length>0 && (
                  <div>
                    <Button variant="contained" size="medium" sx={{ marginRight: '16px' }} onClick={() => setImage(null) & setData({ songs: [], artists: [], urls: [], imgs:[] })}>
                      Re-upload image
                    </Button>
                  </div>
              )}
              {data.songs && data.songs.length>0 && (
              <Button variant="contained" size="medium" sx={{ marginRight: '16px' }} onClick={handleClick} disabled={!image}>
                Try New Playlist
              </Button>)}
            </Stack>
          </Box>
        </div>
          {err && <p>Error: {err}</p>}
        </div>
      </Paper>
  );
}

export default App;
