import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5258/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// token'in süresi bittiyse sil ve kullanıcıyı başlangıca at
// api.interceptors.response.use(
//   (response) => response,
//   (error) => {
//     // 401 Unauthorized
//     if (error.response && error.response.status === 401) {
//       localStorage.removeItem("token");
//       window.location.href = "/login";
//     }
//     return Promise.reject(error);
//   },
// );

export default api;
