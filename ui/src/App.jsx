import React, { useState } from "react";
import { Search, Music, Heart, Sparkles, Gauge, BarChart3, Activity } from "lucide-react";

export default function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTitleClick = () => {
    setQuery("");
    setResults([]);
    setError(null);
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/search?query=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResults(data.results || []);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch results. Try again.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter") handleSearch();
  };

  return (
    <div className="min-h-screen bg-purple-50 flex flex-col pb-15" style={{ fontFamily: 'monospace' }}>
      {/* Soft lavender background pattern */}
      <div className="fixed inset-0 opacity-10 pointer-events-none">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            radial-gradient(circle at 2px 2px, #c084fc 2px, transparent 0),
            radial-gradient(circle at 6px 6px, #a855f7 1px, transparent 0)
          `,
          backgroundSize: '8px 8px'
        }}></div>
      </div>

      {/* Main Content Container */}
      <div className={`flex flex-col items-center px-6 ${results.length > 0 ? 'pt-8 pb-4' : 'flex-1 justify-center'}`}>
        {/* Header */}
        <div className="relative mb-4 text-center">
          <div 
            className="inline-flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
            onClick={handleTitleClick}
          >
            <div className="p-3 bg-purple-200 border-4 border-purple-300" style={{ 
              clipPath: 'polygon(0 0, 100% 0, 100% 80%, 80% 100%, 0 100%)'
            }}>
              <Music className="h-8 w-8 text-purple-400" style={{ filter: 'drop-shadow(2px 2px 0px #9333ea)' }} />
            </div>
            <h1 className="text-4xl text-purple-400 tracking-wide" 
                style={{ 
                  fontFamily: "'Poppins', sans-serif",
                  fontWeight:"bold"
                }}>
              Lyrically
            </h1>
            <Sparkles className="h-5 w-5 text-purple-400 animate-bounce" />
          </div>
        </div>

        {/* Search */}
        <div className="w-full max-w-3xl mb-6">
          <div className="relative">
            <div className="bg-white border-4 border-purple-300 shadow-lg">
              <div className="flex">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={onKeyDown}
                  placeholder="Say something... we'll find the song that says it too."
                  className="flex-1 p-4 bg-white text-purple-500 font-mono text-lg focus:outline-none placeholder-purple-300"
                />
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="bg-purple-200 text-purple-500 px-8 font-bold text-lg border-l-4 border-purple-300 hover:bg-purple-100 disabled:opacity-50 transition-colors"
                  style={{ 
                    fontFamily: "'Jost', sans-serif"
                  }}
                >
                  {loading ? (
                    <div className="h-6 w-6 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    "GO!"
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="w-full max-w-2xl mb-4">
            <div className="bg-red-50 border-4 border-red-300 p-6 text-center" style={{
              boxShadow: '6px 6px 0px #dc2626'
            }}>
              <p className="text-red-700 font-bold text-lg">⚠️ {error}</p>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="w-full px-6 pb-6">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-3 gap-6">
              {results.map((r, idx) => (
                <div
                  key={idx}
                  className="bg-white border-4 border-purple-300 hover:border-purple-400 transition-all duration-200 overflow-hidden group hover:-translate-y-1 hover:shadow-xl"
                  style={{ 
                    zIndex: 1,
                    // boxShadow: '6px 6px 0px #c084fc'
                   }}
                >
                  {/* Image or Music Note */}
                  <div className="relative bg-purple-50 border-b-4 border-purple-300 h-56 flex items-center justify-center overflow-hidden">
                    {r.image ? (
                      <>
                        <img
                          src={r.image}
                          alt={r.title || 'Song artwork'}
                          className="w-full h-full object-cover object-center scale-105"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.parentElement.querySelector('.fallback-icon').style.display = 'flex';
                          }}
                        />
                        {/* Purple tint overlay */}
                        <div className="absolute inset-0 bg-purple-500 bg-opacity-30 mix-blend-multiply"></div>
                      </>
                    ) : null}
                    <div className="fallback-icon absolute inset-0 flex items-center justify-center bg-purple-100" style={{ display: r.image ? 'none' : 'flex' }}>
                      <Music className="h-16 w-16 text-purple-400" />
                    </div>
                    <div className="absolute top-3 right-3 bg-white bg-opacity-90 border-2 border-purple-300 px-2 py-1 rounded-sm backdrop-blur-sm">
                      <div className="flex items-center gap-1">
                        <Gauge className="h-3 w-3 text-purple-500" />
                        <span className="text-xs font-bold text-purple-800">
                          {r.score?.toFixed(1) || 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-white">
                    <h2 className="font-semibold text-gray-700 text-base mb-2 group-hover:text-gray-800 transition-colors min-h-[1rem] flex items-start">
                      <span className="line-clamp-2">{r.title || 'Unknown Title'}</span>
                    </h2>
                    <p className="text-purple-600 text-sm font-bold mb-3 line-clamp-1 min-h-[1.25rem]">{r.artist || 'Unknown Artist'}</p>
                    
                    <div className="bg-purple-50 border-l-4 border-purple-300 p-3">
                      <p className="text-purple-700 text-xs leading-relaxed font-semibold line-clamp-3 min-h-[2rem]">
                        "{r.lyric || 'No lyric preview available'}"
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Aesthetic tagline in bottom right corner - positioned to not overlay results */}
      <div className="fixed bottom-6 right-6 z-10 bg-white bg-opacity-90 px-3 py-2 border-2 border-purple-300 rounded-lg shadow-lg">
        <p className="text-purple-500 font-semibold text-sm italic" >
          Say it with music 🎵
        </p>
      </div>
    </div>
  );
}