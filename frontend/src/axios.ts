import axios from 'axios';

console.log(import.meta.env.VITE_API_BASE_URL)

// Create an Axios instance
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Access-control-allow-origin': '*',
  }
  // Any additional configuration can go here
});

// Export the instance for use in your application
export default axiosInstance;