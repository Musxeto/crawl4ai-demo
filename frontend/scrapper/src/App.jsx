import React, { useEffect, useState } from "react";

const App = () => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/data/")
      .then((response) => response.json())
      .then((data) => {
        setBooks(data.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setError(error);
        setLoading(false);
      });
  }, []);

  if (loading)
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-100">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-500"></div>
      </div>
    );

  if (error)
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-100">
        <p className="text-xl text-red-500 font-semibold">
          Error fetching data. Please try again later.
        </p>
      </div>
    );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">
        📚 Top Books on Amazon
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
        {books.map((book) => (
          <div
            key={book.id}
            className="bg-white shadow-lg rounded-lg overflow-hidden p-5 transition-transform transform hover:scale-105 hover:shadow-2xl"
          >
            <img
              src={book.image_url}
              alt={book.title}
              className="w-full h-64 object-cover rounded-lg"
            />
            <h2 className="text-xl font-semibold text-gray-800 mt-4">
              {book.title}
            </h2>
            <p className="text-gray-600 text-sm mt-1">by {book.author}</p>
            <p className="text-gray-700 font-medium mt-2">⭐ {book.ranking}</p>
            <a
              href={book.amazon_link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-3 px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition duration-300"
            >
              Buy on Amazon
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;
