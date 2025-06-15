import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [moodQuery, setMoodQuery] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [moodInterpretation, setMoodInterpretation] = useState('');
  const [error, setError] = useState('');

  const moodSuggestions = [
    "I need something cozy for a rainy evening",
    "Action-packed weekend vibes",
    "Something to make me laugh after a long day",
    "Romantic and heartwarming",
    "Mind-bending sci-fi adventure",
    "Feel-good family entertainment",
    "Dark and mysterious thriller",
    "Nostalgic comfort viewing"
  ];

  const handleMoodSubmit = async (e) => {
    e.preventDefault();
    if (!moodQuery.trim()) return;

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/recommendations`, {
        mood: moodQuery,
        user_id: 'demo-user'
      });
      
      setRecommendations(response.data.recommendations);
      setMoodInterpretation(response.data.mood_interpretation);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('Failed to get recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setMoodQuery(suggestion);
  };

  const getRatingColor = (rating) => {
    if (rating >= 8) return 'text-green-600';
    if (rating >= 7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatRating = (rating) => {
    return rating ? rating.toFixed(1) : 'N/A';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-pink-500 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xl">P</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">Poppy</h1>
                <p className="text-purple-200 text-sm">AI-Powered Entertainment Discovery</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-5xl font-bold text-white mb-6">
            What's your <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-purple-400">vibe</span> today?
          </h2>
          <p className="text-xl text-purple-200 mb-8 max-w-3xl mx-auto">
            Tell me how you're feeling or what kind of mood you're in, and I'll find the perfect movies and shows that match your energy.
          </p>
        </div>

        {/* Mood Input */}
        <div className="max-w-4xl mx-auto mb-12">
          <form onSubmit={handleMoodSubmit} className="space-y-6">
            <div className="relative">
              <textarea
                value={moodQuery}
                onChange={(e) => setMoodQuery(e.target.value)}
                placeholder="Describe your mood or what you're in the mood for... (e.g., 'I want something cozy and heartwarming for a Sunday afternoon')"
                className="w-full p-6 bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none h-32 text-lg"
                disabled={loading}
              />
            </div>
            
            <div className="flex justify-center">
              <button
                type="submit"
                disabled={loading || !moodQuery.trim()}
                className="px-12 py-4 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-full hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200 text-lg shadow-xl"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Finding perfect matches...</span>
                  </div>
                ) : (
                  'Get My Recommendations ✨'
                )}
              </button>
            </div>
          </form>

          {/* Mood Suggestions */}
          <div className="mt-8">
            <p className="text-purple-200 text-center mb-4">Or try one of these vibes:</p>
            <div className="flex flex-wrap justify-center gap-3">
              {moodSuggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 text-purple-200 hover:text-white rounded-full border border-white/20 hover:border-white/40 transition-all duration-200 text-sm"
                  disabled={loading}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-4xl mx-auto mb-8">
            <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-red-200 text-center">
              {error}
            </div>
          </div>
        )}

        {/* Mood Interpretation */}
        {moodInterpretation && (
          <div className="max-w-4xl mx-auto mb-12">
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6">
              <h3 className="text-xl font-semibold text-white mb-3 flex items-center">
                <span className="w-6 h-6 bg-gradient-to-r from-pink-400 to-purple-400 rounded-full mr-3"></span>
                Poppy's Take on Your Vibe
              </h3>
              <p className="text-purple-200 text-lg leading-relaxed">{moodInterpretation}</p>
            </div>
          </div>
        )}

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="max-w-7xl mx-auto">
            <h3 className="text-3xl font-bold text-white mb-8 text-center">
              Perfect Matches for You 🎬
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {recommendations.map((rec, index) => (
                <div
                  key={rec.id}
                  className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl overflow-hidden hover:bg-white/15 transition-all duration-300 transform hover:scale-105 hover:shadow-2xl"
                >
                  {/* Poster/Backdrop */}
                  <div className="relative h-64 bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                    <div className="text-6xl">
                      {rec.type === 'movie' ? '🎬' : '📺'}
                    </div>
                    <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-full px-3 py-1">
                      <span className={`font-bold ${getRatingColor(rec.rating)}`}>
                        ⭐ {formatRating(rec.rating)}
                      </span>
                    </div>
                    <div className="absolute top-4 left-4 bg-purple-600/80 backdrop-blur-sm rounded-full px-3 py-1">
                      <span className="text-white text-sm font-medium capitalize">
                        {rec.type}
                      </span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-6">
                    <h4 className="text-xl font-bold text-white mb-2">{rec.title}</h4>
                    
                    {/* Genres */}
                    <div className="flex flex-wrap gap-2 mb-3">
                      {rec.genre.map((genre, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-purple-600/30 text-purple-200 rounded-full text-xs"
                        >
                          {genre}
                        </span>
                      ))}
                    </div>

                    {/* Overview */}
                    <p className="text-purple-200 text-sm mb-4 line-clamp-3">
                      {rec.overview}
                    </p>

                    {/* Recommendation Reason */}
                    <div className="bg-gradient-to-r from-pink-500/20 to-purple-500/20 rounded-lg p-3 mb-4">
                      <p className="text-pink-200 text-sm font-medium">
                        💡 {rec.recommendation_reason}
                      </p>
                    </div>

                    {/* Streaming Availability */}
                    {rec.streaming_availability && rec.streaming_availability.length > 0 && (
                      <div className="mb-4">
                        <p className="text-purple-300 text-sm font-medium mb-2">Watch on:</p>
                        <div className="flex flex-wrap gap-2">
                          {rec.streaming_availability.map((service, idx) => (
                            <span
                              key={idx}
                              className="px-3 py-1 bg-green-600/30 text-green-200 rounded-full text-xs border border-green-500/50"
                            >
                              {service.service}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex space-x-2">
                      {rec.trailer_url && (
                        <button className="flex-1 bg-red-600/20 hover:bg-red-600/30 text-red-200 border border-red-500/50 rounded-lg py-2 px-4 text-sm font-medium transition-colors duration-200">
                          🎥 Trailer
                        </button>
                      )}
                      <button className="flex-1 bg-blue-600/20 hover:bg-blue-600/30 text-blue-200 border border-blue-500/50 rounded-lg py-2 px-4 text-sm font-medium transition-colors duration-200">
                        ℹ️ Details
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {recommendations.length === 0 && !loading && (
          <div className="text-center py-20">
            <div className="text-8xl mb-6">🍿</div>
            <h3 className="text-2xl font-bold text-white mb-4">Ready to discover your next favorite?</h3>
            <p className="text-purple-200 text-lg max-w-2xl mx-auto">
              Share your mood, vibe, or what you're in the mood for above, and let Poppy's AI find the perfect entertainment matches for you.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-black/20 backdrop-blur-sm border-t border-white/10 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-purple-200">
              Powered by AI • Made with ❤️ for entertainment lovers
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;