import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Music, LogOut, Home, PlusCircle } from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/dashboard" className="flex items-center space-x-2">
              <Music className="w-8 h-8 text-primary-500" />
              <span className="text-xl font-bold gradient-text">AI Music Video</span>
            </Link>

            {/* Navigation */}
            <nav className="flex items-center space-x-4">
              <Link
                to="/dashboard"
                className="flex items-center space-x-1 text-gray-300 hover:text-white transition-colors"
              >
                <Home className="w-5 h-5" />
                <span>Dashboard</span>
              </Link>

              <Link
                to="/create"
                className="flex items-center space-x-1 text-gray-300 hover:text-white transition-colors"
              >
                <PlusCircle className="w-5 h-5" />
                <span>Create</span>
              </Link>

              <div className="flex items-center space-x-4 ml-4 pl-4 border-l border-gray-700">
                <span className="text-gray-400 text-sm">{user?.email}</span>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-gray-300 hover:text-red-400 transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                  <span>Logout</span>
                </button>
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">{children}</main>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-400 text-sm">
            <p>&copy; 2024 AI Music Video Generator. All rights reserved.</p>
            <p className="mt-1">Professional music videos for independent artists.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
