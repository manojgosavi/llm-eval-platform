// frontend/src/components/NavBar.jsx

import { Link, useLocation } from 'react-router-dom'

const links = [
  { to: '/',     label: 'Dashboard' },
  { to: '/runs', label: 'Run History' },
  { to: '/settings', label: 'Settings' },
]

export default function NavBar() {
  const { pathname } = useLocation()

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="max-w-6xl mx-auto flex items-center gap-8">
        <span className="font-semibold text-gray-900 tracking-tight">
          LLM Eval Platform
        </span>
        <div className="flex gap-6">
          {links.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`text-sm font-medium transition-colors ${
                pathname === to
                  ? 'text-blue-600'
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}