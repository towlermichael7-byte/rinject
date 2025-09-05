'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Plus, Edit, Trash2, Target } from 'lucide-react'
import { generateInterviewId } from '@/lib/utils'

interface Requirement {
  id: string
  jobTitle: string
  client: string
  primeVendor?: string
  status: 'APPLIED' | 'NO_RESPONSE' | 'SUBMITTED' | 'ON_HOLD' | 'INTERVIEWED'
  nextSteps?: string
  vendorInfo?: {
    name: string
    company: string
    phone: string
    email: string
  }
  consultants: string[]
  interviewId?: string
  createdAt: string
  updatedAt: string
}

const statusColors = {
  APPLIED: 'bg-blue-100 text-blue-800',
  NO_RESPONSE: 'bg-gray-100 text-gray-800',
  SUBMITTED: 'bg-yellow-100 text-yellow-800',
  ON_HOLD: 'bg-orange-100 text-orange-800',
  INTERVIEWED: 'bg-green-100 text-green-800'
}

const statusEmojis = {
  APPLIED: '📝',
  NO_RESPONSE: '⏳',
  SUBMITTED: '📤',
  ON_HOLD: '⏸️',
  INTERVIEWED: '✅'
}

export function RequirementsManager() {
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    jobTitle: '',
    client: '',
    primeVendor: '',
    status: 'APPLIED' as const,
    nextSteps: '',
    vendorInfo: {
      name: '',
      company: '',
      phone: '',
      email: ''
    },
    consultants: ['Raju', 'Eric'],
    interviewId: ''
  })

  useEffect(() => {
    fetchRequirements()
  }, [])

  const fetchRequirements = async () => {
    try {
      const response = await fetch('/api/requirements')
      const data = await response.json()
      setRequirements(data)
    } catch (error) {
      console.error('Failed to fetch requirements:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const url = editingId ? `/api/requirements/${editingId}` : '/api/requirements'
      const method = editingId ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        await fetchRequirements()
        resetForm()
      }
    } catch (error) {
      console.error('Failed to save requirement:', error)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this requirement?')) return

    try {
      await fetch(`/api/requirements/${id}`, { method: 'DELETE' })
      await fetchRequirements()
    } catch (error) {
      console.error('Failed to delete requirement:', error)
    }
  }

  const handleEdit = (requirement: Requirement) => {
    setFormData({
      jobTitle: requirement.jobTitle,
      client: requirement.client,
      primeVendor: requirement.primeVendor || '',
      status: requirement.status,
      nextSteps: requirement.nextSteps || '',
      vendorInfo: requirement.vendorInfo || {
        name: '',
        company: '',
        phone: '',
        email: ''
      },
      consultants: requirement.consultants,
      interviewId: requirement.interviewId || ''
    })
    setEditingId(requirement.id)
    setIsCreating(true)
  }

  const resetForm = () => {
    setFormData({
      jobTitle: '',
      client: '',
      primeVendor: '',
      status: 'APPLIED',
      nextSteps: '',
      vendorInfo: {
        name: '',
        company: '',
        phone: '',
        email: ''
      },
      consultants: ['Raju', 'Eric'],
      interviewId: ''
    })
    setIsCreating(false)
    setEditingId(null)
  }

  const generateId = () => {
    const id = generateInterviewId(formData.jobTitle, formData.client)
    setFormData(prev => ({ ...prev, interviewId: id }))
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Requirements Manager</h2>
        <Button onClick={() => setIsCreating(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Requirement
        </Button>
      </div>

      {isCreating && (
        <Card>
          <CardHeader>
            <CardTitle>
              {editingId ? 'Edit Requirement' : 'Create New Requirement'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Job Title *</label>
                  <Input
                    required
                    value={formData.jobTitle}
                    onChange={(e) => setFormData(prev => ({ ...prev, jobTitle: e.target.value }))}
                    placeholder="Senior Software Engineer"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Client *</label>
                  <Input
                    required
                    value={formData.client}
                    onChange={(e) => setFormData(prev => ({ ...prev, client: e.target.value }))}
                    placeholder="Client company name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Prime Vendor</label>
                  <Input
                    value={formData.primeVendor}
                    onChange={(e) => setFormData(prev => ({ ...prev, primeVendor: e.target.value }))}
                    placeholder="Prime vendor company"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Status *</label>
                  <select
                    className="w-full p-2 border rounded-md"
                    value={formData.status}
                    onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as any }))}
                  >
                    <option value="APPLIED">Applied</option>
                    <option value="NO_RESPONSE">No Response</option>
                    <option value="SUBMITTED">Submitted</option>
                    <option value="ON_HOLD">On Hold</option>
                    <option value="INTERVIEWED">Interviewed</option>
                  </select>
                </div>
              </div>

              {formData.status === 'SUBMITTED' && (
                <div>
                  <label className="block text-sm font-medium mb-2">Interview ID</label>
                  <div className="flex space-x-2">
                    <Input
                      value={formData.interviewId}
                      onChange={(e) => setFormData(prev => ({ ...prev, interviewId: e.target.value }))}
                      placeholder="Interview ID"
                    />
                    <Button type="button" onClick={generateId} variant="outline">
                      <Target className="w-4 h-4 mr-2" />
                      Generate
                    </Button>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-2">Next Steps</label>
                <Textarea
                  value={formData.nextSteps}
                  onChange={(e) => setFormData(prev => ({ ...prev, nextSteps: e.target.value }))}
                  placeholder="Add next steps for this requirement"
                  rows={3}
                />
              </div>

              <div className="flex space-x-4">
                <Button type="submit">
                  {editingId ? 'Update' : 'Create'} Requirement
                </Button>
                <Button type="button" variant="outline" onClick={resetForm}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {requirements.map((req) => (
          <Card key={req.id}>
            <CardContent className="p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-2xl">{statusEmojis[req.status]}</span>
                    <h3 className="text-lg font-semibold">{req.jobTitle}</h3>
                    <Badge className={statusColors[req.status]}>
                      {req.status.replace('_', ' ')}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Client:</span> {req.client}
                    </div>
                    {req.primeVendor && (
                      <div>
                        <span className="font-medium">Prime Vendor:</span> {req.primeVendor}
                      </div>
                    )}
                    {req.interviewId && (
                      <div>
                        <span className="font-medium">Interview ID:</span> 
                        <code className="ml-1 px-1 bg-gray-100 rounded">{req.interviewId}</code>
                      </div>
                    )}
                    <div>
                      <span className="font-medium">Consultants:</span> {req.consultants.join(', ')}
                    </div>
                  </div>

                  {req.nextSteps && (
                    <div className="mt-3">
                      <span className="font-medium text-sm">Next Steps:</span>
                      <p className="text-sm text-gray-600 mt-1">{req.nextSteps}</p>
                    </div>
                  )}

                  <div className="mt-3 text-xs text-gray-500">
                    Created: {new Date(req.createdAt).toLocaleDateString()}
                  </div>
                </div>

                <div className="flex space-x-2">
                  <Button size="sm" variant="outline" onClick={() => handleEdit(req)}>
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handleDelete(req.id)}>
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {requirements.length === 0 && !isCreating && (
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-gray-500 mb-4">No requirements found</p>
            <Button onClick={() => setIsCreating(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Requirement
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}