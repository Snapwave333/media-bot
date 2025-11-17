import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import {
  Loader2,
  Download,
  Trash2,
  CheckCircle,
  XCircle,
  Music,
  Clock,
  Zap,
  Palette,
} from 'lucide-react'
import toast from 'react-hot-toast'

interface VideoJob {
  id: number
  status: string
  created_at: string
  updated_at: string
  tempo: number | null
  key: string | null
  duration: number | null
  sections: unknown[] | null
  mood_analysis: Record<string, unknown> | null
  output_video_path: string | null
  thumbnail_path: string | null
  error_message: string | null
  style_preset: string
}

export default function VideoDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [job, setJob] = useState<VideoJob | null>(null)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    fetchJob()

    // Poll for updates if job is processing
    const interval = setInterval(() => {
      if (
        job &&
        ['analyzing', 'generating', 'editing'].includes(job.status)
      ) {
        fetchJob()
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [id, job?.status])

  const fetchJob = async () => {
    try {
      const response = await api.get(`/videos/${id}`)
      setJob(response.data)
    } catch (error) {
      toast.error('Failed to load video details')
      navigate('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (!job) return
    window.open(`/api/v1/videos/${job.id}/download`, '_blank')
    toast.success('Download started!')
  }

  const handleDelete = async () => {
    if (!job || !confirm('Are you sure you want to delete this video?')) return

    setDeleting(true)
    try {
      await api.delete(`/videos/${job.id}`)
      toast.success('Video deleted')
      navigate('/dashboard')
    } catch (error) {
      toast.error('Failed to delete video')
    } finally {
      setDeleting(false)
    }
  }

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return '-'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'pending':
        return { icon: Clock, color: 'text-yellow-500', text: 'Pending' }
      case 'analyzing':
        return { icon: Zap, color: 'text-blue-500', text: 'Analyzing Audio' }
      case 'generating':
        return { icon: Palette, color: 'text-purple-500', text: 'Generating Visuals' }
      case 'editing':
        return { icon: Music, color: 'text-primary-500', text: 'Editing Video' }
      case 'completed':
        return { icon: CheckCircle, color: 'text-green-500', text: 'Completed' }
      case 'failed':
        return { icon: XCircle, color: 'text-red-500', text: 'Failed' }
      default:
        return { icon: Clock, color: 'text-gray-500', text: status }
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-10 h-10 text-primary-500 animate-spin" />
      </div>
    )
  }

  if (!job) {
    return <div>Job not found</div>
  }

  const statusInfo = getStatusInfo(job.status)
  const StatusIcon = statusInfo.icon

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Video #{job.id}</h1>
          <div className="flex items-center space-x-2">
            <StatusIcon className={`w-5 h-5 ${statusInfo.color}`} />
            <span className={statusInfo.color}>{statusInfo.text}</span>
          </div>
        </div>

        <div className="flex space-x-3">
          {job.status === 'completed' && (
            <button onClick={handleDownload} className="btn-primary flex items-center">
              <Download className="w-5 h-5 mr-2" />
              Download
            </button>
          )}
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="btn-secondary flex items-center text-red-400 hover:text-red-300"
          >
            {deleting ? (
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
            ) : (
              <Trash2 className="w-5 h-5 mr-2" />
            )}
            Delete
          </button>
        </div>
      </div>

      {/* Processing Status */}
      {['analyzing', 'generating', 'editing'].includes(job.status) && (
        <div className="card mb-8 border-primary-500">
          <div className="flex items-center space-x-4">
            <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
            <div>
              <h2 className="text-xl font-semibold">{statusInfo.text}</h2>
              <p className="text-gray-400">This may take 10-30 minutes depending on song length</p>
            </div>
          </div>

          <div className="mt-6">
            <div className="flex justify-between text-sm mb-2">
              <span>Progress</span>
              <span>
                {job.status === 'analyzing' ? '25%' : job.status === 'generating' ? '50%' : '75%'}
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-primary-500 to-accent-500 h-2 rounded-full transition-all duration-500"
                style={{
                  width:
                    job.status === 'analyzing'
                      ? '25%'
                      : job.status === 'generating'
                        ? '50%'
                        : '75%',
                }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {job.status === 'failed' && job.error_message && (
        <div className="card mb-8 border-red-500 bg-red-500/10">
          <h2 className="text-xl font-semibold text-red-400 mb-2">Error</h2>
          <p className="text-gray-300">{job.error_message}</p>
        </div>
      )}

      {/* Video Preview */}
      {job.status === 'completed' && job.output_video_path && (
        <div className="card mb-8">
          <h2 className="text-xl font-semibold mb-4">Preview</h2>
          <video
            controls
            className="w-full rounded-lg bg-gray-900"
            poster={job.thumbnail_path ? `/api/v1/videos/${job.id}/thumbnail` : undefined}
          >
            <source src={`/api/v1/videos/${job.id}/download`} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      )}

      {/* Audio Analysis */}
      {job.tempo && (
        <div className="card mb-8">
          <h2 className="text-xl font-semibold mb-4">Audio Analysis</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <p className="text-gray-400 text-sm mb-1">Tempo</p>
              <p className="text-2xl font-bold text-primary-400">{Math.round(job.tempo)} BPM</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm mb-1">Key</p>
              <p className="text-2xl font-bold text-accent-400">{job.key || '-'}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm mb-1">Duration</p>
              <p className="text-2xl font-bold">{formatDuration(job.duration)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Mood Analysis */}
      {job.mood_analysis && (
        <div className="card mb-8">
          <h2 className="text-xl font-semibold mb-4">Mood Analysis</h2>
          <div className="space-y-4">
            {job.mood_analysis.overall_mood && (
              <div>
                <p className="text-gray-400 text-sm mb-1">Overall Mood</p>
                <p className="text-lg font-semibold capitalize">
                  {String(job.mood_analysis.overall_mood)}
                </p>
              </div>
            )}

            {job.mood_analysis.descriptors && Array.isArray(job.mood_analysis.descriptors) && (
              <div>
                <p className="text-gray-400 text-sm mb-2">Descriptors</p>
                <div className="flex flex-wrap gap-2">
                  {(job.mood_analysis.descriptors as string[]).map((desc: string, i: number) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-gray-700 rounded-full text-sm capitalize"
                    >
                      {desc}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {job.mood_analysis.energy !== undefined && (
              <div>
                <p className="text-gray-400 text-sm mb-2">Energy Level</p>
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-green-500 to-red-500 h-3 rounded-full"
                    style={{ width: `${Number(job.mood_analysis.energy) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Sections */}
      {job.sections && job.sections.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Song Sections</h2>
          <div className="space-y-3">
            {job.sections.map((section: unknown, i: number) => {
              const sec = section as Record<string, unknown>
              return (
                <div key={i} className="flex justify-between items-center p-3 bg-gray-700/50 rounded">
                  <div>
                    <span className="font-semibold capitalize">{String(sec.type || 'Section')}</span>
                    <span className="text-gray-400 ml-2">
                      {formatDuration(sec.start_time as number)} -{' '}
                      {formatDuration(sec.end_time as number)}
                    </span>
                  </div>
                  {sec.mood && (
                    <span className="text-sm text-primary-400">
                      Energy: {Math.round(((sec.mood as Record<string, number>).energy || 0) * 100)}%
                    </span>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
