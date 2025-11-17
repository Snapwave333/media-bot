import { Link } from 'react-router-dom'
import { Music, Zap, Palette, DollarSign, Play, ArrowRight } from 'lucide-react'

export default function Landing() {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-900/50 to-accent-900/50"></div>
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <Music className="w-16 h-16 text-primary-500 animate-pulse-slow" />
            </div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="gradient-text">AI Music Video</span>
              <br />
              Generator
            </h1>

            <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto mb-8">
              Transform your music into stunning visual experiences. Professional music videos for
              independent artists—no $5,000 budget required.
            </p>

            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
              <Link to="/register" className="btn-primary text-lg flex items-center justify-center">
                Get Started
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <Link to="/login" className="btn-secondary text-lg">
                Sign In
              </Link>
            </div>

            <div className="inline-block bg-gray-800/50 backdrop-blur-sm rounded-full px-6 py-3 border border-gray-700">
              <span className="text-2xl font-bold text-primary-400">$50</span>
              <span className="text-gray-300 ml-2">per video</span>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-gray-800 py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-16">
            How It <span className="gradient-text">Works</span>
          </h2>

          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-gray-700 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary-400">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Upload</h3>
              <p className="text-gray-400">Upload your MP3 and optional lyrics</p>
            </div>

            <div className="text-center">
              <div className="bg-gray-700 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary-400">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Analyze</h3>
              <p className="text-gray-400">AI detects beat, tempo, mood, and structure</p>
            </div>

            <div className="text-center">
              <div className="bg-gray-700 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary-400">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Generate</h3>
              <p className="text-gray-400">AI creates stunning visual clips</p>
            </div>

            <div className="text-center">
              <div className="bg-gray-700 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary-400">4</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Edit</h3>
              <p className="text-gray-400">Auto-edit synced to your beat</p>
            </div>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-16">
            Powerful <span className="gradient-text">Features</span>
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="card hover:border-primary-500 transition-colors">
              <Zap className="w-12 h-12 text-primary-500 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Beat Detection</h3>
              <p className="text-gray-400">
                Advanced AI using librosa analyzes your track's tempo, beats, and rhythm patterns
                for perfect sync.
              </p>
            </div>

            <div className="card hover:border-primary-500 transition-colors">
              <Palette className="w-12 h-12 text-accent-500 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Mood Analysis</h3>
              <p className="text-gray-400">
                AI interprets your lyrics and audio to understand emotional tone and generate
                matching visuals.
              </p>
            </div>

            <div className="card hover:border-primary-500 transition-colors">
              <Play className="w-12 h-12 text-green-500 mb-4" />
              <h3 className="text-xl font-semibold mb-2">VJ Aesthetics</h3>
              <p className="text-gray-400">
                TouchDesigner-inspired generative visuals, abstract patterns, and professional
                effects.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Style Presets */}
      <div className="bg-gray-800 py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-16">
            Visual <span className="gradient-text">Styles</span>
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                name: 'Abstract VJ',
                desc: 'Generative patterns & particle systems',
              },
              {
                name: 'Cinematic',
                desc: 'Narrative storytelling visuals',
              },
              {
                name: 'Synthwave',
                desc: '80s neon retrowave aesthetics',
              },
              {
                name: 'Organic',
                desc: 'Nature & fractal patterns',
              },
              {
                name: 'Glitch Art',
                desc: 'Digital distortion & cyberpunk',
              },
              {
                name: 'Minimalist',
                desc: 'Clean geometric typography',
              },
            ].map((style) => (
              <div
                key={style.name}
                className="bg-gray-700/50 rounded-lg p-6 border border-gray-600 hover:border-primary-500 transition-colors"
              >
                <h3 className="text-lg font-semibold mb-1">{style.name}</h3>
                <p className="text-gray-400 text-sm">{style.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Pricing */}
      <div className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-16">
            Simple <span className="gradient-text">Pricing</span>
          </h2>

          <div className="max-w-md mx-auto">
            <div className="card text-center border-2 border-primary-500">
              <DollarSign className="w-16 h-16 text-primary-500 mx-auto mb-4" />
              <h3 className="text-3xl font-bold mb-2">$50</h3>
              <p className="text-gray-400 mb-6">per music video</p>

              <ul className="text-left space-y-3 mb-8">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  Full HD 1080p output
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  Beat-synced editing
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  AI mood analysis
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  Multiple style presets
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  Download & own forever
                </li>
              </ul>

              <Link to="/register" className="btn-primary w-full block">
                Start Creating
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="bg-gradient-to-r from-primary-900 to-accent-900 py-16">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-3xl font-bold mb-4">Ready to bring your music to life?</h2>
          <p className="text-xl text-gray-300 mb-8">
            Join independent musicians creating professional videos with AI.
          </p>
          <Link to="/register" className="btn-primary text-lg inline-flex items-center">
            Create Your First Video
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-400">
          <p>&copy; 2024 AI Music Video Generator. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
