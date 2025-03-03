import React, { useState, useEffect } from 'react';
import { Quote } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../api/axios';

function Home() {
  const [quote, setQuote] = useState(null);

  const fetchRandomQuote = async () => {
    // console.log("fetchRandomQuote function called");
    try {
      console.log("Before API call to /quote");
      const response = await api.get('/quote');
      console.log(response)
      console.log("API call to /quote successful", response); // Log success response
      console.log("Response Data:", response.data);
      setQuote(response.data);
      console.log("Quote state updated:", response.data);
    } catch (error) {
      console.error("Error fetching quote:", error);
      toast.error('Failed to fetch quote');
    }
  };

  useEffect(() => {
    console.log("useEffect in Home component is running");
    fetchRandomQuote().then(r =>
    console.log("Error")
    );
  }, []);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="flex items-center justify-center mb-8">
          <Quote className="h-12 w-12 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-800 ml-3">Quote of the Day</h1>
        </div>
        
        {quote ? (
          <div className="text-center">
            <blockquote className="text-2xl italic text-gray-700 mb-4">
              "{quote.text}"
            </blockquote>
            <p className="text-gray-600">- {quote.author}</p>
          </div>
        ) : (
          <p className="text-center text-gray-600">Loading quote...</p>
        )}
        
        <button
          onClick={fetchRandomQuote}
          className="mt-8 mx-auto block px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Get Another Quote
        </button>
      </div>
    </div>
  );
}

export default Home