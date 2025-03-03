import React, { useState, useEffect } from 'react';
import { Settings, Check, X, RefreshCw, Plus } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../api/axios';
import {useAuth} from "../context/AuthContext.jsx";

function AdminDashboard() {
  const [pendingQuotes, setPendingQuotes] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [text, setText] = useState('');
  const [author, setAuthor] = useState('');
  const { token, user  } = useAuth();

  const fetchPendingQuotes = async () => {
    try {
      const response = await api.get('/admin/quotes');
      setPendingQuotes(response.data);
    } catch (error) {
      toast.error('Failed to fetch pending quotes');
    }
  };

  useEffect(() => {
    fetchPendingQuotes();
  }, []);

  const handleApprove = async (quoteId) => {
    try {
      await api.put(`/admin/quotes/${quoteId}`, { status: 'approved' });
      toast.success('Quote approved!');
      await fetchPendingQuotes();
    } catch (error) {
      toast.error('Failed to approve quote');
    }
  };

  const handleDelete = async (quoteId) => {
    try {
      await api.delete(`/admin/quotes/${quoteId}`);
      toast.success('Quote deleted!');
      await fetchPendingQuotes();
    } catch (error) {
      toast.error('Failed to delete quote');
    }
  };

  return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center">
              <Settings className="h-8 w-8 text-blue-600" />
              <h2 className="ml-2 text-2xl font-bold text-gray-800">Admin Dashboard</h2>
            </div>
            <div className="flex space-x-2">
              <button
                  onClick={fetchPendingQuotes}
                  className="flex items-center px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                Refresh
              </button>
              {/*<button*/}
              {/*    onClick={() => setShowAddForm(!showAddForm)}*/}
              {/*    className="flex items-center px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"*/}
              {/*>*/}
              {/*  <Plus className="h-4 w-4 mr-1" />*/}
              {/*  {showAddForm ? "Cancel" : "Add Quote"}*/}
              {/*</button>*/}
            </div>
          </div>

          {/*{showAddForm && (*/}
          {/*    <div className="mb-6 border rounded-lg p-4">*/}
          {/*      <form onSubmit={handleAddQuote}> /!* Added form element and onSubmit handler *!/*/}
          {/*        <input*/}
          {/*            type="text"*/}
          {/*            placeholder="Quote Text"*/}
          {/*            value={text} // Use 'text' state*/}
          {/*            onChange={(e) => setText(e.target.value)} // Update 'text' state*/}
          {/*            className="w-full mb-2 p-2 border rounded"*/}
          {/*            required // Added required attribute*/}
          {/*        />*/}
          {/*        <input*/}
          {/*            type="text"*/}
          {/*            placeholder="Author"*/}
          {/*            value={author} // Use 'author' state*/}
          {/*            onChange={(e) => setAuthor(e.target.value)} // Update 'author' state*/}
          {/*            className="w-full mb-2 p-2 border rounded"*/}
          {/*            required // Added required attribute*/}
          {/*        />*/}
          {/*        <button*/}
          {/*            type="submit" // Changed to submit button*/}
          {/*            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"*/}
          {/*        >*/}
          {/*          Add*/}
          {/*        </button>*/}
          {/*        <button*/}
          {/*            type="button" // Cancel button type button to prevent form submission*/}
          {/*            onClick={() => setShowAddForm(false)}*/}
          {/*            className="px-4 py-2 ml-2 bg-gray-400 text-white rounded hover:bg-gray-500"*/}
          {/*        >*/}
          {/*          Cancel*/}
          {/*        </button>*/}
          {/*      </form>*/}
          {/*    </div>*/}
          {/*)}*/}

          <div className="space-y-6">
            {pendingQuotes.length === 0 ? (
                <p className="text-center text-gray-600">No pending quotes to review</p>
            ) : (
                pendingQuotes.map((quote) => (
                    <div
                        key={quote.id}
                        className="border rounded-lg p-4 space-y-2"
                    >
                      <p className="text-lg text-gray-800">"{quote.text}"</p>
                      <p className="text-gray-600">- {quote.author}</p>
                      <div className="flex justify-end space-x-2">
                        <button
                            onClick={() => handleApprove(quote.id)}
                            className="flex items-center px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          <Check className="h-4 w-4 mr-1" />
                          Approve
                        </button>
                        <button
                            onClick={() => handleDelete(quote.id)}
                            className="flex items-center px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                        >
                          <X className="h-4 w-4 mr-1" />
                          Delete
                        </button>
                      </div>
                    </div>
                ))
            )}
          </div>
        </div>
      </div>
  );
}

export default AdminDashboard;