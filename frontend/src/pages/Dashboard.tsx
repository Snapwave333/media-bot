import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { PlusCircle, Clock, CheckCircle, XCircle, Loader2, Music } from 'lucide-react'
import toast from 'react-hot-toast'

interface VideoJob {
  id: number
  status: string
  created_at: string
  style_preset: string
  duration: number | null
  thumbnail_path: string | null
}

export default function Dashboard() {
  const [jobs, setJobs] = useState<VideoJob[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchJobs()
  }, [])

  const fetchJobs = async () => {
    try {
      const response = await api.get('/videos/')
      setJobs(response.data)
    } catch (error) {
      toast.error('Failed to load videos')
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />
      default:
        return <Loader2 className="w-5 h-5 text-primary-500 animate-spin" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Pending'
      case 'analyzing':
        return 'Analyzing Audio'
      case 'generating':
        return 'Generating Visuals'
      case 'editing':
        return 'Editing Video'
      case 'completed':
        return 'Completed'
      case 'failed':
        return 'Failed'
      default:
        return status
    }
  }

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return '-'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-10 h-10 text-primary-500 animate-spin" />
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Your Videos</h1>
        <Link to="/create" className="btn-primary flex items-center">
          <PlusCircle className="w-5 h-5 mr-2" />
          Create New Video
        </Link>
      </div>

      {jobs.length === 0 ? (
        <div className="card text-center py-16">
          <Music className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No videos yet</h2>
          <p className="text-gray-400 mb-6">Create your first AI-powered music video</p>
          <Link to="/create" className="btn-primary inline-flex items-center">
            <PlusCircle className="w-5 h-5 mr-2" />
            Create Video
          </Link>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <Link
              key={job.id}
              to={`/video/${job.id}`}
              className="card hover:border-primary-500 transition-all duration-200 group"
            >
              {/* Thumbnail */}
              <div className="bg-gray-700 rounded-lg h-40 mb-4 overflow-hidden">
                {job.thumbnail_path ? (
                  <img
                    src={`/api/v1/videos/${job.id}/thumbnail`}
                    alt="Video thumbnail"
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Music className="w-12 h-12 text-gray-500" />
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-semibold text-lg">Video #{job.id}</h3>
                  <p className="text-sm text-gray-400">{job.style_preset.replace('_', ' ')}</p>
                </div>
                <div className="flex items-center space-x-1">
                  {getStatusIcon(job.status)}
                  <span className="text-sm">{getStatusText(job.status)}</span>
                </div>
              </div>

              <div className="flex justify-between text-sm text-gray-400">
                <span>Duration: {formatDuration(job.duration)}</span>
                <span>{formatDate(job.created_at)}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
