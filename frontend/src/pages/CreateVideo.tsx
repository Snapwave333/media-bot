import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import api from '../services/api'
import { Upload, Music, FileText, Palette, Loader2, DollarSign } from 'lucide-react'
import toast from 'react-hot-toast'

const STYLE_PRESETS = [
  {
    id: 'abstract_vj',
    name: 'Abstract VJ',
    description: 'Generative patterns, particle systems, TouchDesigner aesthetics',
  },
  {
    id: 'cinematic_narrative',
    name: 'Cinematic',
    description: 'Story-driven visuals with dramatic lighting',
  },
  {
    id: 'retro_synthwave',
    name: 'Synthwave',
    description: '80s neon grids, retrowave, outrun aesthetics',
  },
  {
    id: 'organic_nature',
    name: 'Organic',
    description: 'Natural forms, fractals, flowing patterns',
  },
  {
    id: 'glitch_art',
    name: 'Glitch Art',
    description: 'Digital distortion, data moshing, cyberpunk',
  },
  {
    id: 'minimalist',
    name: 'Minimalist',
    description: 'Clean geometry, typography, negative space',
  },
]

export default function CreateVideo() {
  const navigate = useNavigate()
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [lyrics, setLyrics] = useState('')
  const [selectedStyle, setSelectedStyle] = useState('abstract_vj')
  const [uploading, setUploading] = useState(false)
  const [jobId, setJobId] = useState<number | null>(null)
  const [showPayment, setShowPayment] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      // Validate file type
      const validTypes = ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/x-m4a', 'audio/ogg']
      if (!validTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|flac|m4a|ogg)$/i)) {
        toast.error('Please upload a valid audio file (MP3, WAV, FLAC, M4A, OGG)')
        return
      }

      // Check file size (100MB max)
      if (file.size > 100 * 1024 * 1024) {
        toast.error('File too large. Maximum size is 100MB')
        return
      }

      setAudioFile(file)
      toast.success('Audio file ready!')
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
    },
    maxFiles: 1,
  })

  const handleUpload = async () => {
    if (!audioFile) {
      toast.error('Please select an audio file')
      return
    }

    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('audio_file', audioFile)
      if (lyrics) {
        formData.append('lyrics', lyrics)
      }
      formData.append('style_preset', selectedStyle)

      const response = await api.post('/videos/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setJobId(response.data.id)
      setShowPayment(true)
      toast.success('Upload successful! Proceed to payment.')
    } catch (error: unknown) {
      const axiosError = error as { response?: { data?: { detail?: string } } }
      toast.error(axiosError.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handlePaymentSuccess = async () => {
    if (!jobId) return

    try {
      // Start processing
      await api.post(`/videos/${jobId}/start`)
      toast.success('Video generation started!')
      navigate(`/video/${jobId}`)
    } catch (error) {
      toast.error('Failed to start processing')
    }
  }

  // Simple payment simulation for demo purposes
  const simulatePayment = () => {
    toast.loading('Processing payment...')
    setTimeout(() => {
      toast.dismiss()
      toast.success('Payment successful!')
      handlePaymentSuccess()
    }, 2000)
  }

  if (showPayment && jobId) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="card text-center">
          <DollarSign className="w-16 h-16 text-primary-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">Complete Payment</h1>
          <p className="text-gray-400 mb-6">Your video is ready to be generated</p>

          <div className="bg-gray-700/50 rounded-lg p-6 mb-6">
            <div className="text-3xl font-bold text-primary-400 mb-2">$50.00</div>
            <p className="text-gray-400">One-time payment for your music video</p>
          </div>

          <div className="space-y-4">
            <button onClick={simulatePayment} className="btn-primary w-full">
              Pay & Generate Video
            </button>

            <button
              onClick={() => setShowPayment(false)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              Go back
            </button>
          </div>

          <p className="text-xs text-gray-500 mt-4">
            In production, this would integrate with Stripe Checkout
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Create New Video</h1>

      <div className="space-y-8">
        {/* Audio Upload */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Upload className="w-6 h-6 mr-2 text-primary-500" />
            Upload Audio
          </h2>

          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive ? 'border-primary-500 bg-primary-500/10' : 'border-gray-600 hover:border-gray-500'}
              ${audioFile ? 'border-green-500 bg-green-500/10' : ''}`}
          >
            <input {...getInputProps()} />

            {audioFile ? (
              <div className="flex items-center justify-center space-x-3">
                <Music className="w-10 h-10 text-green-500" />
                <div className="text-left">
                  <p className="font-semibold">{audioFile.name}</p>
                  <p className="text-sm text-gray-400">
                    {(audioFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>
            ) : (
              <>
                <Upload className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-lg mb-2">
                  {isDragActive ? 'Drop your audio file here' : 'Drag & drop your audio file'}
                </p>
                <p className="text-gray-400">or click to browse</p>
                <p className="text-sm text-gray-500 mt-2">MP3, WAV, FLAC, M4A, OGG (max 100MB)</p>
              </>
            )}
          </div>
        </div>

        {/* Lyrics */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <FileText className="w-6 h-6 mr-2 text-accent-500" />
            Lyrics (Optional)
          </h2>
          <p className="text-gray-400 mb-4">
            Add lyrics for better mood analysis and visual generation
          </p>
          <textarea
            value={lyrics}
            onChange={(e) => setLyrics(e.target.value)}
            className="input-field min-h-[200px] font-mono"
            placeholder="Paste your lyrics here...

Example:
[Verse 1]
Walking through the city lights
Feeling like I own the night
Every beat drops just right
Stars are shining extra bright

[Chorus]
We're alive, we're alive tonight..."
          />
        </div>

        {/* Style Selection */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Palette className="w-6 h-6 mr-2 text-green-500" />
            Visual Style
          </h2>
          <p className="text-gray-400 mb-4">Choose the aesthetic for your music video</p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {STYLE_PRESETS.map((style) => (
              <button
                key={style.id}
                onClick={() => setSelectedStyle(style.id)}
                className={`p-4 rounded-lg border text-left transition-all
                  ${
                    selectedStyle === style.id
                      ? 'border-primary-500 bg-primary-500/10'
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
              >
                <h3 className="font-semibold mb-1">{style.name}</h3>
                <p className="text-sm text-gray-400">{style.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end">
          <button
            onClick={handleUpload}
            disabled={!audioFile || uploading}
            className="btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5 mr-2" />
                Upload & Continue to Payment
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
