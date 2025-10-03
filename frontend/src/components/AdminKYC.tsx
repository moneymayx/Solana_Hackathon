'use client'

import { useState, useEffect } from 'react'
import { Users, Shield, CheckCircle, XCircle, Clock, AlertTriangle, Download } from 'lucide-react'

interface KYCStatistics {
  total_users: number
  kyc_status_breakdown: {
    pending: number
    verified: number
    rejected: number
    expired: number
    under_review: number
  }
  provider_breakdown: {
    moonpay: number
    manual: number
    stripe: number
  }
  verification_rate: number
}

interface PendingUser {
  user_id: number
  email: string
  wallet_address: string
  full_name: string
  kyc_status: string
  kyc_provider: string
  created_at: string
  last_active: string
}

interface ComplianceReport {
  report_date: string
  total_users: number
  kyc_verification_rate: number
  kyc_status_breakdown: any
  provider_breakdown: any
  recent_verifications: number
  compliance_metrics: any
}

export default function AdminKYC() {
  const [statistics, setStatistics] = useState<KYCStatistics | null>(null)
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([])
  const [complianceReport, setComplianceReport] = useState<ComplianceReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedUser, setSelectedUser] = useState<PendingUser | null>(null)
  const [newStatus, setNewStatus] = useState('')
  const [adminNotes, setAdminNotes] = useState('')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load statistics
      const statsResponse = await fetch('/api/admin/kyc/statistics')
      const statsData = await statsResponse.json()
      if (statsData.success) {
        setStatistics(statsData.statistics)
      }

      // Load pending users
      const pendingResponse = await fetch('/api/admin/kyc/pending')
      const pendingData = await pendingResponse.json()
      if (pendingData.success) {
        setPendingUsers(pendingData.pending_users)
      }

      // Load compliance report
      const reportResponse = await fetch('/api/admin/compliance/report')
      const reportData = await reportResponse.json()
      if (reportData.success) {
        setComplianceReport(reportData.compliance_report)
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateKYCStatus = async (userId: number, status: string, notes: string) => {
    try {
      const response = await fetch('/api/admin/kyc/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          new_status: status,
          admin_notes: notes
        })
      })

      const result = await response.json()
      if (result.success) {
        // Reload data
        loadDashboardData()
        setSelectedUser(null)
        setNewStatus('')
        setAdminNotes('')
        alert('KYC status updated successfully')
      } else {
        alert('Failed to update KYC status: ' + result.error)
      }
    } catch (error) {
      console.error('Failed to update KYC status:', error)
      alert('Failed to update KYC status')
    }
  }

  const downloadComplianceReport = () => {
    if (!complianceReport) return

    const reportData = {
      ...complianceReport,
      generated_at: new Date().toISOString()
    }

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `compliance-report-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'verified':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />
      case 'under_review':
        return <AlertTriangle className="h-5 w-5 text-blue-500" />
      default:
        return <Shield className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified':
        return 'bg-green-100 text-green-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'under_review':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">KYC Management Dashboard</h1>
        <p className="text-purple-100">Monitor and manage user verification status</p>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.total_users}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Verified</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.kyc_status_breakdown.verified}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-yellow-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.kyc_status_breakdown.pending}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Verification Rate</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.verification_rate.toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Pending Reviews */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Pending KYC Reviews</h2>
          <p className="text-sm text-gray-600">Users requiring manual verification review</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Provider
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {pendingUsers.map((user) => (
                <tr key={user.user_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {user.full_name || 'No name provided'}
                      </div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                      <div className="text-xs text-gray-400">{user.wallet_address}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(user.kyc_status)}`}>
                      {getStatusIcon(user.kyc_status)}
                      <span className="ml-1">{user.kyc_status}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.kyc_provider || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => setSelectedUser(user)}
                      className="text-purple-600 hover:text-purple-900"
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Compliance Report */}
      {complianceReport && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Compliance Report</h2>
              <p className="text-sm text-gray-600">Generated on {new Date(complianceReport.report_date).toLocaleDateString()}</p>
            </div>
            <button
              onClick={downloadComplianceReport}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700"
            >
              <Download className="h-4 w-4 mr-2" />
              Download Report
            </button>
          </div>
          
          <div className="px-6 py-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">{complianceReport.total_users}</p>
                <p className="text-sm text-gray-600">Total Users</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{complianceReport.kyc_verification_rate.toFixed(1)}%</p>
                <p className="text-sm text-gray-600">Verification Rate</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">{complianceReport.recent_verifications}</p>
                <p className="text-sm text-gray-600">Recent Verifications</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* KYC Status Update Modal */}
      {selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Update KYC Status</h3>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">User: {selectedUser.email}</p>
              <p className="text-sm text-gray-600">Current Status: {selectedUser.kyc_status}</p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Status
              </label>
              <select
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Select status</option>
                <option value="verified">Verified</option>
                <option value="rejected">Rejected</option>
                <option value="under_review">Under Review</option>
                <option value="expired">Expired</option>
              </select>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Admin Notes (Optional)
              </label>
              <textarea
                value={adminNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Add notes about this verification decision..."
              />
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setSelectedUser(null)
                  setNewStatus('')
                  setAdminNotes('')
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={() => updateKYCStatus(selectedUser.user_id, newStatus, adminNotes)}
                disabled={!newStatus}
                className="px-4 py-2 text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 rounded-md"
              >
                Update Status
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
