import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  Grid,
  Chip,
  Fade,
  Grow,
  Divider,
  useTheme,
  IconButton,
  Tooltip,
  Zoom,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import DeleteIcon from '@mui/icons-material/Delete';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ImageIcon from '@mui/icons-material/Image';
import UploadFileIcon from '@mui/icons-material/UploadFile';

// Define the API base URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

console.log('Using API base URL:', API_BASE_URL);

const WaybillUploader = () => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';
  const [files, setFiles] = useState([]);
  const [extractionModels, setExtractionModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [uploadedWaybillIds, setUploadedWaybillIds] = useState([]);
  const [downloadUrl, setDownloadUrl] = useState('');

  useEffect(() => {
    // Fetch available extraction models
    const fetchModels = async () => {
      try {
        console.log('Fetching extraction models from:', `${API_BASE_URL}/extraction-models/`);
        
        // Add a timeout to the request
        const response = await axios.get(`${API_BASE_URL}/extraction-models/`, {
          timeout: 10000, // 10 seconds timeout
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          }
        });
        
        console.log('Extraction models response:', response.data);
        setExtractionModels(response.data);
        if (response.data.length > 0) {
          setSelectedModel(response.data[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch extraction models:', err);
        console.error('Error details:', {
          message: err.message,
          code: err.code,
          response: err.response ? {
            status: err.response.status,
            data: err.response.data,
            headers: err.response.headers
          } : 'No response',
          request: err.request ? 'Request was made but no response was received' : 'No request was made'
        });
        
        setError(`Failed to fetch extraction models: ${err.message}. Please check that the backend server is running.`);
      }
    };
    fetchModels();
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.pdf']
    },
    onDrop: acceptedFiles => {
      setFiles(acceptedFiles.map(file => Object.assign(file, {
        preview: URL.createObjectURL(file)
      })));
      setSuccess(false);
    }
  });

  const handleUpload = async () => {
    if (!selectedModel) {
      setError('Please select an extraction model');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(false);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('images', file);
    });
    formData.append('extraction_model', selectedModel);

    try {
      const response = await axios.post(`${API_BASE_URL}/waybills/bulk_upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Store the waybill IDs and download URL from the response
      if (response.data && response.data.ids) {
        setUploadedWaybillIds(response.data.ids);
        setDownloadUrl(response.data.download_url);
      }
      
      setSuccess(true);
      setFiles([]);
    } catch (err) {
      console.error('Failed to upload files:', err);
      setError(`Failed to upload files: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async () => {
    try {
      setUploading(true);
      
      // Construct the download URL properly
      let url;
      if (downloadUrl) {
        // Remove any leading or trailing slashes from both API_BASE_URL and downloadUrl
        const baseUrl = API_BASE_URL.replace(/\/+$/, '');
        const cleanDownloadUrl = downloadUrl
          .replace(/^\/+/, '')  // Remove leading slashes
          .replace(/^api\//, ''); // Remove 'api/' prefix if present
        
        // Use the waybills endpoint instead of waybill-images
        url = `${baseUrl}/waybills/download_excel/?ids=${uploadedWaybillIds.join(',')}`;
      } else {
        url = `${API_BASE_URL.replace(/\/+$/, '')}/waybills/download_excel/`;
      }
      
      console.log('Download URL:', url);
      
      const response = await axios.get(url, {
        responseType: 'blob',
      });
      
      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = blobUrl;
      link.setAttribute('download', `waybills_${new Date().toISOString()}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      // Clear the waybill IDs and download URL after download
      setUploadedWaybillIds([]);
      setDownloadUrl('');
      
      setUploading(false);
    } catch (err) {
      console.error('Failed to download Excel file:', err);
      console.error('Error details:', {
        message: err.message,
        code: err.code,
        status: err.status,
        url: err.config?.url
      });
      setError(`Failed to download Excel file: ${err.message}`);
      setUploading(false);
    }
  };

  const removeFile = (fileToRemove) => {
    setFiles(files.filter(file => file !== fileToRemove));
  };

  return (
    <Box sx={{ 
      maxWidth: 900, 
      mx: 'auto', 
      p: 4,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
    }}>
      <Paper 
        elevation={6} 
        sx={{ 
          p: 4, 
          borderRadius: 3,
          background: isDarkMode 
            ? 'linear-gradient(145deg, #1E1E1E 0%, #121212 100%)' 
            : 'linear-gradient(145deg, #ffffff 0%, #f5f7fa 100%)',
          boxShadow: isDarkMode
            ? '0 10px 30px rgba(0,0,0,0.3)'
            : '0 10px 30px rgba(0,0,0,0.1)',
          transition: 'background 0.5s ease, box-shadow 0.5s ease',
        }}
      >
        <Grow in={true} timeout={800}>
          <Typography 
            variant="h3" 
            gutterBottom 
            align="center" 
            sx={{ 
              fontWeight: 700, 
              mb: 4,
              background: isDarkMode
                ? 'linear-gradient(90deg, #90CAF9 0%, #CE93D8 100%)'
                : 'linear-gradient(90deg, #2196F3 0%, #673AB7 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              letterSpacing: '-0.5px'
            }}
          >
            Waybill Extractor
          </Typography>
        </Grow>

        <Divider sx={{ mb: 4 }} />

        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Fade in={true} timeout={1000}>
              <Box>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: theme.palette.text.primary }}>
                  1. Select Extraction Model
                </Typography>
                <FormControl fullWidth variant="outlined" sx={{ mb: 3 }}>
                  <InputLabel>Extraction Model</InputLabel>
                  <Select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    label="Extraction Model"
                  >
                    {extractionModels.map((model) => (
                      <MenuItem key={model.id} value={model.id}>
                        {model.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: theme.palette.text.primary }}>
                  2. Upload Waybill Images
                </Typography>
                <Box
                  {...getRootProps()}
                  sx={{
                    border: '2px dashed',
                    borderColor: isDragActive ? 'primary.main' : 'divider',
                    borderRadius: 3,
                    p: 4,
                    mb: 3,
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    backgroundColor: isDragActive 
                      ? (isDarkMode ? 'rgba(144, 202, 249, 0.08)' : 'rgba(33, 150, 243, 0.08)') 
                      : 'transparent',
                    '&:hover': {
                      borderColor: 'primary.main',
                      backgroundColor: isDarkMode 
                        ? 'rgba(144, 202, 249, 0.04)' 
                        : 'rgba(33, 150, 243, 0.04)',
                      transform: 'translateY(-2px)',
                    },
                  }}
                >
                  <input {...getInputProps()} />
                  <Zoom in={true} timeout={800}>
                    <CloudUploadIcon 
                      sx={{ 
                        fontSize: 60, 
                        color: isDragActive ? 'primary.main' : 'text.secondary', 
                        mb: 2,
                        animation: isDragActive ? 'pulse 1.5s infinite' : 'none',
                        '@keyframes pulse': {
                          '0%': {
                            transform: 'scale(1)',
                          },
                          '50%': {
                            transform: 'scale(1.1)',
                          },
                          '100%': {
                            transform: 'scale(1)',
                          },
                        },
                      }} 
                    />
                  </Zoom>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    {isDragActive ? 'Drop files here' : 'Drag and drop waybill images here'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    or click to select files
                  </Typography>
                </Box>
              </Box>
            </Fade>
          </Grid>

          <Grid item xs={12} md={6}>
            <Fade in={true} timeout={1200}>
              <Box>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: theme.palette.text.primary }}>
                  3. Selected Files
                </Typography>
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    minHeight: 200, 
                    maxHeight: 300, 
                    overflow: 'auto',
                    borderRadius: 2,
                    backgroundColor: isDarkMode ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.01)',
                    transition: 'background-color 0.5s ease',
                  }}
                >
                  {files.length > 0 ? (
                    files.map((file, index) => (
                      <Grow key={file.name} in={true} timeout={500 + (index * 100)}>
                        <Box 
                          sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            p: 1, 
                            mb: 1, 
                            borderRadius: 2,
                            backgroundColor: 'background.paper',
                            boxShadow: isDarkMode 
                              ? '0 2px 8px rgba(0,0,0,0.2)' 
                              : '0 2px 8px rgba(0,0,0,0.05)',
                            transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                            '&:hover': {
                              transform: 'translateY(-2px)',
                              boxShadow: isDarkMode 
                                ? '0 4px 12px rgba(0,0,0,0.3)' 
                                : '0 4px 12px rgba(0,0,0,0.1)',
                            }
                          }}
                        >
                          {file.type.startsWith('image/') ? (
                            <ImageIcon sx={{ mr: 1, color: 'primary.main' }} />
                          ) : (
                            <InsertDriveFileIcon sx={{ mr: 1, color: 'primary.main' }} />
                          )}
                          <Typography variant="body2" sx={{ flex: 1, fontWeight: 500 }}>
                            {file.name}
                          </Typography>
                          <Chip 
                            label={`${(file.size / 1024).toFixed(1)} KB`} 
                            size="small" 
                            sx={{ mr: 1 }} 
                            variant="outlined"
                          />
                          <Tooltip title="Remove file">
                            <IconButton 
                              size="small" 
                              onClick={() => removeFile(file)}
                              sx={{
                                transition: 'transform 0.2s ease, color 0.2s ease',
                                '&:hover': {
                                  transform: 'rotate(90deg)',
                                  color: 'error.main',
                                }
                              }}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Grow>
                    ))
                  ) : (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', flexDirection: 'column' }}>
                      <UploadFileIcon sx={{ color: 'text.secondary', fontSize: 40, mb: 1, opacity: 0.5 }} />
                      <Typography variant="body2" color="text.secondary">
                        No files selected
                      </Typography>
                    </Box>
                  )}
                </Paper>
              </Box>
            </Fade>
          </Grid>
        </Grid>

        {error && (
          <Grow in={true}>
            <Alert 
              severity="error" 
              sx={{ 
                mt: 3, 
                borderRadius: 2,
                boxShadow: isDarkMode 
                  ? '0 2px 8px rgba(0,0,0,0.2)' 
                  : '0 2px 8px rgba(0,0,0,0.05)'
              }}
              onClose={() => setError(null)}
            >
              {error}
            </Alert>
          </Grow>
        )}

        {success && (
          <Grow in={true}>
            <Alert 
              severity="success" 
              sx={{ 
                mt: 3, 
                borderRadius: 2,
                boxShadow: isDarkMode 
                  ? '0 2px 8px rgba(0,0,0,0.2)' 
                  : '0 2px 8px rgba(0,0,0,0.05)'
              }}
              icon={<CheckCircleIcon fontSize="inherit" />}
              onClose={() => setSuccess(false)}
            >
              Files uploaded successfully! You can now download the extracted data.
            </Alert>
          </Grow>
        )}

        <Divider sx={{ my: 4 }} />

        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: theme.palette.text.primary }}>
          4. Process & Download
        </Typography>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} sm={6}>
            <Button
              variant="contained"
              onClick={handleUpload}
              disabled={files.length === 0 || uploading}
              fullWidth
              size="large"
              startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <CloudUploadIcon />}
              sx={{ 
                py: 1.5, 
                borderRadius: 2,
                background: isDarkMode
                  ? 'linear-gradient(90deg, #42A5F5 0%, #2196F3 100%)'
                  : 'linear-gradient(90deg, #2196F3 0%, #1976D2 100%)',
                boxShadow: isDarkMode
                  ? '0 4px 10px rgba(66, 165, 245, 0.3)'
                  : '0 4px 10px rgba(33, 150, 243, 0.3)',
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                '&:hover': {
                  boxShadow: isDarkMode
                    ? '0 6px 15px rgba(66, 165, 245, 0.4)'
                    : '0 6px 15px rgba(33, 150, 243, 0.4)',
                  transform: 'translateY(-2px)',
                },
                '&:active': {
                  transform: 'translateY(0)',
                }
              }}
            >
              {uploading ? 'Uploading...' : 'Upload & Process Files'}
            </Button>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Button
              variant="outlined"
              onClick={handleDownload}
              fullWidth
              size="large"
              startIcon={<FileDownloadIcon />}
              sx={{ 
                py: 1.5, 
                borderRadius: 2,
                borderWidth: 2,
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                '&:hover': {
                  borderWidth: 2,
                  transform: 'translateY(-2px)',
                  boxShadow: isDarkMode
                    ? '0 4px 12px rgba(144, 202, 249, 0.2)'
                    : '0 4px 12px rgba(33, 150, 243, 0.2)',
                },
                '&:active': {
                  transform: 'translateY(0)',
                }
              }}
            >
              Download Excel
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default WaybillUploader; 