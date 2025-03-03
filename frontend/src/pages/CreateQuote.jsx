import React, { useState } from 'react';
import { PlusCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext.jsx';

function CreateQuote() {
  const [text, setText] = useState('');
  const [author, setAuthor] = useState('');
  const [approved, setApprove] = useState('false');
  const { token, user  } = useAuth(); //change


  const handleSubmit = async (e) => {
    console.log('handleSubmit function is called!')
    e.preventDefault();
    console.log("Token value immediately before api.post:", token);
    console.log("Text value before api.post:", text);  // **VERY IMPORTANT - ADD THIS LINE**
    console.log("Author value before api.post:", author); // **VERY
    console.log("Token value before api.post:", token)
    console.log("user value before api.post:", user);
     //change
    try {
      await api.post(
          '/quote',
          {text,author,approved},
          // {
          //   text: text,
          //   author: author,
          //   approved: false
          // },
          {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/x-www-form-urlencoded'
            }
          }
      );
      toast.success('Quote submitted for approval!');
      setText('');
      setAuthor('');
    } catch (error) {
      let errorMessage = 'Failed to create quote'; // Default error message
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (typeof error.response.data.detail === 'object') {
          errorMessage = JSON.stringify(error.response.data.detail); // Convert object to string
        }
      } else if (error.response?.data) {
        if (typeof error.response.data === 'object') {
          errorMessage = JSON.stringify(error.response.data); // Convert object to string
        } else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        }
      }
      toast.error(errorMessage || 'Unknown error');
    }
  };

  return (
      <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-md overflow-hidden">
        <div className="p-8">
          <div className="flex items-center justify-center mb-6">
            <PlusCircle className="h-8 w-8 text-blue-600" />
            <h2 className="ml-2 text-2xl font-bold text-gray-800">Create New Quote</h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">Quote Text</label>
              <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows="4"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200"
                  required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Author</label>
              <input
                  type="text"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200"
                  required
              />
            </div>

            <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Submit Quote
            </button>
          </form>
        </div>
      </div>
  );
}

export default CreateQuote;