import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios'; // Import axios here
// import { useNavigate } from 'react-router-dom'; // Import useNavigate - but we will remove it shortly from AuthContext!
import toast from 'react-hot-toast';

const AuthContext = createContext(null);

export const AuthProvider = ({ children, backendURL }) => { // Receive backendURL as prop
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [token, setTokenState] = useState(localStorage.getItem('token') || null); // Track token in state
  const [loading, setLoading] = useState(true); // Add loading state

// const navigate = useNavigate(); // **We will REMOVE useNavigate() from AuthContext in the next step**

// Function to set token and update localStorage
  const setToken = (newToken) => {
    setTokenState(newToken);
    if (newToken) {
      localStorage.setItem('token', newToken);
    } else {
      localStorage.removeItem('token');
    }
  };


// Function to fetch user details using the token
  const fetchUserDetails = async (accessToken) => {
    try {
      const response = await axios.get(`${backendURL}/users/me`, { // Use backendURL prop, endpoint for user details (adjust if needed)
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      setUser(response.data);
      setIsAdmin(response.data.is_admin); // Adjust based on your backend user response structure
    } catch (error) {
      console.error("Error fetching user details:", error);
      setUser(null);
      setIsAdmin(false);
      setToken(null); // Clear token if user details fetch fails
    }
  };


  useEffect(() => {
    console.log("AuthContext useEffect is running");
    const checkStoredToken = async () => {
      setLoading(true); // Start loading
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        await fetchUserDetails(storedToken); // Fetch user details if token exists
        if (!user) { // If fetchUserDetails failed and user is not set, clear token
          setToken(null); // Clear invalid token
          console.log("Token state set from localStorage:", storedToken);
          await fetchUserDetails(storedToken);
        } else {
          console.log("No token found in localStorage");
          setToken(storedToken); // Set token in state if user details fetched successfully
        }
      }
      setLoading(false); // End loading
    };

    checkStoredToken();
  }, [backendURL]); // Add backendURL and user to dependency array - user to re-run if user becomes null due to fetch fail


  const login = (userData, token) => {
    setUser(userData);
    setIsAdmin(userData.isAdmin);
    setToken(token);
    console.log("authcontext.js: login function called"); // ADDED: Log when login function is called
    console.log("authcontext.js: userData received in login:", userData); // ADDED: Log userData received
    console.log("authcontext.js: isAdmin being set to:", userData.isAdmin);
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    console.log(user)
  };

  const logout = () => {
    setUser(null);
    setIsAdmin(false);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const contextValue = {
    user,
    isAdmin,
    token, // Expose token in context
    isLoggedIn: !!token,
    login,
    logout,
    loading // Expose loading state
  };

  return (
      <AuthContext.Provider value={contextValue}>
        {!loading && children} {/* Conditionally render children when not loading */}
      </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);