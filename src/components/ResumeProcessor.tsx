'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Progress } from '@/components/ui/progress'
import { Eye, Send, Download } from 'lucide-react'

interface UploadedFile {
  file: File
  id: string
}

interface ResumeProcessorProps {
  files: UploadedFile[]
}

interface ProcessingState {
  isProcessing: boolean
  progress: number
  currentFile: string
  results: Array<{
    filename: string
    success: boolean
    pointsAdded?: number
    error?: string
    downloadUrl?: string
  }>
}

export function ResumeProcessor({ files }: ResumeProcessorProps) {
  const [techStackInput, setTechStackInput] = useState('')
  const [emailConfig, setEmailConfig] = useState({
    recipient: '',
    sender: '',
    password: '',
    subject: 'Customized Resume',
    body: 'Please find the customized resume attached.'
  })
  const [processing, setProcessing] = useState<ProcessingState>({
    isProcessing: false,
    progress: 0,
    currentFile: '',
    results: []
  })

  const handlePreview = async () => {
    if (!techStackInput.trim()) {
      alert('Please enter tech stack data')
      return
    }

    // Preview functionality
    console.log('Preview requested for:', files.length, 'files')
  }

  const handleProcess = async () => {
    if (!techStackInput.trim()) {
      alert('Please enter tech stack data')
      return
    }

    setProcessing({
      isProcessing: true,
      progress: 0,
      currentFile: '',
      results: []
    })

    try {
      const results = []
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        setProcessing(prev => ({
          ...prev,
          progress: (i / files.length) * 100,
          currentFile: file.file.name
        }))

        const formData = new FormData()
        formData.append('file', file.file)
        formData.append('techStacks', techStackInput)
        formData.append('emailConfig', JSON.stringify(emailConfig))

        try {
          const response = await fetch('/api/process-resume', {
            method: 'POST',
            body: formData
          })

          const result = await response.json()
          results.push({
            filename: file.file.name,
            success: result.success,
            pointsAdded: result.pointsAdded,
            error: result.error,
            downloadUrl: result.downloadUrl
          })
        } catch (error) {
          results.push({
            filename: file.file.name,
            success: false,
            error: 'Processing failed'
          })
        }
      }

      setProcessing(prev => ({
        ...prev,
        isProcessing: false,
        progress: 100,
        currentFile: '',
        results
      }))
    } catch (error) {
      setProcessing(prev => ({
        ...prev,
        isProcessing: false,
        progress: 0,
        currentFile: '',
        results: []
      }))
    }
  }

  if (files.length === 0) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <p className="text-gray-500">Upload DOCX files to get started</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Tech Stack Input */}
      <Card>
        <CardHeader>
          <CardTitle>Tech Stack & Points</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Tech Stack Data
            </label>
            <Textarea
              placeholder="Python: • Developed web applications • Implemented APIs&#10;JavaScript: • Created UI components • Used React"
              value={techStackInput}
              onChange={(e) => setTechStackInput(e.target.value)}
              rows={8}
            />
            <p className="text-sm text-gray-500 mt-2">
              Format: TechName: • point1 • point2
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Email Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Email Configuration (Optional)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Recipient Email
              </label>
              <Input
                type="email"
                value={emailConfig.recipient}
                onChange={(e) => setEmailConfig(prev => ({ ...prev, recipient: e.target.value }))}
                placeholder="recipient@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                Sender Email
              </label>
              <Input
                type="email"
                value={emailConfig.sender}
                onChange={(e) => setEmailConfig(prev => ({ ...prev, sender: e.target.value }))}
                placeholder="your-email@gmail.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                App Password
              </label>
              <Input
                type="password"
                value={emailConfig.password}
                onChange={(e) => setEmailConfig(prev => ({ ...prev, password: e.target.value }))}
                placeholder="Your app-specific password"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                Email Subject
              </label>
              <Input
                value={emailConfig.subject}
                onChange={(e) => setEmailConfig(prev => ({ ...prev, subject: e.target.value }))}
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Email Body
            </label>
            <Textarea
              value={emailConfig.body}
              onChange={(e) => setEmailConfig(prev => ({ ...prev, body: e.target.value }))}
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex space-x-4">
        <Button onClick={handlePreview} variant="outline" disabled={processing.isProcessing}>
          <Eye className="w-4 h-4 mr-2" />
          Preview Changes
        </Button>
        <Button onClick={handleProcess} disabled={processing.isProcessing}>
          <Send className="w-4 h-4 mr-2" />
          {processing.isProcessing ? 'Processing...' : 'Process & Send'}
        </Button>
      </div>

      {/* Processing Progress */}
      {processing.isProcessing && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Processing: {processing.currentFile}</span>
                  <span>{Math.round(processing.progress)}%</span>
                </div>
                <Progress value={processing.progress} />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {processing.results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Processing Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {processing.results.map((result, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{result.filename}</p>
                    {result.success ? (
                      <p className="text-sm text-green-600">
                        ✅ Success - {result.pointsAdded} points added
                      </p>
                    ) : (
                      <p className="text-sm text-red-600">
                        ❌ Failed - {result.error}
                      </p>
                    )}
                  </div>
                  {result.success && result.downloadUrl && (
                    <Button size="sm" variant="outline">
                      <Download className="w-4 h-4 mr-2" />
                      Download
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}