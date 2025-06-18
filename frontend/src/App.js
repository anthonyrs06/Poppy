import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const App = () => {
  const [moodQuery, setMoodQuery] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [moodInterpretation, setMoodInterpretation] = useState('');
  const [error, setError] = useState('');
  const [expandedStreaming, setExpandedStreaming] = useState({});
  const [selectedDetails, setSelectedDetails] = useState(null);

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

  const handleDetailsClick = (recommendation) => {
    setSelectedDetails(recommendation);
  };

  const closeDetails = () => {
    setSelectedDetails(null);
  };

  // Handle ESC key to close modal
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && selectedDetails) {
        closeDetails();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [selectedDetails]);

  const handleTrailerClick = (trailerUrl, title) => {
    if (trailerUrl) {
      window.open(trailerUrl, '_blank');
    } else {
      // Fallback: search YouTube for trailer
      const searchQuery = encodeURIComponent(`${title} trailer`);
      window.open(`https://www.youtube.com/results?search_query=${searchQuery}`, '_blank');
    }
  };

  const toggleStreamingOptions = (recId) => {
    setExpandedStreaming(prev => ({
      ...prev,
      [recId]: !prev[recId]
    }));
  };

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
    <div className="min-h-screen bg-gradient-to-br from-red-900 via-amber-900 to-orange-900">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-sm border-b border-amber-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-red-600 to-amber-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xl">P</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">Poppy</h1>
                <p className="text-amber-200 text-sm">AI-Powered Entertainment Discovery</p>
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
            What's your <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-red-400">vibe</span> today?
          </h2>
          <p className="text-xl text-amber-200 mb-8 max-w-3xl mx-auto">
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
                className="w-full p-6 bg-black/20 backdrop-blur-sm border border-amber-500/30 rounded-2xl text-white placeholder-amber-300 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none h-32 text-lg"
                disabled={loading}
              />
            </div>
            
            <div className="flex justify-center">
              <button
                type="submit"
                disabled={loading || !moodQuery.trim()}
                className="px-12 py-4 bg-gradient-to-r from-red-600 to-amber-600 text-white font-semibold rounded-full hover:from-red-700 hover:to-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200 text-lg shadow-xl"
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
            <p className="text-amber-200 text-center mb-4">Or try one of these vibes:</p>
            <div className="flex flex-wrap justify-center gap-3">
              {moodSuggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="px-4 py-2 bg-black/20 hover:bg-black/30 text-amber-200 hover:text-white rounded-full border border-amber-500/30 hover:border-amber-400/60 transition-all duration-200 text-sm"
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
            <div className="bg-black/20 backdrop-blur-sm border border-amber-500/30 rounded-2xl p-6">
              <h3 className="text-xl font-semibold text-white mb-3 flex items-center">
                <span className="w-6 h-6 bg-gradient-to-r from-amber-400 to-red-400 rounded-full mr-3"></span>
                Poppy's Take on Your Vibe
              </h3>
              <p className="text-amber-200 text-lg leading-relaxed">{moodInterpretation}</p>
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
                  className="bg-black/20 backdrop-blur-sm border border-amber-500/30 rounded-2xl overflow-hidden hover:bg-black/30 transition-all duration-300 transform hover:scale-105 hover:shadow-2xl"
                >
                  {/* Poster/Backdrop */}
                  <div className="relative h-80 bg-gradient-to-br from-red-600 to-amber-600 overflow-hidden">
                    {rec.poster_url ? (
                      <img
                        src={rec.poster_url}
                        alt={rec.title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    
                    {/* Fallback icon - shows when no poster or image fails to load */}
                    <div 
                      className={`absolute inset-0 flex items-center justify-center ${rec.poster_url ? 'hidden' : 'flex'}`}
                      style={{display: rec.poster_url ? 'none' : 'flex'}}
                    >
                      <div className="text-8xl">
                        {rec.type === 'movie' ? '🎬' : '📺'}
                      </div>
                    </div>
                    
                    {/* Overlay with rating and type */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-black/30">
                      <div className="absolute top-4 right-4 bg-black/70 backdrop-blur-sm rounded-full px-3 py-1">
                        <span className={`font-bold ${getRatingColor(rec.rating)}`}>
                          ⭐ {formatRating(rec.rating)}
                        </span>
                      </div>
                      <div className="absolute top-4 left-4 bg-red-600/90 backdrop-blur-sm rounded-full px-3 py-1">
                        <span className="text-white text-sm font-medium capitalize">
                          {rec.type}
                        </span>
                      </div>
                      
                      {/* Trailer button overlay */}
                      {rec.trailer_url && (
                        <div className="absolute bottom-4 right-4">
                          <button
                            onClick={() => handleTrailerClick(rec.trailer_url, rec.title)}
                            className="bg-red-600/90 hover:bg-red-600 text-white rounded-full p-3 shadow-lg transform hover:scale-110 transition-all duration-200"
                            title="Watch Trailer"
                          >
                            <span className="text-xl">▶️</span>
                          </button>
                        </div>
                      )}
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
                          className="px-2 py-1 bg-red-600/30 text-amber-200 rounded-full text-xs"
                        >
                          {genre}
                        </span>
                      ))}
                    </div>


                    {/* Recommendation Reason */}
                    <div className="bg-gradient-to-r from-amber-600/20 to-red-600/20 rounded-lg p-3 mb-4">
                      <p className="text-amber-200 text-sm font-medium">
                        💡 {rec.recommendation_reason}
                      </p>
                    </div>

                    {/* Streaming Availability */}
                    {rec.streaming_availability && rec.streaming_availability.length > 0 && (
                      <div className="mb-4">
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-amber-300 text-sm font-medium flex items-center">
                            <span className="w-4 h-4 mr-2">📺</span>
                            Available on:
                          </p>
                          {rec.streaming_availability.length > 2 && (
                            <button
                              onClick={() => toggleStreamingOptions(rec.id)}
                              className="text-amber-400 hover:text-amber-300 text-xs underline"
                            >
                              {expandedStreaming[rec.id] ? 'Show less' : `+${rec.streaming_availability.length - 2} more`}
                            </button>
                          )}
                        </div>
                        <div className="space-y-2">
                          {(expandedStreaming[rec.id] ? rec.streaming_availability : rec.streaming_availability.slice(0, 2)).map((service, idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between p-2 bg-black/20 rounded-lg border border-amber-500/20 hover:bg-black/30 transition-colors duration-200"
                            >
                              <div className="flex items-center space-x-2">
                                <span className="text-green-400 font-medium text-sm">
                                  {service.service}
                                </span>
                                {service.quality && (
                                  <span className="px-2 py-1 bg-blue-600/30 text-blue-200 rounded text-xs">
                                    {service.quality}
                                  </span>
                                )}
                              </div>
                              <div className="flex items-center space-x-2">
                                {service.price && service.type === 'rent' && (
                                  <span className="text-yellow-300 text-xs font-medium">
                                    {service.price}
                                  </span>
                                )}
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  service.type === 'subscription' 
                                    ? 'bg-green-600/30 text-green-200 border border-green-500/50' 
                                    : service.type === 'rent'
                                    ? 'bg-yellow-600/30 text-yellow-200 border border-yellow-500/50'
                                    : service.type === 'buy'
                                    ? 'bg-orange-600/30 text-orange-200 border border-orange-500/50'
                                    : 'bg-purple-600/30 text-purple-200 border border-purple-500/50'
                                }`}>
                                  {service.type === 'subscription' ? 'Included' : 
                                   service.type === 'rent' ? 'Rent' : 
                                   service.type === 'buy' ? 'Buy' : service.type}
                                </span>
                                {service.link && (
                                  <button
                                    onClick={() => window.open(service.link, '_blank')}
                                    className="text-amber-400 hover:text-amber-300 text-xs"
                                  >
                                    →
                                  </button>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="space-y-3">
                      {/* Primary streaming action */}
                      {rec.streaming_availability && rec.streaming_availability.length > 0 && (
                        <div className="space-y-2">
                          {rec.streaming_availability.slice(0, 1).map((service, idx) => (
                            <button
                              key={idx}
                              onClick={() => service.link && window.open(service.link, '_blank')}
                              className="w-full bg-gradient-to-r from-green-600/20 to-green-500/20 hover:from-green-600/30 hover:to-green-500/30 text-green-200 border border-green-500/50 hover:border-green-400/70 rounded-lg py-3 px-4 font-medium transition-all duration-200 flex items-center justify-center space-x-2"
                            >
                              <span>▶️</span>
                              <span>
                                Watch on {service.service}
                                {service.type === 'rent' && service.price && ` (${service.price})`}
                                {service.type === 'subscription' && ' (Included)'}
                              </span>
                            </button>
                          ))}
                        </div>
                      )}
                      
                      {/* Secondary actions */}
                      <div className="flex space-x-2">
                        {rec.trailer_url && (
                          <button 
                            onClick={() => handleTrailerClick(rec.trailer_url, rec.title)}
                            className="flex-1 bg-red-600/20 hover:bg-red-600/30 text-red-200 border border-red-500/50 hover:border-red-400/70 rounded-lg py-2 px-4 text-sm font-medium transition-all duration-200 flex items-center justify-center space-x-1"
                          >
                            <span>🎥</span>
                            <span>Trailer</span>
                          </button>
                        )}
                        <button 
                          onClick={() => handleDetailsClick(rec)}
                          className="flex-1 bg-amber-600/20 hover:bg-amber-600/30 text-amber-200 border border-amber-500/50 hover:border-amber-400/70 rounded-lg py-2 px-4 text-sm font-medium transition-all duration-200 flex items-center justify-center space-x-1"
                        >
                          <span>ℹ️</span>
                          <span>Details</span>
                        </button>
                        <button className="flex-1 bg-red-600/20 hover:bg-red-600/30 text-red-200 border border-red-500/50 hover:border-red-400/70 rounded-lg py-2 px-4 text-sm font-medium transition-all duration-200 flex items-center justify-center space-x-1">
                          <span>💾</span>
                          <span>Save</span>
                        </button>
                      </div>
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

        {/* Details Modal */}
        {selectedDetails && (
          <div 
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 modal-backdrop"
            onClick={(e) => {
              // Close modal if clicking the backdrop
              if (e.target === e.currentTarget) {
                closeDetails();
              }
            }}
          >
            <div className="bg-gradient-to-br from-red-900/95 to-amber-900/95 backdrop-blur-md border border-amber-500/30 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto modal-content">
              {/* Modal Header */}
              <div className="flex items-center justify-between p-6 border-b border-white/10">
                <h3 className="text-2xl font-bold text-white">{selectedDetails.title}</h3>
                <button
                  onClick={closeDetails}
                  className="text-purple-300 hover:text-white transition-colors duration-200 text-2xl"
                >
                  ✕
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-6 space-y-6">
                {/* Poster and Basic Info */}
                <div className="flex flex-col md:flex-row gap-6">
                  {/* Poster */}
                  <div className="flex-shrink-0">
                    <div className="w-48 h-72 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg overflow-hidden">
                      {selectedDetails.poster_url ? (
                        <img
                          src={selectedDetails.poster_url}
                          alt={selectedDetails.title}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-6xl">
                          {selectedDetails.type === 'movie' ? '🎬' : '📺'}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Basic Info */}
                  <div className="flex-1 space-y-4">
                    {/* Type and Rating */}
                    <div className="flex items-center gap-4">
                      <span className="px-3 py-1 bg-purple-600/30 text-purple-200 rounded-full text-sm font-medium capitalize">
                        {selectedDetails.type}
                      </span>
                      <span className={`font-bold text-lg ${getRatingColor(selectedDetails.rating)}`}>
                        ⭐ {formatRating(selectedDetails.rating)}
                      </span>
                    </div>

                    {/* Genres */}
                    <div>
                      <h4 className="text-purple-300 text-sm font-medium mb-2">Genres</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedDetails.genre.map((genre, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-purple-600/30 text-purple-200 rounded-full text-sm"
                          >
                            {genre}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Why We Recommended It */}
                    <div>
                      <h4 className="text-purple-300 text-sm font-medium mb-2">Why We Recommended This</h4>
                      <div className="bg-gradient-to-r from-pink-500/20 to-purple-500/20 rounded-lg p-3">
                        <p className="text-pink-200 text-sm">
                          💡 {selectedDetails.recommendation_reason}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Description */}
                <div>
                  <h4 className="text-purple-300 text-sm font-medium mb-3">Description</h4>
                  <p className="text-purple-100 text-base leading-relaxed">
                    {selectedDetails.overview}
                  </p>
                </div>

                {/* Streaming Availability */}
                {selectedDetails.streaming_availability && selectedDetails.streaming_availability.length > 0 && (
                  <div>
                    <h4 className="text-purple-300 text-sm font-medium mb-3 flex items-center">
                      <span className="w-4 h-4 mr-2">📺</span>
                      Where to Watch
                    </h4>
                    <div className="space-y-3">
                      {selectedDetails.streaming_availability.map((service, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors duration-200"
                        >
                          <div className="flex items-center space-x-3">
                            <span className="text-green-400 font-medium">
                              {service.service}
                            </span>
                            {service.quality && (
                              <span className="px-2 py-1 bg-blue-600/30 text-blue-200 rounded text-xs">
                                {service.quality}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center space-x-3">
                            {service.price && service.type === 'rent' && (
                              <span className="text-yellow-300 text-sm font-medium">
                                {service.price}
                              </span>
                            )}
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                              service.type === 'subscription' 
                                ? 'bg-green-600/30 text-green-200 border border-green-500/50' 
                                : service.type === 'rent'
                                ? 'bg-yellow-600/30 text-yellow-200 border border-yellow-500/50'
                                : service.type === 'buy'
                                ? 'bg-orange-600/30 text-orange-200 border border-orange-500/50'
                                : 'bg-purple-600/30 text-purple-200 border border-purple-500/50'
                            }`}>
                              {service.type === 'subscription' ? 'Included' : 
                               service.type === 'rent' ? 'Rent' : 
                               service.type === 'buy' ? 'Buy' : service.type}
                            </span>
                            {service.link && (
                              <button
                                onClick={() => window.open(service.link, '_blank')}
                                className="bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 px-3 py-1 rounded text-sm transition-colors duration-200"
                              >
                                Watch
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4 border-t border-white/10">
                  {selectedDetails.trailer_url && (
                    <button
                      onClick={() => handleTrailerClick(selectedDetails.trailer_url, selectedDetails.title)}
                      className="flex-1 bg-red-600/20 hover:bg-red-600/30 text-red-200 border border-red-500/50 hover:border-red-400/70 rounded-lg py-3 px-4 font-medium transition-all duration-200 flex items-center justify-center space-x-2"
                    >
                      <span>🎥</span>
                      <span>Watch Trailer</span>
                    </button>
                  )}
                  <button className="flex-1 bg-purple-600/20 hover:bg-purple-600/30 text-purple-200 border border-purple-500/50 hover:border-purple-400/70 rounded-lg py-3 px-4 font-medium transition-all duration-200 flex items-center justify-center space-x-2">
                    <span>💾</span>
                    <span>Save to List</span>
                  </button>
                </div>
              </div>
            </div>
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